"""Application web locale : poser une demande, modifier une hypothèse, recalculer, lire le dossier.

Lancement : `uv run python -m datathon2026.app` (ou `bash scripts/lancer-app.sh`), puis
http://127.0.0.1:8765. Le serveur n'écoute que sur la machine locale. Bibliothèque standard seule.

Deux modes, toujours étiquetés dans le dossier :
- « Calcul de référence » : workflow fixe, sans appel de modèle, instantané ;
- « Agent sur Amazon Bedrock » : l'agent choisit les outils et rédige ; chaque appel porte son RequestId.

Ce module n'appelle que `workflow.WORKFLOWS`, `BedrockAgent.run` et `report.render`.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import data, report, workflow
from . import tools as T

PERSONAS = ("robert", "amira", "mateo")
_LOCK = threading.Lock()  # un calcul à la fois : le marché est chargé une fois par exécution


def _float(v, lo: float, hi: float, name: str) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        raise ValueError(f"{name} : nombre attendu") from None
    if not lo <= x <= hi:
        raise ValueError(f"{name} : valeur attendue entre {lo:g} et {hi:g}")
    return x


def build_scenario(persona: str, hyp: dict, request: str | None) -> tuple[dict, list[str]]:
    """Scénario de démonstration modifié par les hypothèses saisies. Renvoie aussi la liste des
    hypothèses changées par rapport au fichier de configuration (affichée à l'utilisateur)."""
    scenarios = T.load_scenarios()
    base = scenarios.get(persona)
    if base is None:
        return {"persona": persona, "demande": request or "", "origine_demande": "demande libre saisie dans l'outil"}, []
    sc, changed = dict(base), []
    tickers = set(data.load_universe()["ticker"])

    def put(key: str, value, label: str):
        if key in sc and sc[key] != value:
            changed.append(label)
        sc[key] = value

    if persona == "robert":
        if "part" in hyp:
            part = round(_float(hyp["part"], 1, 30, "part étudiée (%)") / 100, 4)
            put("part_declaree", part, "part étudiée")
            sc["parts_etudiees"] = sorted({round(part / 2, 4), part, round(min(part * 2, 0.5), 4)})
        if "seuil" in hyp:
            put("seuil_perte", -round(_float(hyp["seuil"], 1, 60, "seuil de perte (%)") / 100, 4), "seuil de perte")
        if "horizon" in hyp:
            put("horizon_etude_ans", _float(hyp["horizon"], 1, 4, "horizon étudié (ans)"), "horizon étudié")
        for key, label in (("actif", "actif étudié"), ("alternative", "alternative comparée")):
            if hyp.get(key):
                if hyp[key] not in tickers:
                    raise ValueError(f"{label} : symbole inconnu du jeu de données")
                put("actif_demande" if key == "actif" else "alternative", hyp[key], label)
        if sc["actif_demande"] in sc["portefeuille_actuel"] or sc["alternative"] in sc["portefeuille_actuel"]:
            raise ValueError("l'actif étudié et l'alternative doivent être absents du portefeuille de départ")
        if sc["actif_demande"] == sc["alternative"]:
            raise ValueError("l'actif étudié et l'alternative doivent être différents")
    if persona == "amira" and "plafond" in hyp:
        put("plafond_risque_groupe", round(_float(hyp["plafond"], 20, 90, "plafond de risque par groupe (%)") / 100, 4),
            "plafond de risque par groupe")
    if request and request.strip() and request.strip() != base["demande"]:
        sc["demande"] = request.strip()
        changed.append("demande")
    return sc, changed


def produce(payload: dict) -> dict:
    persona = payload.get("profil")
    if persona not in PERSONAS:
        raise ValueError("profil inconnu")
    mode = payload.get("mode", "reference")
    scenario, changed = build_scenario(persona, payload.get("hypotheses") or {}, payload.get("demande"))
    t0 = time.perf_counter()
    with _LOCK:
        if mode == "agent":
            from .agent import BedrockAgent

            if not scenario.get("demande"):
                raise ValueError("saisissez une demande pour l'agent")
            free = "demande" in changed or persona not in workflow.WORKFLOWS
            if free:  # demande libre : l'agent ne reçoit que les hypothèses que l'utilisateur a touchées
                kept = {"persona", "demande", "origine_demande"}
                scenario = {k: v for k, v in scenario.items() if k in kept} | {"origine_demande": "demande libre saisie dans l'outil"}
            dossier = BedrockAgent().run(f"{persona}-{'libre' if free else 'agent'}", scenario)
        else:
            if persona not in workflow.WORKFLOWS:
                raise ValueError("aucun calcul de référence pour ce profil : utilisez l'agent sur Amazon Bedrock")
            if "demande" in changed:
                raise ValueError("le calcul de référence traite la demande du scénario ; pour une demande libre, utilisez l'agent")
            dossier = workflow.WORKFLOWS[persona](scenario)
    d = dossier.to_dict()
    v = d["verification"]
    return {
        "html": report.render(d),
        "titre": d.get("titre") or d["scenario"],
        "mode": d["mode"],
        "resume": d["resume"]["texte"],
        "controle": {"ok": v["ok"], "valeurs": v["valeurs_reliees"], "affirmations": v["affirmations"]},
        "appels_aws": len((d.get("aws") or {}).get("appels", [])),
        "hypotheses_modifiees": [c for c in changed if c != "demande"],
        "duree_s": round(time.perf_counter() - t0, 1),
    }


def bootstrap() -> dict:
    """Valeurs initiales de l'interface, lues dans la configuration (aucun chiffre en dur dans la page)."""
    sc = T.load_scenarios()
    uni = data.load_universe()
    personas = data.load_personas()
    r, am = sc["robert"], sc["amira"]
    held = set(r["portefeuille_actuel"])
    return {
        "profils": {
            k: {"nom": personas[k]["nom"], "risque": personas[k]["profil_risque"], "objectif": personas[k]["objectif"],
                "demande": sc.get(k, {}).get("demande", ""), "reference": k in workflow.WORKFLOWS}
            for k in PERSONAS
        },
        "actifs": [{"t": t, "n": n} for t, n in zip(uni["ticker"], uni["name"]) if t not in held],
        "robert": {"part": r["part_declaree"] * 100, "seuil": -r["seuil_perte"] * 100, "horizon": r["horizon_etude_ans"],
                   "actif": r["actif_demande"], "alternative": r["alternative"]},
        "amira": {"plafond": am["plafond_risque_groupe"] * 100},
    }


PAGE = r"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AlphaForge — laboratoire de décision</title>
<style>
:root{color-scheme:light;--paper:#fff;--ink:#111;--ink-2:#3d3d3d;--ink-3:#6b6b6b;--rule:#111;--hair:#d9d9d9;--tint:#f4f4f2;--accent:#1d4f91;--bad:#b3261e}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--paper:#141414;--ink:#ececea;--ink-2:#c9c9c6;--ink-3:#9a9a96;--rule:#ececea;--hair:#3a3a38;--tint:#1c1c1b;--accent:#7fa9e3;--bad:#f28b82}}
*{box-sizing:border-box}html,body{height:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;display:grid;grid-template-columns:360px 1fr}
aside{border-right:1px solid var(--hair);padding:18px 20px 28px;overflow-y:auto;height:100vh}
h1{font:600 22px/1.2 "Iowan Old Style",Palatino,Georgia,serif;margin:0 0 2px}
.tag{font-size:12px;color:var(--ink-3);margin:0 0 16px}
h2{font-size:12px;font-weight:600;color:var(--ink-3);margin:20px 0 6px;border-top:1px solid var(--hair);padding-top:12px}
.seg{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;border:1px solid var(--rule)}
.seg button{font:inherit;border:0;background:none;color:var(--ink-2);padding:7px 4px;cursor:pointer}
.seg button+button{border-left:1px solid var(--hair)}
.seg button[aria-pressed=true]{background:var(--ink);color:var(--paper)}
.who{font-size:13px;color:var(--ink-2);margin:8px 0 0}
textarea,select,input[type=number]{font:inherit;width:100%;border:1px solid var(--hair);background:var(--paper);color:var(--ink);padding:7px 8px}
textarea{min-height:76px;resize:vertical}
label{display:block;font-size:13px;color:var(--ink-2);margin:10px 0 3px}
.row{display:grid;grid-template-columns:1fr 84px;gap:10px;align-items:center}
input[type=range]{width:100%;accent-color:var(--accent)}
.hyp{font-style:italic}
.go{font:inherit;font-weight:600;width:100%;margin-top:18px;padding:10px;border:1px solid var(--rule);background:var(--ink);color:var(--paper);cursor:pointer}
.go[disabled]{opacity:.5;cursor:progress}
.note{font-size:12px;color:var(--ink-3);margin:6px 0 0}
.err{color:var(--bad);font-size:13px;margin:10px 0 0;min-height:1.2em}
ol.hist{list-style:none;margin:0;padding:0;font-size:13px}
ol.hist li{border-bottom:1px solid var(--hair)}
ol.hist button{font:inherit;text-align:left;width:100%;border:0;background:none;color:var(--ink);padding:7px 0;cursor:pointer}
ol.hist button[aria-current=true]{color:var(--accent);font-weight:600}
ol.hist small{display:block;color:var(--ink-3)}
main{height:100vh;display:grid;grid-template-rows:auto 1fr}
.bar{border-bottom:1px solid var(--hair);padding:8px 16px;font-size:13px;color:var(--ink-2);display:flex;gap:16px;flex-wrap:wrap;min-height:38px}
.bar b{color:var(--ink)}.bar .ko{color:var(--bad);font-weight:600}
iframe{border:0;width:100%;height:100%;background:var(--paper)}
.empty{padding:60px 40px;color:var(--ink-3);max-width:60ch}
[hidden]{display:none!important}
@media (max-width:820px){body{grid-template-columns:1fr}aside{height:auto;border-right:0;border-bottom:1px solid var(--hair)}main{height:90vh}}
</style></head><body>
<aside>
<h1>AlphaForge</h1>
<p class="tag">Laboratoire de décision d'investissement · simulation sur profils fictifs, aucun conseil personnalisé</p>

<h2>Profil fictif</h2>
<div class="seg" id="profils"></div>
<p class="who" id="who"></p>

<h2>Demande</h2>
<textarea id="demande" aria-label="Demande de la personne"></textarea>
<p class="note" id="demande-note"></p>

<h2>Hypothèses modifiables</h2>
<div id="hyp-robert">
  <label for="actif">Actif étudié</label><select id="actif"></select>
  <label for="part" class="hyp">Part du portefeuille consacrée à cet actif (%)</label>
  <div class="row"><input type="range" id="part-r" min="1" max="30" step="1"><input type="number" id="part" min="1" max="30" step="1"></div>
  <label for="seuil" class="hyp">Baisse maximale supportable du portefeuille (%)</label>
  <div class="row"><input type="range" id="seuil-r" min="5" max="40" step="1"><input type="number" id="seuil" min="1" max="60" step="1"></div>
  <label for="horizon" class="hyp">Horizon étudié (ans)</label>
  <div class="row"><input type="range" id="horizon-r" min="1" max="4" step="1"><input type="number" id="horizon" min="1" max="4" step="1"></div>
  <label for="alternative">Alternative comparée, à part égale</label><select id="alternative"></select>
</div>
<div id="hyp-amira" hidden>
  <label for="plafond" class="hyp">Part maximale du risque portée par un groupe d'actifs (%)</label>
  <div class="row"><input type="range" id="plafond-r" min="20" max="90" step="5"><input type="number" id="plafond" min="20" max="90" step="5"></div>
</div>
<p class="note" id="hyp-none" hidden>Aucune hypothèse de démonstration pour ce profil : l'agent travaille à partir de la demande et signale ce qui manque.</p>

<h2>Traitement</h2>
<div class="seg" id="modes">
  <button data-mode="reference" aria-pressed="true">Calcul de référence</button>
  <button data-mode="agent" aria-pressed="false">Agent sur Amazon Bedrock</button>
</div>
<p class="note" id="mode-note"></p>
<button class="go" id="go">Produire le dossier</button>
<p class="err" id="err" role="alert"></p>

<h2>Dossiers produits dans cette séance</h2>
<ol class="hist" id="hist"></ol>
<p class="note">Cliquez sur un dossier pour y revenir, avec ses hypothèses.</p>
</aside>
<main>
<div class="bar" id="bar"></div>
<div class="empty" id="empty">Choisissez un profil, ajustez une hypothèse, puis produisez le dossier. Chaque valeur du dossier est reliée au calcul qui la produit : survolez-la pour voir sa source.</div>
<iframe id="doc" title="Dossier de décision" hidden></iframe>
</main>
<script>
const B = __BOOT__;
const $ = id => document.getElementById(id);
let profil = 'robert', mode = 'reference', runs = [], current = -1;
const FIELDS = {robert: ['part', 'seuil', 'horizon'], amira: ['plafond']};

function seg(el, items, get, set) {
  el.innerHTML = '';
  for (const [k, label] of items) {
    const b = document.createElement('button'); b.textContent = label; b.setAttribute('aria-pressed', k === get());
    b.onclick = () => { set(k); [...el.children].forEach(c => c.setAttribute('aria-pressed', c === b)); refresh(); };
    el.appendChild(b);
  }
}
function link(id) {
  const n = $(id), r = $(id + '-r');
  r.oninput = () => { n.value = r.value; }; n.oninput = () => { r.value = n.value; };
}
function setFields(values) { for (const [k, v] of Object.entries(values)) { const n = $(k); if (!n) continue; n.value = v; const r = $(k + '-r'); if (r) r.value = v; } }
function refresh() {
  const p = B.profils[profil];
  $('who').textContent = p.nom + ' — profil de risque ' + p.risque + '. Objectif : ' + p.objectif + '.';
  $('hyp-robert').hidden = profil !== 'robert'; $('hyp-amira').hidden = profil !== 'amira'; $('hyp-none').hidden = profil !== 'mateo';
  if (!p.reference && mode === 'reference') { mode = 'agent'; [...$('modes').children].forEach(c => c.setAttribute('aria-pressed', c.dataset.mode === 'agent')); }
  $('modes').children[0].disabled = !p.reference;
  $('mode-note').textContent = mode === 'agent'
    ? "L'agent choisit lui-même les outils de calcul et rédige le dossier. Appels facturés sur le compte AWS ; comptez environ une minute."
    : 'Enchaînement fixe des mêmes outils de calcul, sans modèle de langage. Réponse immédiate.';
  $('demande-note').textContent = mode === 'agent' ? 'Demande libre : écrivez ce que la personne veut étudier.' : "Le calcul de référence traite la demande du scénario ; pour une demande libre, passez à l'agent.";
  $('demande').readOnly = mode !== 'agent';
}
function setProfil(k) { profil = k; $('demande').value = B.profils[k].demande; if (B[k]) setFields(B[k]); }
function payload() {
  const h = {};
  for (const k of FIELDS[profil] || []) h[k] = $(k).value;
  if (profil === 'robert') { h.actif = $('actif').value; h.alternative = $('alternative').value; }
  return {profil, mode, demande: $('demande').value, hypotheses: h};
}
function show(i) {
  current = i; const r = runs[i];
  $('empty').hidden = true; $('doc').hidden = false; $('doc').srcdoc = r.out.html;
  const c = r.out.controle;
  $('bar').innerHTML = '';
  const add = (t, cls) => { const s = document.createElement('span'); s.textContent = t; if (cls) s.className = cls; $('bar').appendChild(s); };
  add(r.out.mode); add(c.ok ? 'Contrôle conforme : ' + c.valeurs + ' valeurs reliées au registre' : 'Contrôle en échec', c.ok ? '' : 'ko');
  if (r.out.appels_aws) add(r.out.appels_aws + ' appels Amazon Bedrock');
  if (r.out.hypotheses_modifiees.length) add('Hypothèses modifiées : ' + r.out.hypotheses_modifiees.join(', '));
  add(r.out.duree_s.toString().replace('.', ',') + ' s');
  [...$('hist').children].forEach((li, j) => li.firstChild.setAttribute('aria-current', j === runs.length - 1 - i));
}
function restore(i) {
  const q = runs[i].req; profil = q.profil; mode = q.mode;
  [...$('profils').children].forEach((c, j) => c.setAttribute('aria-pressed', Object.keys(B.profils)[j] === profil));
  [...$('modes').children].forEach(c => c.setAttribute('aria-pressed', c.dataset.mode === mode));
  $('demande').value = q.demande; setFields(q.hypotheses); refresh(); show(i);
}
function history() {
  $('hist').innerHTML = '';
  runs.map((r, i) => i).reverse().forEach(i => {
    const r = runs[i], li = document.createElement('li'), b = document.createElement('button'), s = document.createElement('small');
    b.textContent = r.out.titre; s.textContent = r.out.mode + (r.out.hypotheses_modifiees.length ? ' · ' + r.out.hypotheses_modifiees.join(', ') : '');
    b.appendChild(s); b.onclick = () => restore(i); li.appendChild(b); $('hist').appendChild(li);
  });
}
async function go() {
  const req = payload(); $('err').textContent = ''; $('go').disabled = true;
  $('go').textContent = mode === 'agent' ? "L'agent travaille sur Amazon Bedrock…" : 'Calcul en cours…';
  try {
    const res = await fetch('/api/dossier', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(req)});
    const out = await res.json();
    if (!res.ok) throw new Error(out.erreur || 'Erreur');
    runs.push({req, out}); history(); show(runs.length - 1);
  } catch (e) { $('err').textContent = e.message; }
  $('go').disabled = false; $('go').textContent = 'Produire le dossier';
}
for (const id of ['actif', 'alternative']) for (const a of B.actifs) { const o = document.createElement('option'); o.value = a.t; o.textContent = a.t + ' — ' + a.n; $(id).appendChild(o); }
['part', 'seuil', 'horizon', 'plafond'].forEach(link);
seg($('profils'), Object.entries(B.profils).map(([k, p]) => [k, p.nom]), () => profil, setProfil);
[...$('modes').children].forEach(b => b.onclick = () => { if (b.disabled) return; mode = b.dataset.mode; [...$('modes').children].forEach(c => c.setAttribute('aria-pressed', c === b)); refresh(); });
$('go').onclick = go;
setProfil('robert'); refresh(); go();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            page = PAGE.replace("__BOOT__", json.dumps(bootstrap(), ensure_ascii=False).replace("</", "<\\/"))
            self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
        else:
            self._send(404, b"introuvable", "text/plain; charset=utf-8")

    def do_POST(self):
        if self.path != "/api/dossier":
            return self._send(404, b"{}", "application/json")
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n > 20_000:
                raise ValueError("requête trop longue")
            out, code = produce(json.loads(self.rfile.read(n) or b"{}")), 200
        except (ValueError, KeyError) as e:
            out, code = {"erreur": str(e).strip("'\"")}, 400
        except Exception as e:  # erreur AWS ou agent : message lisible, jamais de trace renvoyée au navigateur
            out, code = {"erreur": _explain(e)}, 502
        self._send(code, json.dumps(out, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def log_message(self, fmt, *args):  # journal court sur la sortie standard
        print("app :", fmt % args)


def _explain(e: Exception) -> str:
    name = type(e).__name__
    if name in ("NoCredentialsError", "ProfileNotFound"):
        return "Accès AWS non configuré : lancez « bash scripts/configurer-aws-workshop.sh », puis réessayez."
    if "ExpiredToken" in str(e) or name == "TokenRetrievalError":
        return "Identifiants AWS expirés : relancez « bash scripts/configurer-aws-workshop.sh » avec les nouvelles valeurs."
    if name == "RuntimeError":
        return f"Dossier non produit : {e}"
    return f"Appel Amazon Bedrock en échec ({name})."


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="alphaforge-app", description="Application web locale AlphaForge (simulation).")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--ouvrir", action="store_true", help="ouvrir le navigateur")
    args = ap.parse_args(argv)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}"
    print(f"AlphaForge : {url} (Ctrl-C pour arrêter)")
    if args.ouvrir:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
