"""SQLite is authoritative; checkpoints only schedule work.

Transactions serialize commits, verify observed inputs and recursively invalidate
dependent heads. Artifact bytes are content addressed and never overwritten.
The callback's return and its writes commit together, closing the
commit-before-checkpoint crash window. In-flight remote calls remain explicitly
uncertain after a process crash; this store does not promise exactly-once billing.
"""
from __future__ import annotations

import hashlib
import fcntl
import json
import os
import re
import sqlite3
import tempfile
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .models import ChangeSet, OWNERS


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Conflict(RuntimeError):
    pass


class Missing(KeyError):
    pass


class Store:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "objects").mkdir(exist_ok=True)
        (self.root / "locks").mkdir(exist_ok=True)
        self.path = self.root / "dossiers.sqlite3"
        self.lock = threading.RLock()
        self.software_manifest = {}
        with self.connect() as db:
            db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS dossiers (
              id TEXT PRIMARY KEY,title TEXT,revision INTEGER,status TEXT,
              active_run_id TEXT,created_at TEXT,updated_at TEXT,origin TEXT);
            CREATE TABLE IF NOT EXISTS artifacts (
              dossier_id TEXT,id TEXT,version INTEGER,type TEXT,owner TEXT,
              hash TEXT,input_refs TEXT,revision INTEGER,created_at TEXT,
              PRIMARY KEY(dossier_id,id,version));
            CREATE TABLE IF NOT EXISTS heads (
              dossier_id TEXT,id TEXT,version INTEGER,usable INTEGER,
              PRIMARY KEY(dossier_id,id));
            CREATE TABLE IF NOT EXISTS revisions (
              dossier_id TEXT,revision INTEGER,kind TEXT,actor TEXT,payload TEXT,created_at TEXT,
              PRIMARY KEY(dossier_id,revision));
            CREATE TABLE IF NOT EXISTS events (
              id TEXT PRIMARY KEY,dossier_id TEXT,kind TEXT,actor TEXT,revision INTEGER,
              payload TEXT,created_at TEXT);
            CREATE TABLE IF NOT EXISTS runs (
              id TEXT PRIMARY KEY,dossier_id TEXT,status TEXT,current_role TEXT,
              request TEXT,error TEXT,created_at TEXT,updated_at TEXT);
            CREATE TABLE IF NOT EXISTS tasks (
              id TEXT PRIMARY KEY,run_id TEXT,role TEXT,step_index INTEGER,status TEXT,
              read_set TEXT,saved_return TEXT,error TEXT,started_at TEXT,finished_at TEXT);
            CREATE TABLE IF NOT EXISTS attempts (
              id TEXT PRIMARY KEY,task_id TEXT,role TEXT,tool TEXT,status TEXT,
              input_hash TEXT,result TEXT,error TEXT,started_at TEXT,finished_at TEXT);
            CREATE TABLE IF NOT EXISTS api_commands (
              request_id TEXT PRIMARY KEY,kind TEXT NOT NULL,body_hash TEXT NOT NULL,
              dossier_id TEXT NOT NULL,run_id TEXT NOT NULL,created_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS artifact_dossier ON artifacts(dossier_id);
            """)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=30000")
        return db

    @contextmanager
    def transaction(self):
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise

    def _object(self, content):
        raw = canonical(content).encode()
        h = hashlib.sha256(raw).hexdigest()
        directory = self.root / "objects"
        path = directory / f"{h}.json"
        # Never expose a partly written object under its final content hash.
        # link() publishes atomically and refuses to replace an existing object.
        fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=directory)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(raw)
                f.flush()
                os.fsync(f.fileno())
            try:
                os.link(temporary, path)
            except FileExistsError:
                if path.read_bytes() != raw:
                    raise Conflict("Artefact immuable corrompu.")
            else:
                directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
        finally:
            os.unlink(temporary)
        return h

    def _load_object(self, h):
        raw = (self.root / "objects" / f"{h}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != h:
            raise Conflict("Empreinte d’artefact invalide.")
        return json.loads(raw)

    def _dossier(self, db, dossier_id):
        row = db.execute("SELECT * FROM dossiers WHERE id=?", (dossier_id,)).fetchone()
        if row is None:
            raise Missing(dossier_id)
        return dict(row)

    def _heads(self, db, dossier_id):
        return {r["id"]: dict(r) for r in db.execute("SELECT * FROM heads WHERE dossier_id=?", (dossier_id,))}

    def _event(self, db, dossier_id, revision, kind, actor, payload):
        event_id = uuid.uuid4().hex
        db.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                   (event_id, dossier_id, kind, actor, revision, canonical(payload), now()))
        return event_id

    def _revision(self, db, dossier_id, actor, kind, payload):
        revision = self._dossier(db, dossier_id)["revision"] + 1
        timestamp = now()
        db.execute("UPDATE dossiers SET revision=?,updated_at=? WHERE id=?", (revision, timestamp, dossier_id))
        db.execute("INSERT INTO revisions VALUES (?,?,?,?,?,?)",
                   (dossier_id, revision, kind, actor, canonical(payload), timestamp))
        self._event(db, dossier_id, revision, kind, actor, payload)
        return revision

    def _artifact(self, db, dossier_id, item_id, content, type_, owner, refs, revision):
        version = db.execute("SELECT COALESCE(MAX(version),0)+1 FROM artifacts WHERE dossier_id=? AND id=?",
                             (dossier_id, item_id)).fetchone()[0]
        h = self._object(content)
        db.execute("INSERT INTO artifacts VALUES (?,?,?,?,?,?,?,?,?)",
                   (dossier_id, item_id, version, type_, owner, h, canonical(refs), revision, now()))
        db.execute("INSERT INTO heads VALUES (?,?,?,1) ON CONFLICT(dossier_id,id) DO UPDATE SET version=excluded.version,usable=1",
                   (dossier_id, item_id, version))
        return f"{item_id}@{version}"

    def _invalidate(self, db, dossier_id, changed, forced=()):
        """Return exact references invalidated, without modifying artifact bytes."""
        heads = self._heads(db, dossier_id)
        invalid = {f"{i}@{heads[i]['version']}" for i in changed | set(forced) if i in heads}
        rows = db.execute("""SELECT a.* FROM artifacts a JOIN heads h
          ON a.dossier_id=h.dossier_id AND a.id=h.id AND a.version=h.version
          WHERE a.dossier_id=? AND h.usable=1""", (dossier_id,)).fetchall()
        dependencies = {}
        for row in rows:
            refs = set(json.loads(row["input_refs"]))
            # Pre-Prompt5 extractions used the request cursor as their source
            # dependency. Its historical bytes remain valid provenance after a
            # new message arrives. Preserve those existing facts without
            # rewriting their immutable artifacts; all other edges still apply.
            if row["id"].startswith("fact.") and row["owner"] == "agent0":
                content = self._load_object(row["hash"])
                source = content.get("source_ref", "")
                if (content.get("origin") in {"extracted", "assumed"}
                        and re.fullmatch(r"request@[1-9][0-9]*", source)):
                    refs.discard(source)
            dependencies[f"{row['id']}@{row['version']}"] = refs
        while True:
            more = {ref for ref, refs in dependencies.items() if refs & invalid}
            if more <= invalid:
                break
            invalid |= more
        for ref in invalid:
            db.execute("UPDATE heads SET usable=0 WHERE dossier_id=? AND id=?", (dossier_id, ref.rsplit("@", 1)[0]))
        return sorted(invalid)

    def _command(self, db, request_id, kind, body):
        """Read the durable receipt while holding the mutation transaction."""
        if request_id is None:
            return None
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 200:
            raise ValueError("request_id doit être une chaîne non vide de 200 caractères au plus.")
        row = db.execute("SELECT * FROM api_commands WHERE request_id=?", (request_id,)).fetchone()
        if row:
            if row["kind"] != kind or row["body_hash"] != digest(body):
                raise Conflict("Cette clé de requête a déjà été utilisée avec un autre contenu.")
            return row["dossier_id"], row["run_id"]
        return None

    def _remember_command(self, db, request_id, kind, body, result):
        if request_id is not None:
            db.execute("INSERT INTO api_commands VALUES (?,?,?,?,?,?)",
                       (request_id, kind, digest(body), *result, now()))

    def create(self, prompt, facts, use_ai=True, origin=None, *, request_id=None):
        body = {"prompt": prompt, "facts": facts, "use_ai": use_ai, "origin": origin}
        with self.transaction() as db:
            cached = self._command(db, request_id, "create", body)
            if cached:
                return cached
            result = self._create(db, prompt, facts, use_ai, origin)
            self._remember_command(db, request_id, "create", body, result)
            return result

    def _create(self, db, prompt, facts, use_ai=True, origin=None, inherited_facts=None):
        dossier_id, run_id = uuid.uuid4().hex, uuid.uuid4().hex
        db.execute("INSERT INTO dossiers VALUES (?,?,?,?,?,?,?,?)",
                   (dossier_id, prompt[:95], 0, "running", run_id, now(), now(), canonical(origin) if origin else None))
        rev = self._revision(db, dossier_id, "human", "request_received", {"prompt": prompt, "facts": facts})
        capture = {"prompt": prompt, "facts": facts, "kind": "initial"}
        source_ref = self._artifact(db, dossier_id, "request_source." + run_id,
                                    capture, "assertion", "human", [], rev)
        ref = self._artifact(db, dossier_id, "request", {**capture, "source_ref": source_ref},
                             "assertion", "human", [source_ref], rev)
        for field, value in facts.items():
            content = {"field": field, "value": value, "origin": "declared", "source_ref": ref,
                       "category": self.category(field)}
            inherited = (inherited_facts or {}).get(field)
            if inherited and inherited["content"].get("value") == value:
                content["origin"] = inherited["content"].get("origin", "declared")
                content["inherited_from"] = {
                    "dossier_id": inherited["dossier_id"], "artifact_ref": inherited["ref"],
                    "sha256": inherited["hash"], "origin": content["origin"],
                    "source_ref": inherited["content"].get("source_ref"),
                    "source_revision": origin.get("source_revision"),
                }
            self._artifact(db, dossier_id, "fact." + field,
                           content, "assertion", "human", [], rev)
        request = {"prompt": prompt, "facts": facts, "use_ai": use_ai, "request_ref": ref, "kind": "initial",
                   "software_manifest": self.software_manifest}
        db.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?)",
                   (run_id, dossier_id, "running", "agent0", canonical(request), None, now(), now()))
        return dossier_id, run_id

    @staticmethod
    def category(field):
        if field in {"withdrawal_cad", "withdrawal_months", "max_asset_weights", "scenario_loss_limit_cad"}:
            return "constraint"
        if field in {"objective", "horizon_years", "comparison"}:
            return "preference_or_mandate"
        if field in {"scenarios", "reserve_policy", "assumptions"}:
            return "scenario_or_assumption"
        return "input"

    def revise(self, dossier_id, message, changes, base_revision, intent="replace", *,
               request_id=None, source_revision=None):
        if intent not in {"replace", "variant"}:
            raise ValueError("Intention de révision inconnue.")
        if source_revision is not None and intent != "variant":
            raise ValueError("source_revision est réservé à une variante historique.")
        body = {"dossier_id": dossier_id, "message": message, "changes": changes,
                "base_revision": base_revision, "intent": intent}
        if source_revision is not None:
            body["source_revision"] = source_revision
        run_id = uuid.uuid4().hex
        with self.transaction() as db:
            cached = self._command(db, request_id, "revise", body)
            if cached:
                return cached
            d = self._dossier(db, dossier_id)
            if d["revision"] != base_revision:
                raise Conflict("Le dossier a évolué ; rechargez-le avant de le modifier.")
            heads = self._heads(db, dossier_id)
            if intent == "variant":
                # Capture the parent and create the child in the same transaction.
                source_revision = source_revision if source_revision is not None else base_revision
                if not db.execute("SELECT 1 FROM revisions WHERE dossier_id=? AND revision=?",
                                  (dossier_id, source_revision)).fetchone():
                    raise Missing(f"revision:{source_revision}")
                if source_revision != base_revision:
                    # Read the historical fact heads in this same transaction.
                    # The current revision remains the concurrency lease only.
                    heads = {}
                    records = db.execute("SELECT revision,payload FROM revisions WHERE dossier_id=? AND revision<=? ORDER BY revision",
                                         (dossier_id, source_revision)).fetchall()
                    for record in records:
                        invalid = set(json.loads(record["payload"]).get("invalidated", []))
                        heads = {k: h for k, h in heads.items() if f"{k}@{h['version']}" not in invalid}
                        for row in db.execute("SELECT id,version FROM artifacts WHERE dossier_id=? AND revision=?",
                                              (dossier_id, record["revision"])):
                            heads[row["id"]] = {"version": row["version"], "usable": True}
                facts = {}
                inherited_facts = {}
                for item_id, head in heads.items():
                    if item_id.startswith("fact.") and head["usable"]:
                        artifact = self._read(db, dossier_id, item_id, head["version"])
                        content = artifact["content"]
                        facts[content["field"]] = content["value"]
                        inherited_facts[content["field"]] = artifact
                facts.update(changes)
                old_run = db.execute("SELECT request FROM runs WHERE id=?", (d["active_run_id"],)).fetchone()
                use_ai = json.loads(old_run[0]).get("use_ai", True) if old_run else True
                result = self._create(db, message, facts, use_ai,
                                      {"dossier_id": dossier_id, "revision": base_revision,
                                       "source_revision": source_revision, "intent": "variant"},
                                      inherited_facts=inherited_facts)
                self._remember_command(db, request_id, "revise", body, result)
                return result
            old_analysis = self._read_head(db, dossier_id, "analysis")
            changed = set()
            for field, value in changes.items():
                previous = self._read_head(db, dossier_id, "fact." + field)
                if previous is None or previous["content"]["value"] != value:
                    changed.add("fact." + field)
            # Unknown content in a free-text correction may affect any field:
            # suppress active conclusions now, before a model interprets it.
            invalid = self._invalidate(db, dossier_id, changed, {"request", "problem", "analysis", "view", "questions"})
            reuse = [f"{k}@{v['version']}" for k, v in self._heads(db, dossier_id).items() if v["usable"]]
            rev = self._revision(db, dossier_id, "human", "revision_requested",
                                 {"message": message, "changes": changes, "intent": intent,
                                  "changed_fields": sorted(changed), "invalidated": invalid,
                                  "reused": reuse, "before": old_analysis["content"] if old_analysis else None})
            capture = {"prompt": message, "facts": changes, "kind": "correction"}
            source_ref = self._artifact(db, dossier_id, "request_source." + run_id,
                                        capture, "assertion", "human", [], rev)
            ref = self._artifact(db, dossier_id, "request", {**capture, "source_ref": source_ref},
                                 "assertion", "human", [source_ref], rev)
            for field, value in changes.items():
                if "fact." + field in changed:
                    self._artifact(db, dossier_id, "fact." + field,
                                   {"field": field, "value": value, "origin": "declared", "source_ref": ref,
                                    "category": self.category(field)}, "assertion", "human", [], rev)
            old_run = db.execute("SELECT request FROM runs WHERE id=?", (d["active_run_id"],)).fetchone()
            use_ai = json.loads(old_run[0]).get("use_ai", True) if old_run else True
            db.execute("UPDATE runs SET status='superseded',updated_at=? WHERE dossier_id=? AND status IN ('running','waiting','error')", (now(), dossier_id))
            request = {"prompt": message, "facts": changes, "use_ai": use_ai, "request_ref": ref, "kind": "correction",
                       "software_manifest": self.software_manifest}
            db.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?)",
                       (run_id, dossier_id, "running", "agent0", canonical(request), None, now(), now()))
            db.execute("UPDATE dossiers SET active_run_id=?,status='running' WHERE id=?", (run_id, dossier_id))
            self._remember_command(db, request_id, "revise", body, (dossier_id, run_id))
        return dossier_id, run_id

    def artifact(self, dossier_id, ref):
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+@[1-9][0-9]*", ref):
            raise Missing(ref)
        item_id, version = ref.rsplit("@", 1)
        with self.connect() as db:
            return self._read(db, dossier_id, item_id, int(version))

    def _read(self, db, dossier_id, item_id, version):
        row = db.execute("SELECT * FROM artifacts WHERE dossier_id=? AND id=? AND version=?",
                         (dossier_id, item_id, version)).fetchone()
        if row is None:
            raise Missing(f"{item_id}@{version}")
        result = dict(row)
        result["content"] = self._load_object(result["hash"])
        result["input_refs"] = json.loads(result["input_refs"])
        result["ref"] = f"{item_id}@{version}"
        head = db.execute("SELECT version,usable FROM heads WHERE dossier_id=? AND id=?", (dossier_id, item_id)).fetchone()
        result["usable"] = bool(head and head["version"] == version and head["usable"])
        return result

    def _read_head(self, db, dossier_id, item_id, usable_only=True):
        head = db.execute("SELECT * FROM heads WHERE dossier_id=? AND id=?", (dossier_id, item_id)).fetchone()
        if not head or (usable_only and not head["usable"]):
            return None
        return self._read(db, dossier_id, item_id, head["version"])

    def context(self, run_id):
        with self.connect() as db:
            run = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if not run:
                raise Missing(run_id)
            run = dict(run)
            run["request"] = json.loads(run["request"])
            dossier = self._dossier(db, run["dossier_id"])
            if dossier["active_run_id"] != run_id or run["status"] == "superseded":
                raise Conflict("Cette exécution est remplacée par une révision plus récente.")
            artifacts = [self._read(db, run["dossier_id"], k, v["version"])
                         for k, v in self._heads(db, run["dossier_id"]).items() if v["usable"]]
            return run, dossier, {a["id"]: a for a in artifacts}

    def begin_task(self, run_id, role, step_index, read_set):
        task_id = f"{run_id}:{step_index}"
        with self.transaction() as db:
            existing = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if existing and existing["status"] == "complete":
                return task_id, json.loads(existing["saved_return"])
            run = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if not run or run["status"] == "superseded" or self._dossier(db, run["dossier_id"])["active_run_id"] != run_id:
                raise Conflict("Une exécution remplacée ne peut pas ouvrir de nouvelle tâche.")
            if existing and (existing["role"] != role or json.loads(existing["read_set"]) != read_set):
                raise Conflict("La reprise ne correspond plus au rôle et aux entrées observées.")
            if existing:
                db.execute("UPDATE tasks SET status='running',error=NULL WHERE id=?", (task_id,))
            else:
                db.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?)",
                           (task_id, run_id, role, step_index, "running", canonical(read_set), None, None, now(), None))
            db.execute("UPDATE runs SET current_role=?,status='running',error=NULL,updated_at=? WHERE id=?", (role, now(), run_id))
        return task_id, None

    def committed_task(self, task_id):
        with self.connect() as db:
            task = db.execute("SELECT saved_return FROM tasks WHERE id=? AND status='complete'", (task_id,)).fetchone()
            return json.loads(task[0]) if task else None

    def commit(self, change: ChangeSet):
        with self.transaction() as db:
            task = db.execute("SELECT * FROM tasks WHERE id=?", (change.task_id,)).fetchone()
            if not task or task["run_id"] != change.run_id or task["role"] != change.role:
                raise Conflict("Tâche ou autorisation d’écriture invalide.")
            if task["status"] == "complete":
                return json.loads(task["saved_return"])
            observed = json.loads(task["read_set"])
            if observed != change.read_set:
                raise Conflict("Le read_set doit correspondre aux entrées transmises par le noyau.")
            run = db.execute("SELECT * FROM runs WHERE id=?", (change.run_id,)).fetchone()
            dossier_id = run["dossier_id"]
            d = self._dossier(db, dossier_id)
            if d["active_run_id"] != change.run_id:
                raise Conflict("Résultat tardif conservé dans les traces, sans remplacer la révision active.")
            for ref in observed:
                item_id, version = ref.rsplit("@", 1)
                current = self._read_head(db, dossier_id, item_id)
                if not current or current["version"] != int(version):
                    raise Conflict(f"Entrée devenue obsolète : {ref}")
            changed = set()
            available_outputs = set()
            logical_contracts = {
                "problem": ("agent0", "problem"), "qualification": ("agent0", "assertion"),
                "research": ("agent1", "research"), "research_review": ("agent1", "review"),
                "research_plan": ("agent1", "review"),
                "data_inspection": ("agent1", "research"),
                "baseline_stress": ("agent2", "analysis"),
                "analysis": ("agent2", "analysis"), "analysis_review": ("agent2", "review"),
                "view": ("agent3", "view"),
            }
            for w in change.writes:
                if w.type not in OWNERS[change.role]:
                    raise Conflict(f"{change.role} ne peut pas écrire {w.type}.")
                contract = logical_contracts.get(w.id)
                if w.id.startswith("fact."):
                    contract = ("agent0", "assertion")
                if w.id.startswith("questions."):
                    contract = (w.id.split(".", 1)[1], "questions")
                if w.id.startswith("research."):
                    contract = ("agent1", "research")
                if contract != (change.role, w.type):
                    raise Conflict("Identifiant, type et propriétaire incompatibles avec le contrat.")
                ordinary = {r for r in w.input_refs if not r.startswith("$")}
                produced = {r[1:] for r in w.input_refs if r.startswith("$")}
                if not ordinary <= set(observed) or not produced <= available_outputs:
                    raise Conflict("Une dépendance n’a pas été lue dans cette étape.")
                # Prevent one role overwriting another role's logical artifact.
                previous = self._read_head(db, dossier_id, w.id, False)
                if previous and previous["owner"] not in {change.role, "human"}:
                    raise Conflict("Le propriétaire de cette pièce est un autre agent.")
                if w.id in {"request"} or (w.id.startswith("fact.") and change.role != "agent0"):
                    raise Conflict("Écriture de déclaration interdite pour ce rôle.")
                changed.add(w.id)
                if w.id in available_outputs:
                    raise Conflict("Une pièce ne peut être écrite deux fois dans une transaction.")
                available_outputs.add(w.id)
            invalid = self._invalidate(db, dossier_id, changed)
            if any(set(w.input_refs) & set(invalid) for w in change.writes):
                raise Conflict("Une sortie dépendrait d’une entrée invalidée dans la même transaction.")
            rev = self._revision(db, dossier_id, change.role, "agent_commit",
                                 {"run_id": change.run_id, "task_id": change.task_id,
                                  "read_set": observed, "writes": sorted(changed),
                                  "invalidated": invalid, "reason": change.reason})
            outputs = {}
            for w in change.writes:
                deps = [outputs[r[1:]] if r.startswith("$") else r for r in w.input_refs]
                def resolve(value):
                    if isinstance(value, str) and value.startswith("$") and value[1:] in outputs:
                        return outputs[value[1:]]
                    if isinstance(value, list):
                        return [resolve(x) for x in value]
                    if isinstance(value, dict):
                        return {k: resolve(v) for k, v in value.items()}
                    return value
                outputs[w.id] = self._artifact(db, dossier_id, w.id, resolve(w.content), w.type, change.role, deps, rev)
            refs = list(outputs.values())
            saved = {"run_id": change.run_id, "dossier_id": dossier_id, "step_index": task["step_index"] + 1,
                     "status": change.status, "next_role": change.next_role, "output_refs": refs, "revision": rev}
            db.execute("UPDATE tasks SET status='complete',saved_return=?,finished_at=?,error=NULL WHERE id=?",
                       (canonical(saved), now(), change.task_id))
            db.execute("UPDATE runs SET status=?,current_role=?,updated_at=?,error=NULL WHERE id=?",
                       (change.status, change.next_role, now(), change.run_id))
            db.execute("UPDATE dossiers SET status=? WHERE id=?", (change.status, dossier_id))
            return saved

    def operation(self, task_id, role, tool, inputs, execute):
        """Persist tool/model receipts. Successful results are reused on retry."""
        lock_path = self.root / "locks" / (digest([task_id, tool, inputs]) + ".lock")
        with lock_path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            return self._operation_locked(task_id, role, tool, inputs, execute)

    def _operation_locked(self, task_id, role, tool, inputs, execute):
        h = digest(inputs)
        self._object(inputs)  # Exact prompt/tool arguments, inspectable and immutable.
        with self.transaction() as db:
            cached = db.execute("SELECT result FROM attempts WHERE task_id=? AND tool=? AND input_hash=? AND status='complete' ORDER BY started_at LIMIT 1", (task_id, tool, h)).fetchone()
            if cached:
                return json.loads(cached[0])
            db.execute("UPDATE attempts SET status='outcome_unknown',error=? WHERE task_id=? AND tool=? AND status='running'",
                       (canonical({"message": "Interruption après émission possible ; une nouvelle tentative peut être facturée."}), task_id, tool))
            attempt_id = uuid.uuid4().hex
            db.execute("INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (attempt_id, task_id, role, tool, "running", h, None, None, now(), None))
        try:
            result = execute()
            raw = canonical(result)
        except BaseException as exc:
            error = exc.as_dict() if hasattr(exc, "as_dict") else {"code": type(exc).__name__, "message": str(exc)[:1500]}
            with self.transaction() as db:
                db.execute("UPDATE attempts SET status='error',error=?,finished_at=? WHERE id=?",
                           (canonical(error), now(), attempt_id))
            raise
        with self.transaction() as db:
            db.execute("UPDATE attempts SET status='complete',result=?,finished_at=? WHERE id=?", (raw, now(), attempt_id))
        return result

    def fail(self, run_id, error):
        value = error.as_dict() if hasattr(error, "as_dict") else {"code": type(error).__name__, "message": str(error)[:1500]}
        with self.transaction() as db:
            run = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if not run:
                return
            db.execute("UPDATE tasks SET status='error',error=?,finished_at=? WHERE run_id=? AND status='running'", (canonical(value), now(), run_id))
            if self._dossier(db, run["dossier_id"])["active_run_id"] == run_id:
                db.execute("UPDATE runs SET status='error',error=?,updated_at=? WHERE id=?", (canonical(value), now(), run_id))
                db.execute("UPDATE dossiers SET status='error' WHERE id=?", (run["dossier_id"],))
                self._event(db, run["dossier_id"], self._dossier(db, run["dossier_id"])["revision"],
                            "execution_error", "kernel", {"run_id": run_id, "error": value})

    def record_display(self, dossier_id, view_ref):
        with self.transaction() as db:
            d = self._dossier(db, dossier_id)
            view = self._read_head(db, dossier_id, "view")
            if not view or view["ref"] != view_ref:
                raise Conflict("Cette vue n’est plus courante.")
            # Display doesn't modify the financial revision and never implies acceptance.
            return self._event(db, dossier_id, d["revision"], "view_displayed", "browser", {"view_ref": view_ref, "accepted": False})

    def list(self):
        with self.connect() as db:
            rows = [dict(r) for r in db.execute("SELECT id,title,revision,status,created_at,updated_at,origin FROM dossiers ORDER BY created_at DESC LIMIT 100")]
            for row in rows:
                row["origin"] = json.loads(row["origin"]) if row["origin"] else None
            return rows

    def snapshot(self, dossier_id):
        with self.connect() as db:
            db.execute("BEGIN")
            d = self._dossier(db, dossier_id)
            artifacts = [self._read(db, dossier_id, r["id"], r["version"]) for r in
                         db.execute("SELECT id,version FROM artifacts WHERE dossier_id=? ORDER BY revision,id", (dossier_id,))]
            heads = {a["id"]: a for a in artifacts if a["usable"]}
            revisions = [dict(r) for r in db.execute("SELECT * FROM revisions WHERE dossier_id=? ORDER BY revision", (dossier_id,))]
            events = [dict(r) for r in db.execute("SELECT * FROM events WHERE dossier_id=? ORDER BY created_at", (dossier_id,))]
            for row in revisions + events:
                row["payload"] = json.loads(row["payload"])
            runs = [dict(r) for r in db.execute("SELECT * FROM runs WHERE dossier_id=? ORDER BY created_at", (dossier_id,))]
            tasks = [dict(r) for r in db.execute("SELECT t.* FROM tasks t JOIN runs r ON t.run_id=r.id WHERE r.dossier_id=? ORDER BY t.started_at", (dossier_id,))]
            attempts = [dict(r) for r in db.execute("""SELECT a.* FROM attempts a JOIN tasks t ON t.id=a.task_id
              JOIN runs r ON r.id=t.run_id WHERE r.dossier_id=? ORDER BY a.started_at""", (dossier_id,))]
            for row in runs:
                row["request"] = json.loads(row["request"])
                row["error"] = json.loads(row["error"]) if row["error"] else None
            for row in tasks:
                row["read_set"] = json.loads(row["read_set"])
                saved = json.loads(row.pop("saved_return")) if row["saved_return"] else {}
                row["output_refs"] = saved.get("output_refs", [])
                row["committed_revision"] = saved.get("revision")
                row["result_status"] = saved.get("status")
                row["next_role"] = saved.get("next_role")
                row["reused_refs"] = row["read_set"]
                row["error"] = json.loads(row["error"]) if row["error"] else None
            for row in attempts:
                result = json.loads(row.pop("result")) if row["result"] else {}
                row["detail"] = result
                for key in ("request_id", "usage", "latency_ms", "model", "provider", "region", "account_id"):
                    if key in result:
                        row[key] = result[key]
                row["error"] = json.loads(row["error"]) if row["error"] else None
            evidence = {canonical(e): e for a in heads.values() if a["type"] == "research"
                        for e in a["content"].get("evidence", [])}
            latest_revision = next((r for r in reversed(revisions) if r["kind"] == "revision_requested"), None)
            comparison = None
            if latest_revision:
                p = latest_revision["payload"]
                comparison = {k: p.get(k) for k in ("before", "changed_fields", "invalidated", "reused")}
                comparison["after"] = heads.get("analysis", {}).get("content")
                # Free-text corrections are interpreted after the intake
                # transaction. Preserve that event, but project the actual
                # current usability rather than its provisional reuse list.
                before_refs = set(p.get("invalidated", [])) | set(p.get("reused", []))
                usable_refs = {a["ref"] for a in artifacts if a["usable"]}
                comparison["reused"] = sorted(before_refs & usable_refs)
                comparison["invalidated"] = sorted(before_refs - usable_refs)
                old_inputs = (p.get("before") or {}).get("inputs", {})
                current_problem = heads.get("problem", {}).get("content")
                if current_problem:
                    interpreted = {"fact." + k for k, value in current_problem.items()
                                   if k in old_inputs and old_inputs[k] != value}
                    comparison["changed_fields"] = sorted(set(p.get("changed_fields", [])) | interpreted)
                comparison["provisional"] = current_problem is None
            d.update(active_problem=heads.get("problem", {}).get("content"),
                     current_analysis=heads.get("analysis"), current_view=heads.get("view"),
                     pending_clarifications={
                         "qualification_ref": heads.get("qualification", {}).get("ref"),
                         "questions": heads.get("qualification", {}).get("content", {}).get("clarifications", []),
                     },
                     artifacts=artifacts, questions=[n for key, a in heads.items() if key.startswith("questions.")
                                                     for n in a.get("content", {}).get("nodes", [])],
                     evidence=list(evidence.values()), events=events, revisions=revisions,
                     runs=runs, tasks=tasks, attempts=attempts, comparison=comparison,
                     route={"provider": "amazon-bedrock-runtime", "model": "global.openai.gpt-6-astra",
                            "entry_region": "us-east-1", "residency": "global; aucune résidence canadienne revendiquée",
                            "verified_requests": [a["request_id"] for a in attempts if a.get("request_id")]},
                     limitations=["Conseil simulé sur données et hypothèses explicites.",
                                  "Une reprise réutilise les résultats enregistrés ; un appel AWS interrompu avant réception peut nécessiter une nouvelle tentative facturée."])
            return d
