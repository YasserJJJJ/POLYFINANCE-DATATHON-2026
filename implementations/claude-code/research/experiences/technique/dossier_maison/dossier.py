"""Dossier maison : journal en ajout seul, pièces rangées par empreinte, tête déduite.

Expérience technique du 15 novembre 2026 (cadre de conception, sections 2, 3 et 7 ; contrat
02-dossier). Ce n'est pas le produit. Bibliothèque standard seulement : aucun appel de modèle,
aucune ressource AWS, aucun accès au réseau.

Vocabulaire
- pièce     : contenu immuable {type, corps}, rangé sous le SHA-256 de sa forme canonique.
- événement : ligne du journal d'une branche. Il porte l'empreinte du précédent (« prolonge »),
              l'auteur et la date. Les mentions d'une pièce (auteur, activité, entrées, date)
              vivent ici, pas dans son empreinte : sinon rien ne pourrait revenir en vigueur.
- sommet    : empreinte du dernier événement d'une branche ; une écriture nomme celui qu'elle prolonge.
- tête      : emplacement -> empreinte de la pièce en vigueur. Elle se recalcule, elle ne s'écrit pas.
- tâche     : fonction pure sur des emplacements déclarés. Sa clé est l'empreinte de
              (nom, version, empreintes des entrées). Une clé déjà au journal n'est pas refaite.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PRINCIPALE = "principale"


class TeteDepassee(Exception):
    """L'événement nomme un sommet qui n'est plus le dernier de la branche : écriture refusée."""


class EcritureInterdite(Exception):
    """L'auteur n'a pas ce droit, ou l'événement cite une pièce ou un affichage inconnus."""


def canon(objet) -> bytes:
    """Forme canonique : clés triées, aucun espace, UTF-8, ni NaN ni infini."""
    return json.dumps(objet, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def empreinte(objet) -> str:
    return hashlib.sha256(canon(objet)).hexdigest()


@dataclass(frozen=True)
class Tache:
    nom: str
    auteur: str  # rôle (agent0 à agent3, contradicteur) ou « code »
    entrees: tuple[str, ...]  # emplacements lus : déclarés, jamais devinés
    sortie: str  # emplacement écrit
    version: str = "1"  # version du code ou de la consigne ; elle entre dans la clé

    def cle(self, tete: dict[str, str]) -> str:
        return empreinte({"tache": self.nom, "version": self.version, "entrees": {x: tete[x] for x in self.entrees}})


class Dossier:
    def __init__(self, racine, taches: list[Tache], droits: dict[str, tuple[str, ...]], durable: bool = True):
        """taches : dans l'ordre des dépendances. droits : auteur -> préfixes d'emplacements qu'il dépose."""
        self.racine, self.taches, self.droits, self.durable = Path(racine), list(taches), droits, durable
        sorties = [t.sortie for t in self.taches]
        for i, t in enumerate(self.taches):  # ni cycle ni lecture d'une sortie produite plus tard
            assert not set(t.entrees) & set(sorties[i:]), f"{t.nom} lit une sortie qui ne la précède pas"
        (self.racine / "pieces").mkdir(parents=True, exist_ok=True)
        (self.racine / "journal").mkdir(exist_ok=True)

    # ------------------------------------------------------------------ pièces
    def ranger(self, type_: str, corps) -> str:
        """Range une pièce sous l'empreinte de son contenu. Une pièce déjà rangée n'est jamais réécrite."""
        contenu = canon({"type": type_, "corps": corps})
        h = hashlib.sha256(contenu).hexdigest()
        chemin = self.racine / "pieces" / f"{h}.json"
        if not chemin.exists():
            fd, provisoire = tempfile.mkstemp(dir=chemin.parent, suffix=".tmp")
            with os.fdopen(fd, "wb") as f:
                f.write(contenu)
                self._vider(f)
            os.replace(provisoire, chemin)  # apparition atomique : jamais de pièce à moitié écrite
        return h

    def lire(self, h: str) -> dict:
        octets = (self.racine / "pieces" / f"{h}.json").read_bytes()
        if hashlib.sha256(octets).hexdigest() != h:
            raise ValueError("contenu différent de son empreinte")
        return json.loads(octets)

    def _vider(self, f) -> None:
        f.flush()
        if self.durable:
            os.fsync(f.fileno())

    # ----------------------------------------------------------------- journal
    def _fichier(self, branche: str) -> Path:
        return self.racine / "journal" / f"{branche}.jsonl"

    def _propres(self, branche: str) -> list[dict]:
        """Événements du fichier de la branche. Une ligne tronquée par une panne n'est pas un événement."""
        evenements = []
        if self._fichier(branche).exists():
            for ligne in self._fichier(branche).read_bytes().split(b"\n"):
                try:
                    evenements.append(json.loads(ligne))
                except ValueError:
                    continue
        return evenements

    def evenements(self, branche: str = PRINCIPALE) -> list[dict]:
        """Lignée d'une branche : les événements du parent jusqu'à la bifurcation, puis les siens."""
        propres = self._propres(branche)
        if propres and propres[0]["type"] == "branche":
            parent = self.evenements(propres[0]["parent"])
            coupe = next(i for i, e in enumerate(parent) if e["empreinte"] == propres[0]["prolonge"])
            return parent[: coupe + 1] + propres
        return propres

    def sommet(self, branche: str = PRINCIPALE) -> str | None:
        evenements = self.evenements(branche)
        return evenements[-1]["empreinte"] if evenements else None

    def ajouter(self, branche: str, type_: str, auteur: str, prolonge: str | None, **charge) -> dict:
        """Ajoute un événement s'il prolonge le sommet actuel de la branche ; sinon refuse, sans rien écrire."""
        with open(self._fichier(branche), "ab+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)  # une seule écriture à la fois par branche, entre processus
            propres = self._propres(branche)
            sommet = propres[-1]["empreinte"] if propres else None
            if (propres or type_ != "branche") and prolonge != sommet:
                raise TeteDepassee(f"{branche} : sommet {str(sommet)[:12]}, écriture préparée sur {str(prolonge)[:12]}")
            evenement = {"n": len(propres), "branche": branche, "type": type_, "auteur": auteur, "prolonge": prolonge,
                         "date": datetime.now(timezone.utc).isoformat(), **charge}  # le greffier seul date
            evenement["empreinte"] = empreinte(evenement)
            f.seek(0, os.SEEK_END)
            if f.tell():
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b"\n":  # reste d'une écriture interrompue : on repart sur une ligne neuve
                    f.write(b"\n")
            f.write(canon(evenement) + b"\n")
            self._vider(f)
        return evenement

    def _rejouer(self, branche: str, type_: str, auteur: str, **charge) -> dict:
        """Un fait d'exécution vaut quelle que soit la tête : refusé, il est rejoué sur le sommet suivant."""
        for _ in range(50):
            try:
                return self.ajouter(branche, type_, auteur, self.sommet(branche), **charge)
            except TeteDepassee:
                continue
        raise TeteDepassee(f"{branche} : cinquante refus de suite")

    # ------------------------------------------------- écritures des personnes
    def deposer(self, branche: str, emplacement: str, corps, auteur: str, prolonge: str | None, **mentions) -> dict:
        """Dépôt d'une pièce source (fait déclaré, données, catalogue) par qui en a le droit."""
        if not any(emplacement.startswith(p) for p in self.droits.get(auteur, ())):
            raise EcritureInterdite(f"{auteur} n'a pas le droit d'écrire {emplacement}")
        piece = self.ranger(emplacement, corps)
        remplace = self.tete(branche).get(emplacement)
        return self.ajouter(branche, "depot", auteur, prolonge, emplacement=emplacement, piece=piece,
                            remplace=remplace, **mentions)

    def ouvrir_branche(self, nom: str, parent: str = PRINCIPALE, depuis: str | None = None) -> dict:
        """Variante : une branche qui part d'un événement du parent et n'écrit rien chez lui."""
        depuis = depuis or self.sommet(parent)
        if self._propres(nom) or depuis not in {e["empreinte"] for e in self.evenements(parent)}:
            raise EcritureInterdite(f"branche {nom} déjà ouverte, ou point de départ inconnu")
        return self.ajouter(nom, "branche", "personne", depuis, parent=parent)

    def retirer(self, branche: str, piece: str, auteur: str, motif: str, prolonge: str) -> dict:
        """Retrait d'une pièce erronée : irréversible, motivé. La pièce reste lisible."""
        if piece not in {e.get("piece") for e in self.evenements(branche)}:
            raise EcritureInterdite("pièce inconnue de cette branche")
        return self.ajouter(branche, "retrait", auteur, prolonge, piece=piece, motif=motif)

    def afficher(self, branche: str, piece: str, prolonge: str, **mentions) -> dict:
        """L'interface enregistre ce qui a réellement été montré. Préparer n'est pas afficher."""
        connues = {e["piece"] for e in self.evenements(branche) if e.get("emplacement") == "restitution"}
        if piece not in connues:
            raise EcritureInterdite("on n'affiche qu'une restitution préparée dans cette branche")
        return self.ajouter(branche, "affichage", "interface", prolonge, piece=piece, **mentions)

    def reagir(self, branche: str, affichage: str, nature: str, texte: str, prolonge: str) -> dict:
        """Réaction de la personne. Elle se rattache à un affichage enregistré, jamais à une préparation."""
        if affichage not in {e["empreinte"] for e in self.evenements(branche) if e["type"] == "affichage"}:
            raise EcritureInterdite("une réaction cite un affichage enregistré")
        return self.ajouter(branche, "reaction", "personne", prolonge, affichage=affichage, nature=nature, texte=texte)

    # ------------------------------------------------------------ déductions
    def tete(self, branche: str = PRINCIPALE, evenements: list[dict] | None = None) -> dict[str, str]:
        """Ce qui est en vigueur : les derniers dépôts, puis toute sortie dont la clé de tâche est au journal."""
        evenements = self.evenements(branche) if evenements is None else evenements
        tete, produits, retirees = {}, {}, set()
        for e in evenements:
            if e["type"] == "depot":
                tete[e["emplacement"]] = e["piece"]
            elif e["type"] == "tache_terminee":
                produits[e["cle"]] = e["piece"]
            elif e["type"] == "retrait":
                retirees.add(e["piece"])
        tete = {k: h for k, h in tete.items() if h not in retirees}
        for t in self.taches:
            if all(x in tete for x in t.entrees):
                piece = produits.get(t.cle(tete))
                if piece and piece not in retirees:
                    tete[t.sortie] = piece
        return tete

    def etats(self, branche: str = PRINCIPALE) -> dict[str, dict]:
        """État de chaque pièce par rapport à la tête, avec l'événement qui l'a fait changer."""
        evenements, etats, avant = self.evenements(branche), {}, {}
        for i, e in enumerate(evenements):
            apres = self.tete(branche, evenements[: i + 1])
            if e["type"] in ("depot", "tache_terminee"):
                etats.setdefault(e["piece"], {"emplacement": e["emplacement"], "source": e["type"] == "depot",
                                              "etat": "périmée", "cause": e["empreinte"]})
            for h in set(avant.values()) - set(apres.values()):  # sorties de la tête à cet événement
                etats[h].update(etat="remplacée" if etats[h]["source"] else "périmée", cause=e["empreinte"])
            for h in apres.values():
                etats[h].update(etat="en vigueur", cause=None)
            if e["type"] == "retrait":
                etats[e["piece"]].update(etat="erronée", cause=e["empreinte"], motif=e["motif"])
            avant = apres
        return etats

    def ascendance(self, piece: str, evenements: list[dict]) -> set[str]:
        """Toutes les pièces dont celle-ci dérive, d'après les entrées enregistrées par le greffier."""
        parents: dict[str, set[str]] = {}
        for e in evenements:
            if e["type"] == "tache_terminee":
                parents.setdefault(e["piece"], set()).update(e["entrees"].values())
        vues, pile = set(), [piece]
        while pile:
            for p in parents.get(pile.pop(), ()):
                if p not in vues:
                    vues.add(p)
                    pile.append(p)
        return vues

    def affichages_a_signaler(self, branche: str = PRINCIPALE) -> list[dict]:
        """Affichages dont la restitution dérive d'une pièce retirée : la personne est à prévenir."""
        evenements = self.evenements(branche)
        retirees = {e["piece"] for e in evenements if e["type"] == "retrait"}
        return [e for e in evenements if e["type"] == "affichage"
                and retirees & (self.ascendance(e["piece"], evenements) | {e["piece"]})]

    # --------------------------------------------------------------- greffier
    def bilan(self, branche: str = PRINCIPALE, essais_max: int = 2) -> dict:
        """État de l'étude. « Interrompue » et « en attente » ne sont jamais des conclusions."""
        evenements = self.evenements(branche)
        tete = self.tete(branche, evenements)
        echecs = Counter(e["cle"] for e in evenements if e["type"] == "tache_echouee")
        closes = {e["cle"] for e in evenements if e["type"] == "tache_terminee"}
        sorties = {t.sortie for t in self.taches}
        pretes, attente, bloquees = [], {}, {}
        for t in self.taches:
            manquent = [x for x in t.entrees if x not in tete]
            if t.sortie in tete:
                continue
            if manquent:
                attente[t.nom] = manquent
            elif t.cle(tete) in closes:  # même clé, même résultat : il a été retiré, la tâche doit changer
                bloquees[t.nom] = "résultat retiré comme erroné ; la tâche doit changer de version"
            elif echecs[t.cle(tete)] >= essais_max:
                bloquees[t.nom] = f"{echecs[t.cle(tete)]} échecs"
            else:
                pretes.append(t)
        questions = sorted({x for m in attente.values() for x in m if x not in sorties})
        etat = ("à poursuivre" if pretes else "interrompue" if bloquees
                else "en attente de la personne" if questions else "complète")
        return {"etat": etat, "pretes": pretes, "attente": attente, "bloquees": bloquees, "questions": questions}

    def avancer(self, branche: str, fonctions: dict, essais_max: int = 2) -> list[str]:
        """Lance chaque tâche prête, range sa pièce, journalise. Rend les tâches réellement exécutées."""
        faites = []
        while True:
            pretes = self.bilan(branche, essais_max)["pretes"]
            if not pretes:
                return faites
            t, tete = pretes[0], self.tete(branche)
            cle, entrees = t.cle(tete), {x: tete[x] for x in t.entrees}
            self._rejouer(branche, "tache_lancee", "greffier", tache=t.nom, cle=cle)
            try:
                corps = fonctions[t.nom]({x: self.lire(h)["corps"] for x, h in entrees.items()})
                piece = self.ranger(t.sortie, corps)
            except Exception as erreur:  # erreur d'outil : journalisée, bornée, jamais une conclusion
                self._rejouer(branche, "tache_echouee", "greffier", tache=t.nom, cle=cle, erreur=repr(erreur))
                continue
            self._rejouer(branche, "tache_terminee", t.auteur, tache=t.nom, version=t.version, cle=cle,
                          entrees=entrees, emplacement=t.sortie, piece=piece)
            faites.append(t.nom)

    # -------------------------------------------------------------- intégrité
    def verifier(self, branche: str = PRINCIPALE) -> list[str]:
        """Chaîne des empreintes du journal, lignes illisibles, pièces citées : liste des anomalies."""
        anomalies, precedent = [], None
        for i, ligne in enumerate(l for l in self._fichier(branche).read_bytes().split(b"\n") if l):
            try:
                e = json.loads(ligne)
            except ValueError:
                anomalies.append(f"ligne {i + 1} illisible")
                continue
            if empreinte({k: v for k, v in e.items() if k != "empreinte"}) != e["empreinte"]:
                anomalies.append(f"événement {e['n']} altéré")
            if precedent is not None and e["prolonge"] != precedent:
                anomalies.append(f"événement {e['n']} : chaîne rompue")
            precedent = e["empreinte"]
            if "piece" in e:
                try:
                    self.lire(e["piece"])
                except (OSError, ValueError) as erreur:
                    anomalies.append(f"pièce {e['piece'][:12]} : {erreur}")
        return anomalies
