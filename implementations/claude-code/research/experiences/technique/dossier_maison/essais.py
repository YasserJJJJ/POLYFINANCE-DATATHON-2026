"""Essais du dossier maison : assertions (a) à (h) et quelques garde-fous. Voir LISEZMOI.md.

    python3 research/experiences/technique/dossier_maison/essais.py
    uv run --with prov python research/experiences/technique/dossier_maison/essais.py   # contrôle PROV en plus

Aucun appel de modèle, aucun accès au réseau. Tout se passe dans un dossier temporaire ; un exemplaire
du dossier le plus complet est recopié dans sorties/dossier_exemple pour être ouvert à la main.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))

import chaine  # noqa: E402
from chaine import APPELS, CATALOGUE, DONNEES, DROITS, FAITS, FONCTIONS, TACHES  # noqa: E402
from dossier import PRINCIPALE, Dossier, EcritureInterdite, Tache, TeteDepassee, empreinte  # noqa: E402
from export_prov import controler_avec_prov, exporter  # noqa: E402

COMPTE: Counter = Counter()
DERIVES = ["decision", "preuves", "plan", "calculs", "objections", "restitution"]  # emplacements écrits par les tâches
TOUTES = ["qualification", "preuves", "plan", "calculs", "objections", "restitution"]  # noms des tâches
P = PRINCIPALE


def exige(condition, quoi: str) -> None:
    COMPTE["assertions"] += 1
    if not condition:
        raise AssertionError(quoi)


def refuse(exception, action, quoi: str) -> None:
    try:
        action()
    except exception:
        COMPTE["assertions"] += 1
        return
    raise AssertionError(f"aurait dû être refusé : {quoi}")


def ouvrir(racine, taches=TACHES) -> Dossier:
    return Dossier(racine, taches, DROITS)


def copie(base: Path, nom: str) -> Dossier:
    shutil.copytree(base, base.parent / nom)
    return ouvrir(base.parent / nom)


def corriger(d: Dossier, champ: str, valeur, branche: str = P, nature: str = "correction") -> dict:
    return d.deposer(branche, champ, valeur, "personne", d.sommet(branche), nature=nature)


def reprendre(d: Dossier, branche: str = P, fonctions=FONCTIONS, **options) -> list[str]:
    APPELS.clear()
    return d.avancer(branche, fonctions, **options)


def nb_pieces(d: Dossier) -> int:
    return len(list((d.racine / "pieces").glob("*.json")))


def par_tache(d: Dossier) -> Counter:
    return Counter((e["type"], e.get("tache")) for e in d.evenements())


# ------------------------------------------------------- processus auxiliaires
def mode_mourir(racine: str) -> None:
    """Ouvre l'étude puis meurt en plein « calculs » : os._exit ne nettoie rien, comme une panne."""
    d = ouvrir(racine)
    d.deposer(P, "donnees", DONNEES, "code", d.sommet())
    d.deposer(P, "catalogue", CATALOGUE, "code", d.sommet())
    for champ, valeur in FAITS.items():
        corriger(d, champ, valeur, nature="initiale")
    d.avancer(P, {**FONCTIONS, "calculs": lambda e: os._exit(17)})


def mode_ecrire(racine: str, prolonge: str, i: str, quand: str) -> None:
    if os.environ.get("SANS_VERROU"):  # contre-épreuve seulement : le verrou du journal est neutralisé
        import dossier as module

        module.fcntl.flock = lambda *a: None
    d = ouvrir(racine)
    time.sleep(max(0.0, float(quand) - time.time()))
    try:
        d.deposer(P, "fait:prenom", f"Robert-{i}", "personne", prolonge, nature="correction")
        print("accepte")
    except TeteDepassee:
        print("refuse")


# ---------------------------------------------------------------------- essais
def essai_c_reprise_et_question(base: Path) -> None:
    """(c) arrêt réel en cours d'étude puis reprise ; question à la personne qui suspend sans bloquer."""
    code = subprocess.run([sys.executable, __file__, "--mourir", str(base)]).returncode
    exige(code == 17, "le processus devait mourir pendant « calculs »")
    d, n = ouvrir(base), None
    n = par_tache(d)
    exige([n[("tache_terminee", t)] for t in TOUTES[:4]] == [1, 1, 1, 0], "trois tâches terminées avant la panne")
    exige(n[("tache_lancee", "calculs")] == 1, "« calculs » lancée, jamais terminée")
    exige(d.bilan()["etat"] == "à poursuivre" and [t.nom for t in d.bilan()["pretes"]] == ["calculs"], "bilan après panne")
    faites = reprendre(d)
    exige(faites == ["calculs", "objections"] and dict(APPELS) == {"calculs": 1, "objections": 1},
          f"reprise : seules les tâches non terminées sont exécutées ({faites}, {dict(APPELS)})")
    n = par_tache(d)
    exige(n[("tache_lancee", "calculs")] == 2 and n[("tache_terminee", "calculs")] == 1, "les deux tentatives sont au journal")
    exige(reprendre(d) == [] and not APPELS, "seconde reprise : rien à refaire")
    b = d.bilan()
    exige(b["etat"] == "en attente de la personne" and b["questions"] == ["fait:perte_acceptable"]
          and b["attente"] == {"restitution": ["fait:perte_acceptable"]}, f"étude suspendue à la question ({b})")
    exige(set(DERIVES) - set(d.tete()) == {"restitution"}, "ce qui ne dépend pas de la réponse est déjà fait")
    corriger(d, "fait:perte_acceptable", 10, nature="précision")
    exige(reprendre(d) == ["restitution"] and dict(APPELS) == {"restitution": 1}, "la réponse ne lance que la restitution")
    exige(d.bilan()["etat"] == "complète" and d.verifier() == [], "étude complète, journal intègre")
    exige(all(s["etat"] == "en vigueur" for s in d.etats().values()), "au départ, toutes les pièces sont en vigueur")


def essai_ligne_tronquee(base: Path) -> None:
    """Panne au milieu d'une écriture du journal : la ligne incomplète n'est pas un événement."""
    d = copie(base, "tronquee")
    avant = d.tete()
    with open(d._fichier(P), "ab") as f:
        f.write(b'{"n": 99, "type": "depot", "emplac')
    exige(d.tete() == avant, "la tête ne change pas")
    exige(len(d.verifier()) == 1 and "illisible" in d.verifier()[0], "la ligne tronquée est signalée")
    corriger(d, "fait:prenom", "Roberte")
    exige(d.tete()["fait:prenom"] != avant["fait:prenom"] and len(d.verifier()) == 1,
          "l'écriture suivante repart sur une ligne neuve ; la chaîne des empreintes tient")


CAS_A = {  # champ -> (nouvelle valeur, emplacements périmés attendus, tâches réellement refaites attendues)
    "fait:prenom": ("Roberte", {"restitution"}, ["restitution"]),
    "fait:perte_acceptable": (4, {"restitution"}, ["restitution"]),
    "fait:horizon": (3, {"plan", "calculs", "objections", "restitution"}, TOUTES[2:]),
    "fait:part": (15, set(DERIVES), TOUTES),
    "fait:titre": ("NVDA", set(DERIVES), TOUTES),
    "fait:objectif": ("Je veux préserver mon capital", set(DERIVES), ["qualification"]),  # reformulation sans effet
}


def essai_a_invalidation(base: Path) -> None:
    """(a) un seul champ change : l'ensemble périmé est exactement celui attendu, écrit ici à la main."""
    for champ, (valeur, attendues, refaites) in CAS_A.items():
        d = copie(base, "a_" + champ.split(":")[1])
        avant, pieces_avant = d.tete(), nb_pieces(d)
        evt = corriger(d, champ, valeur)
        etats, apres = d.etats(), d.tete()
        perimees = {s["emplacement"] for s in etats.values() if s["etat"] == "périmée"}
        exige(perimees == attendues, f"{champ} : périmées {sorted(perimees)}, attendues {sorted(attendues)}")
        exige(all(s["cause"] == evt["empreinte"] for s in etats.values() if s["etat"] == "périmée"),
              f"{champ} : chaque pièce périmée nomme l'événement qui l'a périmée")
        ancien = etats[avant[champ]]
        exige(ancien["etat"] == "remplacée" and ancien["cause"] == evt["empreinte"], f"{champ} : ancien fait remplacé")
        exige(set(apres) == set(avant) - attendues and all(apres[k] == avant[k] for k in apres if k != champ),
              f"{champ} : tout le reste est en vigueur, aux mêmes empreintes")
        faites = reprendre(d)
        exige(faites == refaites and sum(APPELS.values()) == len(refaites), f"{champ} : refaites {faites}, attendues {refaites}")
        exige(d.bilan()["etat"] == "complète" and d.verifier() == [], f"{champ} : étude de nouveau complète")
        if champ == "fait:objectif":
            exige(all(d.tete()[k] == avant[k] for k in DERIVES),
                  "coupure anticipée : la décision refaite a la même empreinte, les six pièces d'origine reviennent")
        if champ == "fait:part":  # « preuves » est refaite et rend le même contenu : une pièce, deux productions
            productions = [e for e in d.evenements() if e["type"] == "tache_terminee" and e["piece"] == avant["preuves"]]
            exige(d.tete()["preuves"] == avant["preuves"] and len(productions) == 2, "même contenu, même pièce, deux productions")
            exige(nb_pieces(d) == pieces_avant + 6, "six pièces nouvelles (le fait et cinq sorties) pour six tâches refaites")
        print(f"    {champ:<22} périme {len(perimees)} pièce(s), refait {len(faites)} tâche(s) : {', '.join(faites)}")


def essai_e_retour(base: Path) -> None:
    """(e) un résultat périmé redevient en vigueur sans recalcul quand ses entrées reviennent."""
    d = copie(base, "e_retour")
    origine = d.tete()
    corriger(d, "fait:horizon", 3)
    exige(reprendre(d) == TOUTES[2:], "horizon 3 : quatre tâches refaites")
    variante, pieces = d.tete(), nb_pieces(d)
    retour = corriger(d, "fait:horizon", 5)
    exige(d.tete() == origine, "horizon 5 de retour : la tête d'origine revient, empreinte pour empreinte")
    exige(reprendre(d) == [] and not APPELS and nb_pieces(d) == pieces, "aucun recalcul, aucune pièce nouvelle")
    etats = d.etats()
    exige(all(etats[origine[k]]["etat"] == "en vigueur" for k in DERIVES), "les pièces d'origine sont en vigueur")
    exige(all(etats[variante[k]]["etat"] == "périmée" and etats[variante[k]]["cause"] == retour["empreinte"]
              for k in DERIVES[2:]), "les pièces de l'horizon 3 sont périmées par le retour")


def essai_b_variante(base: Path) -> None:
    """(b) une variante ouvre une branche qui partage les pièces non touchées ; la ligne principale est intacte."""
    d, v = copie(base, "b_variante"), "et-si-horizon-3"
    journal = d._fichier(P)
    octets, sommet, tete, pieces = journal.read_bytes(), d.sommet(), d.tete(), nb_pieces(d)
    d.ouvrir_branche(v)
    exige(d.tete(v) == tete, "à l'ouverture, la branche a la tête de son parent")
    corriger(d, "fait:horizon", 3, branche=v, nature="variante")
    exige(reprendre(d, v) == TOUTES[2:] and sum(APPELS.values()) == 4, "la variante ne refait que quatre tâches")
    tv = d.tete(v)
    exige(sorted(k for k in tete if tv[k] != tete[k]) == sorted(["fait:horizon"] + DERIVES[2:]),
          "la branche ne diffère que par l'horizon et ce qui en dépend")
    exige(tv["decision"] == tete["decision"] and tv["preuves"] == tete["preuves"], "décision et preuves partagées")
    exige(journal.read_bytes() == octets and d.sommet() == sommet and d.tete() == tete and d.bilan()["etat"] == "complète",
          "ligne principale intacte, octet pour octet")
    exige(nb_pieces(d) - pieces == 5, "cinq pièces nouvelles ; les autres sont partagées, pas copiées")
    exige(len(d._propres(v)) == 10, "le fichier de la branche ne contient que ses dix événements")
    refuse(EcritureInterdite, lambda: d.ouvrir_branche(v), "deux branches du même nom")
    corriger(d, "fait:prenom", "Roberte")
    exige(d.tete(v) == tv, "une correction sur la ligne principale ne touche pas la variante")
    passe = d.evenements()[8]
    d.ouvrir_branche("depuis-le-passe", depuis=passe["empreinte"])
    exige(d.tete("depuis-le-passe") == d.tete(evenements=d.evenements()[:9]), "bifurcation depuis un état passé")
    exige(d.verifier() == [] and d.verifier(v) == [], "journaux intègres")


def essai_d_concurrence(base: Path) -> None:
    """(d) deux écritures sur le même sommet : la seconde est refusée. Puis huit processus à la fois."""
    a = copie(base, "d_concurrence")
    b = ouvrir(a.racine)
    sommet, n = a.sommet(), len(a.evenements())
    a.deposer(P, "fait:prenom", "Roberto", "personne", sommet, nature="correction")
    refuse(TeteDepassee, lambda: b.deposer(P, "fait:horizon", 7, "personne", sommet, nature="correction"),
           "seconde écriture préparée sur le même sommet")
    exige(len(a.evenements()) == n + 1 and a.lire(a.tete()["fait:horizon"])["corps"] == 5, "le refus n'a rien écrit")
    corriger(b, "fait:horizon", 7)
    exige(len(a.evenements()) == n + 2 and a.lire(a.tete()["fait:horizon"])["corps"] == 7, "rejouée sur le nouveau sommet")
    sommet, n, quand = a.sommet(), len(a.evenements()), time.time() + 1.0
    lances = [subprocess.Popen([sys.executable, __file__, "--ecrire", str(a.racine), sommet, str(i), str(quand)],
                               stdout=subprocess.PIPE, text=True) for i in range(8)]
    reponses = Counter(p.communicate()[0].strip() for p in lances)
    exige(reponses == {"accepte": 1, "refuse": 7}, f"huit écrivains au même instant : {dict(reponses)}")
    exige(len(a.evenements()) == n + 1 and a.verifier() == [], "un seul événement ajouté, journal intègre")
    citees = {e["piece"] for e in a.evenements() if "piece" in e}
    orphelines = {p.stem for p in (a.racine / "pieces").glob("*.json")} - citees
    exige(len(orphelines) == 7, f"les sept refus laissent sept pièces sans événement ({len(orphelines)})")

    c = copie(base, "d_pendant")  # la personne corrige pendant qu'une tâche tourne
    corriger(c, "fait:horizon", 4)

    def plan_pendant_correction(e):
        if APPELS["plan"] == 0:
            corriger(c, "fait:horizon", 6)
        return chaine.plan(e)

    faites = reprendre(c, fonctions={**FONCTIONS, "plan": plan_pendant_correction})
    exige(faites == ["plan"] + TOUTES[2:] and APPELS["plan"] == 2, f"le plan est refait pour la nouvelle valeur ({faites})")
    exige(c.lire(c.tete()["plan"])["corps"]["horizon_ans"] == 6 and c.bilan()["etat"] == "complète" and c.verifier() == [],
          "la tête finale porte l'horizon 6")
    perimes = [s for s in c.etats().values() if s["emplacement"] == "plan" and s["etat"] == "périmée"]
    exige(len(perimes) == 2, "le plan d'origine et le plan arrivé trop tard sont périmés, pas perdus")


def essai_f_erronee(base: Path) -> Dossier:
    """(f) une pièce retirée comme erronée se distingue d'une pièce périmée."""
    d = copie(base, "f_erronee")
    t = d.tete()
    aff = d.afficher(P, t["restitution"], d.sommet(), profondeur="courte")
    d.reagir(P, aff["empreinte"], "choix", "Je garde le portefeuille actuel.", d.sommet())
    ret = d.retirer(P, t["calculs"], "code", "signe de l'écart inversé", d.sommet())
    etats = d.etats()
    faux = etats[t["calculs"]]
    exige(faux["etat"] == "erronée" and faux["motif"] == "signe de l'écart inversé" and faux["cause"] == ret["empreinte"],
          "la pièce retirée est « erronée », avec son motif")
    exige(all(etats[t[k]]["etat"] == "périmée" and etats[t[k]]["cause"] == ret["empreinte"] for k in DERIVES[4:]),
          "ce qui en dérive est périmé, et la cause nommée est le retrait")
    exige(all(etats[t[k]]["etat"] == "en vigueur" for k in DERIVES[:3]), "l'amont reste en vigueur")
    exige(d.lire(t["calculs"])["corps"]["fictif"] is True, "la pièce retirée reste lisible")
    b = d.bilan()
    exige(b["etat"] == "interrompue" and list(b["bloquees"]) == ["calculs"], f"étude interrompue, pas conclue ({b['etat']})")
    exige(reprendre(d) == [] and not APPELS, "même clé : la tâche n'est pas relancée pour refaire la même erreur")
    exige([e["empreinte"] for e in d.affichages_a_signaler()] == [aff["empreinte"]], "l'affichage qui en dépendait est à signaler")
    corriger(d, "fait:horizon", 3)
    corriger(d, "fait:horizon", 5)
    exige("calculs" not in d.tete() and d.etats()[t["calculs"]]["etat"] == "erronée" and d.tete()["plan"] == t["plan"],
          "contraste avec (e) : les mêmes entrées reviennent, la pièce erronée ne revient pas")
    v2 = [Tache(x.nom, x.auteur, x.entrees, x.sortie, "2") if x.nom == "calculs" else x for x in TACHES]
    d2 = ouvrir(d.racine, v2)
    exige(reprendre(d2, fonctions={**FONCTIONS, "calculs": chaine.calculs_v2}) == TOUTES[3:], "calcul corrigé : trois tâches")
    t2 = d2.tete()
    exige(t2["calculs"] != t["calculs"] and d2.bilan()["etat"] == "complète", "nouvelle pièce de calcul, étude complète")
    corriger(d2, "fait:prenom", "Roberte")
    etats, types = d2.etats(), {e["empreinte"]: e["type"] for e in d2.evenements()}
    exige(etats[t2["restitution"]]["etat"] == "périmée" and types[etats[t2["restitution"]]["cause"]] == "depot"
          and etats[t["calculs"]]["etat"] == "erronée" and types[etats[t["calculs"]]["cause"]] == "retrait",
          "périmée (par une correction) et erronée (par un retrait) coexistent sans se confondre")
    reprendre(d2)
    return d2


def essai_g_affichage(base: Path) -> None:
    """(g) restitution préparée, affichage enregistré, réaction de la personne : trois choses."""
    d = copie(base, "g_affichage")
    t = d.tete()

    def genre(type_: str) -> list[dict]:
        return [e for e in d.evenements() if e["type"] == type_]

    exige("restitution" in t and not genre("affichage") and not genre("reaction"), "préparée : ni affichée ni choisie")
    refuse(EcritureInterdite, lambda: d.reagir(P, t["restitution"], "choix", "…", d.sommet()),
           "réagir à une restitution préparée mais jamais affichée")
    refuse(EcritureInterdite, lambda: d.afficher(P, t["calculs"], d.sommet()), "afficher autre chose qu'une restitution")
    aff = d.afficher(P, t["restitution"], d.sommet(), profondeur="courte")
    exige(len(genre("affichage")) == 1 and not genre("reaction") and aff["auteur"] == "interface" and d.tete() == t,
          "affichée : aucun choix ne s'en déduit, et la tête ne bouge pas")
    rea = d.reagir(P, aff["empreinte"], "choix", "Je garde le portefeuille actuel.", d.sommet())
    exige(rea["auteur"] == "personne" and rea["affichage"] == aff["empreinte"] and aff["piece"] == t["restitution"],
          "le choix se rattache à l'affichage, donc à la version montrée")
    corriger(d, "fait:perte_acceptable", 4)
    reprendre(d)
    t2 = d.tete()
    exige(t2["restitution"] != t["restitution"] and all(e["piece"] != t2["restitution"] for e in genre("affichage")),
          "après correction : une nouvelle version est préparée, elle n'a pas été affichée")
    exige(d.etats()[aff["piece"]]["etat"] == "périmée", "le choix porte sur une version périmée : l'interface peut le dire")
    auteurs = {(e["type"], e["auteur"]) for e in d.evenements()
               if e["type"] in ("affichage", "reaction") or e.get("emplacement") == "restitution"}
    exige(auteurs == {("tache_terminee", "agent3"), ("affichage", "interface"), ("reaction", "personne")},
          "trois types d'événements, trois auteurs")


def essai_h_prov(d: Dossier, sorties: Path) -> dict:
    """(h) export PROV-JSON par la bibliothèque standard ; relecture par le paquet « prov » s'il est là."""
    doc = exporter(d)
    texte = json.dumps(doc, ensure_ascii=False, indent=1)
    (sorties / "dossier.prov.json").write_text(texte, encoding="utf-8")
    evts = d.evenements()
    n = Counter(e["type"] for e in evts)
    pieces = {e["piece"] for e in evts if e["type"] in ("depot", "tache_terminee")}
    exige(len(doc["entity"]) == len(pieces) + n["reaction"], "une entité par pièce et par réaction")
    exige(len(doc["wasGeneratedBy"]) == n["tache_terminee"] and len(doc["wasInvalidatedBy"]) == n["retrait"] == 1,
          "une génération par tâche terminée ; une seule invalidation, celle du retrait")
    exige(len(doc["used"]) == sum(len(e["entrees"]) for e in evts if e["type"] == "tache_terminee") + n["affichage"],
          "un usage par entrée de tâche et par affichage")
    perimees = [h for h, s in d.etats().items() if s["etat"] == "périmée"]
    invalidees = {v["prov:entity"] for v in doc["wasInvalidatedBy"].values()}
    exige(perimees and not any(f"af:piece-{h[:16]}" in invalidees for h in perimees),
          "aucune pièce périmée n'est exportée comme invalidée")
    exige(json.loads(texte) == doc, "aller-retour JSON")
    total = sum(len(v) for k, v in doc.items() if k != "prefix")
    resume = {"enregistrements": total, "par_section": {k: len(v) for k, v in doc.items() if k != "prefix"}}
    try:
        controle = controler_avec_prov(texte)
    except ImportError:
        print("    paquet « prov » absent : relecture par un lecteur tiers non faite (uv run --with prov …)")
        return {**resume, "paquet_prov": "absent"}
    exige(controle["enregistrements"] == total and controle["aller_retour_identique"],
          f"le paquet prov lit {controle['enregistrements']} enregistrements sur {total}")
    (sorties / "dossier.provn").write_text(controle["provn"], encoding="utf-8")
    import prov

    print(f"    paquet prov {prov.__version__} : {total} enregistrements relus, aller-retour identique")
    return {**resume, "paquet_prov": prov.__version__}


def essai_empreintes_et_droits(base: Path) -> None:
    """Ce qui entre dans une empreinte, et qui a le droit de déposer quoi."""
    exige(empreinte({"a": 1, "b": 2}) == empreinte({"b": 2, "a": 1}), "l'ordre des clés ne compte pas")
    exige(empreinte({"x": 1}) != empreinte({"x": 1.0}), "1 et 1.0 : deux empreintes (piège d'un aller-retour JSON)")
    nfc, nfd = (unicodedata.normalize(f, "préserver") for f in ("NFC", "NFD"))
    exige(nfc != nfd and empreinte(nfc) != empreinte(nfd), "deux codages du même mot accentué : deux empreintes")
    refuse(ValueError, lambda: empreinte({"x": float("nan")}), "NaN dans une pièce")
    d = copie(base, "empreintes")
    premiere = d.ranger("fait:horizon", 5)
    time.sleep(0.01)
    exige(premiere == d.ranger("fait:horizon", 5) == d.tete()["fait:horizon"], "la date n'entre pas dans l'empreinte")
    refuse(EcritureInterdite, lambda: d.deposer(P, "fait:horizon", 9, "agent3", d.sommet()), "l'agent 3 écrit un fait")
    refuse(EcritureInterdite, lambda: d.deposer(P, "catalogue", {}, "personne", d.sommet()), "la personne écrit le catalogue")
    refuse(AssertionError, lambda: Dossier(d.racine, TACHES[::-1], DROITS), "graphe de tâches avec cycle ou désordre")


def essai_erreur_outil(base: Path) -> None:
    """Une tâche qui échoue est journalisée, bornée, et rend l'étude « interrompue », jamais « complète »."""
    d = copie(base, "erreur_outil")
    corriger(d, "fait:horizon", 8)

    def panne(e):
        raise RuntimeError("outil indisponible")

    exige(reprendre(d, fonctions={**FONCTIONS, "plan": panne}) == [], "aucune tâche terminée")
    b = d.bilan()
    exige(par_tache(d)[("tache_echouee", "plan")] == 2 and b["etat"] == "interrompue" and list(b["bloquees"]) == ["plan"]
          and set(b["attente"]) == set(TOUTES[3:]), f"deux échecs journalisés, étude interrompue ({b})")
    exige("restitution" not in d.tete(), "interrompue : aucune restitution en vigueur")
    exige(reprendre(d, essais_max=3) == TOUTES[2:] and d.bilan()["etat"] == "complète", "outil réparé : la reprise termine")


def essai_integrite(base: Path) -> None:
    """Une altération du journal ou d'une pièce se voit."""
    d = copie(base, "integrite")
    piece = d.racine / "pieces" / f"{d.tete()['calculs']}.json"
    piece.write_bytes(piece.read_bytes().replace(b"true", b"false"))
    exige(any("pièce" in a for a in d.verifier()), "pièce altérée")
    journal = d._fichier(P)
    lignes = journal.read_bytes().split(b"\n")
    journal.write_bytes(b"\n".join(lignes[:3] + [lignes[3].replace(b'"personne"', b'"agent3"')] + lignes[4:]))
    exige(any("altéré" in a for a in d.verifier()), "événement altéré")
    journal.write_bytes(b"\n".join(lignes[:3] + lignes[4:]))
    exige(any("chaîne rompue" in a for a in d.verifier()), "événement supprimé")


def mesures(base: Path, exemple: Path) -> dict:
    """Lignes de code, taille sur disque, coût de la relecture d'un long journal, coût de l'écriture durable."""
    def taille(racine: Path) -> dict:
        fichiers = [p for p in racine.rglob("*") if p.is_file()]
        return {"evenements_ligne_principale": len(ouvrir(racine).evenements()), "pieces": len(list((racine / "pieces").iterdir())),
                "fichiers": len(fichiers), "octets": sum(p.stat().st_size for p in fichiers)}

    m = {"lignes": {f.name: len(f.read_text(encoding="utf-8").splitlines()) for f in sorted(ICI.glob("*.py"))},
         "dossier_de_base": taille(base), "dossier_exemple": taille(exemple)}
    long = Dossier(base.parent / "long", TACHES, DROITS, durable=False)
    shutil.copytree(base, long.racine, dirs_exist_ok=True)
    debut = time.perf_counter()
    for i in range(200):  # deux cents corrections successives, chacune suivie de la reprise
        corriger(long, "fait:prenom", f"R{i}")
        long.avancer(P, FONCTIONS)
    m["long_journal"] = {"evenements": len(long.evenements()), "construction_s": round(time.perf_counter() - debut, 3)}
    for nom, action in (("lecture_s", long.evenements), ("tete_s", long.tete), ("etats_s", long.etats), ("verifier_s", long.verifier)):
        debut = time.perf_counter()
        action()
        m["long_journal"][nom] = round(time.perf_counter() - debut, 4)
    for durable in (True, False):
        d = Dossier(base.parent / f"durable_{durable}", TACHES, DROITS, durable=durable)
        debut = time.perf_counter()
        for i in range(100):
            corriger(d, "fait:prenom", f"R{i}")
        m[f"cent_depots_{'avec' if durable else 'sans'}_fsync_s"] = round(time.perf_counter() - debut, 3)
    return m


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="dossier_maison_"))
    base, sorties, garde = tmp / "base", ICI / "sorties", {}
    sorties.mkdir(exist_ok=True)
    essais = [
        ("(c) reprise après un arrêt réel, puis question à la personne", lambda: essai_c_reprise_et_question(base)),
        ("    ligne du journal tronquée par une panne", lambda: essai_ligne_tronquee(base)),
        ("(a) invalidation sélective, six champs", lambda: essai_a_invalidation(base)),
        ("(b) variante sur une branche", lambda: essai_b_variante(base)),
        ("(d) écritures concurrentes", lambda: essai_d_concurrence(base)),
        ("(e) retour en vigueur sans recalcul", lambda: essai_e_retour(base)),
        ("(f) erronée contre périmée", lambda: garde.update(f=essai_f_erronee(base))),
        ("(g) préparé, affiché, choisi", lambda: essai_g_affichage(base)),
        ("(h) export PROV-JSON", lambda: garde.update(prov=essai_h_prov(garde["f"], sorties))),
        ("    empreintes et droits d'écriture", lambda: essai_empreintes_et_droits(base)),
        ("    erreur d'outil", lambda: essai_erreur_outil(base)),
        ("    intégrité du journal et des pièces", lambda: essai_integrite(base)),
    ]
    durees, debut_total = {}, time.perf_counter()
    for nom, essai in essais:
        debut, avant = time.perf_counter(), COMPTE["assertions"]
        essai()
        durees[nom.strip()] = round(time.perf_counter() - debut, 3)
        print(f"{nom} : réussi, {COMPTE['assertions'] - avant} assertions, {durees[nom.strip()]} s")
    total = round(time.perf_counter() - debut_total, 3)
    exemple = sorties / "dossier_exemple"
    shutil.rmtree(exemple, ignore_errors=True)
    shutil.copytree(garde["f"].racine, exemple)
    m = {"python": sys.version.split()[0], "assertions": COMPTE["assertions"], "duree_des_essais_s": total, "durees": durees,
         "prov": garde["prov"], **mesures(base, exemple)}
    (sorties / "mesures.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{COMPTE['assertions']} assertions réussies en {total} s (Python {m['python']}).")
    print(json.dumps({k: v for k, v in m.items() if k not in ("durees", "prov")}, ensure_ascii=False, indent=1))
    shutil.rmtree(tmp, ignore_errors=True)


def contre_epreuve_verrou(tours: int = 10) -> None:
    """L'essai (d) prouve-t-il quelque chose ? Même course, avec puis sans le verrou du journal."""
    resultats = {}
    for verrou in (True, False):
        tmp = Path(tempfile.mkdtemp(prefix="dossier_maison_course_"))
        d = ouvrir(tmp / "d")
        d.deposer(P, "donnees", DONNEES, "code", d.sommet())
        environnement = dict(os.environ) if verrou else {**os.environ, "SANS_VERROU": "1"}
        doubles = 0
        for tour in range(tours):
            sommet, quand = d.sommet(), time.time() + 0.8
            lances = [subprocess.Popen([sys.executable, __file__, "--ecrire", str(d.racine), sommet, f"{tour}-{i}", str(quand)],
                                       stdout=subprocess.PIPE, text=True, env=environnement) for i in range(8)]
            doubles += sum(p.communicate()[0].strip() == "accepte" for p in lances) > 1
        ruptures = sum("chaîne rompue" in a for a in d.verifier())
        resultats["avec verrou" if verrou else "sans verrou"] = {"tours": tours, "tours_a_plusieurs_acceptations": doubles,
                                                                 "ruptures_de_chaine_vues": ruptures}
        shutil.rmtree(tmp, ignore_errors=True)
    (ICI / "sorties").mkdir(exist_ok=True)
    (ICI / "sorties" / "contre_epreuve_verrou.json").write_text(json.dumps(resultats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resultats, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--contre-epreuve"]:
        contre_epreuve_verrou()
    elif sys.argv[1:2] == ["--mourir"]:
        mode_mourir(sys.argv[2])
    elif sys.argv[1:2] == ["--ecrire"]:
        mode_ecrire(*sys.argv[2:6])
    else:
        main()
