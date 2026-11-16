"""Analyse en direct : chaque étape part dès que son agent a fini, puis le dossier complet."""
import asyncio
import json

from alphaforge.orchestrateur import analyser
from alphaforge.personas import PERSONAS


def _robert():
    p = PERSONAS["robert"]
    return p["profil"], p["demande"]


def test_chaque_etape_est_publiee_dans_l_ordre_et_une_seule_fois():
    recues = []
    dossier = analyser(*_robert(), sur_etape=recues.append)
    assert [e["etape"]["agent"] for e in recues] == [t["agent"] for t in dossier["trace"]]
    sceptique = next(e for e in recues if e["etape"]["agent"] == "Sceptique")
    assert sceptique["objections"] and all(o["issue"] for o in sceptique["objections"])
    assert {f["id"] for f in recues[-1]["faits"]} == {f["id"] for f in dossier["faits"]}


def test_sans_rappel_le_dossier_est_identique():
    a, b = analyser(*_robert()), analyser(*_robert(), sur_etape=lambda e: None)
    assert a["verdict"] == b["verdict"] and len(a["trace"]) == len(b["trace"])


def _lire_flux(profil, demande):
    import api
    rep = api.analyse_flux(api.Requete(profil=profil, demande=demande))

    async def lire():
        return [c if isinstance(c, str) else c.decode() async for c in rep.body_iterator]

    return [json.loads(ligne) for morceau in asyncio.run(lire()) for ligne in morceau.splitlines() if ligne]


def test_le_flux_envoie_les_etapes_puis_le_dossier():
    messages = _lire_flux(*_robert())
    assert [m["type"] for m in messages] == ["etape"] * (len(messages) - 1) + ["dossier"]
    assert len(messages) - 1 == len(messages[-1]["dossier"]["trace"])


def test_un_actif_inconnu_arrive_comme_erreur_dans_le_flux():
    profil, demande = _robert()
    messages = _lire_flux(profil, {**demande, "ticker": "FOO", "texte": ""})
    assert messages[-1]["type"] == "erreur" and messages[-1]["statut"] == 422
