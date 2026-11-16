"""Consolide les résultats d'un workflow de recherche : fiches, vérifications, registre des sources, manifeste.

    uv run python research/outils/consolider_recherche.py extraire JOURNAL.jsonl
    uv run python research/outils/consolider_recherche.py registre
    uv run python research/outils/consolider_recherche.py condense [CLE]
    uv run python research/outils/consolider_recherche.py court [CLE]
    uv run python research/outils/consolider_recherche.py manifeste DOSSIER_DES_TEXTES
    uv run python research/outils/consolider_recherche.py assembler

Les fiches brutes (JSON) vont dans research/fiches/ ; le registre dans research/R07-registre-des-sources-2026-11-15.md.
Les textes téléchargés restent hors de git (research/sources/textes/) : seul leur manifeste est versé.
"""

import hashlib
import json
import shutil
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
FICHES = RACINE / "fiches"
ORDRE = ["qualification", "recherche", "analyse", "confrontation", "restitution", "organisation"]
TITRES = {"qualification": "Qualification et formalisation (agent 0)", "recherche": "Recherche et revue de littérature (agent 1)",
          "analyse": "Analyse et résolution (agent 2)", "confrontation": "Confrontation des arguments (contradicteur rattaché à l'agent 2)",
          "restitution": "Restitution et interaction (agent 3)", "organisation": "Organisation d'ensemble et documents de travail"}
NATURES = {"resultat_theorique": "résultat théorique", "resultat_empirique": "résultat empirique", "cadre_professionnel": "cadre professionnel",
           "documentation_technique": "documentation technique", "guide_de_praticien": "guide de praticien", "affirmation_commerciale": "affirmation commerciale"}
VERDICTS = {"confirmee": "confirmée", "corrigee": "corrigée", "non_verifiable": "non vérifiable", "fausse": "fausse"}


def extraire(journal):
    FICHES.mkdir(exist_ok=True)
    labels, n = {}, 0
    for line in Path(journal).read_text().splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "started":
            labels[d["agentId"]] = d["label"]
        elif d.get("type") == "result" and d.get("result"):
            label = labels.get(d["agentId"], d["agentId"])
            (FICHES / (label.replace(":", "-") + ".json")).write_text(json.dumps(d["result"], ensure_ascii=False, indent=1))
            n += 1
            print("extrait :", label, len(json.dumps(d["result"])) // 1000, "ko")
    print(n, "résultats")


def charge(prefixe, cle):
    p = FICHES / f"{prefixe}-{cle}.json"
    return json.loads(p.read_text()) if p.exists() else None


def une_ligne(s):
    return " ".join(str(s or "").split())


def registre():
    out = ["# R07 — Registre des sources de la recherche sur les processus professionnels (15 novembre 2026)", "",
           "Produit par `research/outils/consolider_recherche.py registre` à partir des fiches de `research/fiches/`. Ne pas modifier à la main.", "",
           "Chaque source déterminante est décrite selon le standard demandé : référence et version, niveau de lecture réel, résultat ou méthode utilisé, "
           "hypothèses et limites, élément du projet influencé, contradiction éventuelle, passage clé. La **nature** sépare résultat théorique, résultat empirique, "
           "cadre professionnel, documentation technique, guide de praticien et affirmation commerciale.", "",
           "Chaque fiche a été relue par un vérificateur indépendant chargé de réfuter : retour au texte, recherche de la citation, contrôle de la version et du niveau "
           "de lecture. Son verdict figure sous chaque source ; quand il corrige la fiche, la correction prime.", ""]
    total = {"decisives": 0, "confirmee": 0, "corrigee": 0, "non_verifiable": 0, "fausse": 0, "sans_verdict": 0, "secondaires": 0}
    corps = []
    for cle in ORDRE:
        f, v = charge("recherche", cle), charge("verif", cle)
        if not f:
            corps += [f"## {TITRES[cle]}", "", "Aucune fiche produite.", ""]
            continue
        verdicts = {s["id"]: s for s in (v or {}).get("sources", [])}
        corps += [f"## {TITRES[cle]}", ""]
        if v:
            corps += ["**Bilan du vérificateur.** " + une_ligne(v.get("bilan")), ""]
        else:
            corps += ["**Fiche non vérifiée** (le vérificateur n'a pas rendu de résultat).", ""]
        for s in sorted(f.get("sources", []), key=lambda s: (not s.get("decisive"), s["id"])):
            vd = verdicts.get(s["id"])
            total["decisives"] += bool(s.get("decisive"))
            total[vd["verdict"] if vd else "sans_verdict"] += 1
            corps += [f"### {s['id']} — {une_ligne(s['reference'])}", "",
                      f"- **Nature** : {NATURES.get(s['nature'], s['nature'])}" + ("" if s.get("decisive") else " ; source d'appui, non déterminante"),
                      f"- **Niveau de lecture déclaré** : {une_ligne(s['niveau_de_lecture'])}",
                      f"- **Résultat ou méthode utilisé** : {une_ligne(s['resultat_ou_methode'])}",
                      f"- **Hypothèses et limites** : {une_ligne(s['hypotheses_et_limites'])}",
                      f"- **Élément du projet influencé** : {une_ligne(s['element_du_projet'])}",
                      f"- **Contradiction** : {une_ligne(s.get('contradiction') or 'aucune relevée')}"]
            if s.get("passage_cle"):
                corps.append(f"- **Passage clé** : {une_ligne(s['passage_cle'])}")
            if vd:
                ligne = f"- **Vérification** : {VERDICTS.get(vd['verdict'], vd['verdict'])}. {une_ligne(vd.get('ce_que_j_ai_verifie'))}"
                if vd.get("niveau_de_lecture_reel"):
                    ligne += f" Niveau de lecture constaté : {une_ligne(vd['niveau_de_lecture_reel'])}."
                if vd.get("correction"):
                    ligne += f" **Correction** : {une_ligne(vd['correction'])}"
                corps.append(ligne)
            else:
                corps.append("- **Vérification** : source non examinée par le vérificateur.")
            corps.append("")
        for titre, champ, src in (("Sources adverses ou nuances trouvées par le vérificateur", "contradictions_et_sources_adverses", v),
                                  ("Affirmations de la fiche que les sources ne soutiennent pas", "affirmations_sans_appui", v),
                                  ("Fonctions décrites sans base dans les textes", "fonctions_inventees", v),
                                  ("Versions périmées", "versions_perimees", v),
                                  ("Verdicts d'applicabilité à corriger", "corrections_d_applicabilite", v),
                                  ("Sources secondaires (repérées, non déterminantes)", "sources_secondaires", f),
                                  ("Recherches sans résultat", "recherches_sans_resultat", f)):
            items = (src or {}).get(champ) or []
            if items:
                if champ == "sources_secondaires":
                    total["secondaires"] += len(items)
                corps += [f"**{titre}**", ""] + [f"- {une_ligne(x)}" for x in items] + [""]
    out += ["## Décompte", "",
            f"- Sources décrites au standard : {sum(total[k] for k in ('confirmee', 'corrigee', 'non_verifiable', 'fausse', 'sans_verdict'))}, dont {total['decisives']} déterminantes.",
            f"- Verdicts des vérificateurs : {total['confirmee']} confirmées, {total['corrigee']} corrigées, {total['non_verifiable']} non vérifiables, {total['fausse']} fausses, {total['sans_verdict']} non examinées.",
            f"- Sources secondaires repérées : {total['secondaires']}.", ""] + corps
    cible = RACINE / "R07-registre-des-sources-2026-11-15.md"
    cible.write_text("\n".join(out))
    print("écrit :", cible, "|", total)


def coupe(s, n):
    s = une_ligne(s)
    return s if len(s) <= n else s[: n - 1] + "…"


def condense(cles):
    for cle in cles or ORDRE:
        f, v = charge("recherche", cle), charge("verif", cle)
        if not f:
            print(f"\n===== {cle} : aucune fiche")
            continue
        print(f"\n===== {cle.upper()} =====\nSYNTHÈSE : {une_ligne(f['synthese'])}")
        print("\nFONCTIONS PROFESSIONNELLES")
        for x in f["fonctions_professionnelles"]:
            print(f" • {coupe(x['fonction'], 110)} — {coupe(x['qui_l_exerce'], 170)} [{', '.join(x['sources'])}]\n     adaptation : {coupe(x['adaptation_au_datathon'], 260)}")
        print("\nMÉTHODES")
        for x in f["methodes"]:
            print(f" • [{x['statut']}] {coupe(x['methode'], 100)} — {coupe(x['applicabilite_a_nos_donnees'], 230)} [{', '.join(x['sources'])}]")
        print("\nDÉCLENCHEURS")
        for x in f["declencheurs"]:
            print(f" • {x['action']} → {coupe(x['vers'], 40)} : {coupe(x['situation'], 170)}")
        print("\nCONTROVERSES")
        for x in f["controverses_et_inconnues"]:
            print(f" • {coupe(x['question'], 150)} || {coupe(x['positions'], 330)} || trancherait : {coupe(x['ce_qui_trancherait'], 170)}")
        print("\nRECOMMANDATION :", une_ligne(f["recommandation"]))
        print("\nSOURCES")
        vd = {s["id"]: s for s in (v or {}).get("sources", [])}
        for s in f["sources"]:
            x = vd.get(s["id"], {})
            print(f" • {s['id']}{'*' if s.get('decisive') else ''} [{s['nature']}] {coupe(s['reference'], 150)} | lecture : {coupe(s['niveau_de_lecture'], 70)} | vérif : {x.get('verdict', '—')} {coupe(x.get('correction', ''), 200)}")
        if v:
            print("\nBILAN DU VÉRIFICATEUR :", une_ligne(v["bilan"]))
            for champ in ("affirmations_sans_appui", "fonctions_inventees", "contradictions_et_sources_adverses", "versions_perimees", "corrections_d_applicabilite"):
                for x in v.get(champ) or []:
                    print(f"   [{champ}] {coupe(x, 420)}")


def court(cles):
    """Vue de synthèse : ce que la recherche établit, ce qu'elle recommande, ce qui reste ouvert, ce que le vérificateur corrige."""
    for cle in cles or ORDRE:
        f, v = charge("recherche", cle), charge("verif", cle)
        if not f:
            print(f"\n===== {cle} : aucune fiche")
            continue
        print(f"\n===== {cle.upper()} =====\nSYNTHÈSE : {une_ligne(f['synthese'])}")
        print("\nFONCTIONS :", " | ".join(f"{coupe(x['fonction'], 90)} [{', '.join(x['sources'][:4])}]" for x in f["fonctions_professionnelles"]))
        print("\nMÉTHODES :", " | ".join(f"[{x['statut']}] {coupe(x['methode'], 90)}" for x in f["methodes"]))
        print("\nCONTROVERSES")
        for x in f["controverses_et_inconnues"]:
            print(f" • {coupe(x['question'], 160)} || {coupe(x['positions'], 260)} || trancherait : {coupe(x['ce_qui_trancherait'], 150)}")
        print("\nEXPÉRIENCES SUGGÉRÉES :", " | ".join(coupe(x["question"], 130) for x in f.get("experiences_suggerees") or []))
        print("\nRECOMMANDATION :", une_ligne(f["recommandation"]))
        print("\nSOURCES DÉTERMINANTES :", " | ".join(f"{s['id']} {coupe(s['reference'], 95)} ({coupe(s['niveau_de_lecture'], 40)})" for s in f["sources"] if s.get("decisive")))
        if v:
            print("\nBILAN DU VÉRIFICATEUR :", une_ligne(v["bilan"]))
            print("VERDICTS :", " ".join(f"{s['id']}={s['verdict']}" for s in v.get("sources", [])))
            for champ in ("affirmations_sans_appui", "fonctions_inventees", "contradictions_et_sources_adverses", "versions_perimees", "corrections_d_applicabilite"):
                for x in v.get(champ) or []:
                    print(f"   [{champ}] {coupe(x, 380)}")
        else:
            print("\n(vérification non disponible)")


def verifs(cles):
    """Ce que les vérificateurs corrigent, sans le reste de la fiche."""
    for cle in cles or ORDRE:
        v = charge("verif", cle)
        if not v:
            print(f"\n===== {cle} : vérification absente")
            continue
        print(f"\n===== {cle.upper()} =====\nBILAN : {une_ligne(v['bilan'])}")
        for s in v.get("sources", []):
            if s["verdict"] != "confirmee":
                print(f" • {s['id']} = {s['verdict']} : {coupe(s.get('correction') or s.get('ce_que_j_ai_verifie'), 420)}")
        print("   confirmées :", " ".join(s["id"] for s in v.get("sources", []) if s["verdict"] == "confirmee"))
        for champ in ("affirmations_sans_appui", "fonctions_inventees", "contradictions_et_sources_adverses", "versions_perimees", "corrections_d_applicabilite"):
            for x in v.get(champ) or []:
                print(f"   [{champ}] {coupe(x, 520)}")


def manifeste(dossier):
    src, dst = Path(dossier), RACINE / "sources" / "textes"
    dst.mkdir(parents=True, exist_ok=True)
    (RACINE / "sources" / ".gitignore").write_text("textes/\n")
    refs = {}
    for cle in ORDRE:
        for s in (charge("recherche", cle) or {}).get("sources", []):
            if s.get("chemin_local") and "non téléchargé" not in s["chemin_local"]:
                refs[Path(s["chemin_local"].split(" ")[0]).name] = (s["id"], une_ligne(s["reference"]))
    lignes = []
    for p in sorted(src.rglob("*")):
        if not p.is_file() or p.stat().st_size == 0:
            continue
        rel = p.relative_to(src)
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst / rel)
        ident, ref = refs.get(p.name, ("", ""))
        lignes.append({"fichier": str(rel), "octets": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "source": ident, "reference": ref})
    (RACINE / "sources" / "manifeste.json").write_text(json.dumps(lignes, ensure_ascii=False, indent=1))
    print(len(lignes), "fichiers copiés hors git ;", sum(1 for x in lignes if x["source"]), "rattachés à une source du registre")


def assembler():
    """Réunit les rédactions par fonction en deux documents de docs/refonte/."""
    red, cible = FICHES / "redaction", RACINE.parent / "docs" / "refonte"
    renvois = ("Les identifiants entre crochets renvoient au registre des sources (`research/R07-registre-des-sources-2026-11-15.md`) ; "
               "`[R09 …]` renvoie aux expériences (`research/R09-experiences-discriminantes-2026-11-15.md`) ; `[conception]` marque une proposition de l'équipe "
               "qui ne vient d'aucune source. Rédigé à partir des fiches de recherche (`research/fiches/`), puis relu contre les rapports des vérificateurs.")
    docs = {
        "revue-par-questions.md": ("# Revue par questions et décisions — détail par fonction", "revue",
                                   "Livrable 2 de la recherche sur les processus professionnels (15 novembre 2026). La synthèse se trouve dans "
                                   "`recherche-processus-professionnels.md`, section 4. Pour chaque question : ce que les sources établissent, ce que cela donne sur "
                                   "notre cas, la décision proposée, la solidité de son appui, et ce qui la contredit ou la limite."),
        "fiches-des-agents.md": ("# Fiches méthodologiques des quatre agents", "fiche",
                                 "Livrable 3 de la recherche sur les processus professionnels (15 novembre 2026). Une fiche par rôle, dans l'ordre de la chaîne, "
                                 "avec les six rubriques demandées ; le contradicteur, rattaché à l'agent 2, a sa propre fiche ; la dernière partie décrit "
                                 "l'organisation d'ensemble (cartographie détaillée, enchaînement, mesure de l'apport de chaque rôle). Le produit n'est pas modifié : "
                                 "ces fiches décrivent le fonctionnement cible proposé."),
    }
    for nom, (titre, suffixe, chapeau) in docs.items():
        parts, manquants = [titre, "", chapeau, "", renvois, ""], []
        for cle in ORDRE:
            f = red / f"{cle}-{suffixe}.md"
            if f.exists():
                parts += [f.read_text().strip(), ""]
            else:
                manquants.append(cle)
        (cible / nom).write_text("\n".join(parts) + "\n")
        print("écrit :", cible / nom, "| lignes :", sum(x.count("\n") + 1 for x in parts), "| manquants :", manquants)


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    {"extraire": lambda: extraire(args[0]), "registre": registre, "condense": lambda: condense(args), "court": lambda: court(args), "verifs": lambda: verifs(args), "manifeste": lambda: manifeste(args[0]), "assembler": assembler}[cmd]()
