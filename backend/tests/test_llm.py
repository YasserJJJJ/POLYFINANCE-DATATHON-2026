"""Accès à Bedrock simulé (aucun appel réseau) : délais bornés, repli correct, indicateur honnête."""
import sys
import types
import copy
import json
import threading
from contextvars import ContextVar

import pytest

from alphaforge import llm


@pytest.fixture
def faux_boto3(monkeypatch):
    """Remplace boto3 par un faux module ; renvoie le journal des clients créés."""
    journal = {"configs": [], "erreur": None, "sts_erreur": None, "dernier_appel": None,
               "erreurs_modeles": {}, "hook": None, "appels": [],
               "reponse": {"stopReason": "end_turn", "output": {"message": {"content": [{"text": "ok"}]}}}}

    class Client:
        def __init__(self, service, **kw):
            self.service = service
            journal["configs"].append((service, kw.get("config")))

        def converse(self, **kw):
            journal["dernier_appel"] = kw
            journal["appels"].append(kw)
            erreur = journal["erreurs_modeles"].get(kw["modelId"]) or journal["erreur"]
            if erreur:
                raise erreur
            if journal["hook"]:
                return journal["hook"](kw)
            reponse = copy.deepcopy(journal["reponse"])
            reponse.setdefault("ResponseMetadata", {"RequestId": f"req-{len(journal['appels'])}"})
            reponse.setdefault("usage", {"inputTokens": 17, "outputTokens": 3})
            reponse.setdefault("metrics", {"latencyMs": 42})
            return reponse

        def get_caller_identity(self):
            if journal["sts_erreur"]:
                raise journal["sts_erreur"]
            return {"Account": "000000000000"}

    monkeypatch.setitem(sys.modules, "boto3", types.SimpleNamespace(
        Session=lambda **kw: types.SimpleNamespace(client=lambda s, **options: Client(s, **options))))
    monkeypatch.setenv("ALPHAFORGE_LLM", "auto")
    monkeypatch.setattr(llm, "_etat", {"indisponible": None})
    monkeypatch.setattr(llm, "_client", {})
    monkeypatch.setattr(llm, "_journal", ContextVar("test_appels", default=()))
    return journal


def _erreur(nom):
    return type(nom, (Exception,), {})("simulée")


def test_delais_bornes_sur_le_client_bedrock(faux_boto3):
    faux_boto3["erreur"] = _erreur("ThrottlingException")
    with pytest.raises(llm.LLMIndisponible):
        llm.appeler("s", "m")
    service, config = faux_boto3["configs"][0]
    assert service == "bedrock-runtime" and config is not None
    assert config.connect_timeout == 5 and config.read_timeout == 40 and config.retries["max_attempts"] == 2


def test_erreur_passagere_ne_coupe_pas_les_agents_mais_une_cle_expiree_si(faux_boto3):
    faux_boto3["erreur"] = _erreur("ThrottlingException")
    with pytest.raises(llm.LLMIndisponible):
        llm.appeler("s", "m")
    assert llm.actif()
    faux_boto3["erreur"] = _erreur("ExpiredTokenException")
    with pytest.raises(llm.LLMIndisponible):
        llm.appeler("s", "m")
    assert not llm.actif() and "ExpiredTokenException" in llm.raison_indisponible()


def test_indicateur_n_annonce_pas_bedrock_sans_identifiants_valides(faux_boto3):
    faux_boto3["sts_erreur"] = _erreur("NoCredentialsError")
    assert llm.acces_verifie() is False          # avant : sante() disait llm=True avant tout appel
    assert "NoCredentialsError" in llm.raison_indisponible()


def test_indicateur_dit_bedrock_quand_les_identifiants_sont_valides(faux_boto3):
    assert llm.acces_verifie() is True


# --- Bedrock Guardrails (préparé, activé seulement si ALPHAFORGE_GUARDRAIL_ID est défini) ---
def test_sans_guardrail_configure_aucun_parametre_guardrail_envoye(faux_boto3, monkeypatch):
    monkeypatch.delenv("ALPHAFORGE_GUARDRAIL_ID", raising=False)
    assert llm.appeler("s", "m", source_ancrage="dossier") == "ok"
    assert "guardrailConfig" not in faux_boto3["dernier_appel"]


def test_guardrail_configure_envoie_la_source_d_ancrage_et_bloque(faux_boto3, monkeypatch):
    monkeypatch.setenv("ALPHAFORGE_GUARDRAIL_ID", "gr-test")
    llm.appeler("s", "question", source_ancrage="le dossier")
    appel = faux_boto3["dernier_appel"]
    assert appel["guardrailConfig"]["guardrailIdentifier"] == "gr-test"
    qualifs = [c["guardContent"]["text"]["qualifiers"] for c in appel["messages"][0]["content"] if "guardContent" in c]
    assert ["grounding_source"] in qualifs and ["query"] in qualifs
    faux_boto3["reponse"] = {"stopReason": "guardrail_intervened",
                             "output": {"message": {"content": [{"text": "Réponse bloquée."}]}}}
    with pytest.raises(llm.LLMIndisponible, match="guardrail"):
        llm.appeler("s", "question", source_ancrage="le dossier")
    assert llm.actif()      # un blocage n'est pas une panne d'accès : les autres agents continuent


def test_guardrail_question_courte_contenu_complet_et_perimetre_redacteur(faux_boto3, monkeypatch):
    monkeypatch.setenv("ALPHAFORGE_GUARDRAIL_ID", "gr-test")
    llm.appeler("s", "catalogue", llm.MODELE_LEGER)
    assert "guardrailConfig" not in faux_boto3["dernier_appel"]
    llm.appeler("s", "vérifications du Sceptique")
    assert "guardrailConfig" not in faux_boto3["dernier_appel"]
    dossier = "faits " * 1500
    llm.appeler("s", dossier, source_ancrage=dossier)
    blocs = [c["guardContent"]["text"] for c in faux_boto3["dernier_appel"]["messages"][0]["content"]]
    assert len(next(b["text"] for b in blocs if b["qualifiers"] == ["query"])) <= 1000
    assert next(b["text"] for b in blocs if b["qualifiers"] == ["guard_content"]) == dossier
    assert next(b["text"] for b in blocs if b["qualifiers"] == ["grounding_source"]) == dossier


def test_preuve_k6_metadonnees_seulement_et_agent_facultatif(faux_boto3):
    llm.appeler("SYSTEME CONFIDENTIEL", "MESSAGE CONFIDENTIEL", agent="Vérification")
    assert llm.journal_appels() == [{
        "agent": "Vérification", "modele": llm.MODELE_PRINCIPAL, "request_id": "req-1",
        "stop_reason": "end_turn", "jetons_entree": 17, "jetons_sortie": 3,
        "latence_ms": 42, "garde_fou": "absent",
    }]
    assert llm.journal_appels() == []  # livraison finale sans contamination de l'analyse suivante


def test_refus_guardrail_et_json_inutilisable_restent_dans_le_journal(faux_boto3, monkeypatch):
    monkeypatch.setenv("ALPHAFORGE_GUARDRAIL_ID", "gr-test")
    faux_boto3["reponse"]["stopReason"] = "guardrail_intervened"
    with pytest.raises(llm.LLMIndisponible):
        llm.appeler_json("s", "m", source_ancrage="faits")
    faux_boto3["reponse"]["stopReason"] = "end_turn"
    with pytest.raises(ValueError):
        llm.appeler_json("s", "m", source_ancrage="faits")  # texte « ok », pas un JSON
    journal = llm.journal_appels()
    assert len(journal) == 2 and [e["request_id"] for e in journal] == ["req-1", "req-2"]
    assert [e["garde_fou"] for e in journal] == ["bloque", "configure"]
    assert all(e["agent"] == "Rédacteur" for e in journal)


def test_convention_des_agents_du_socle(faux_boto3):
    llm.appeler("s", "m", llm.MODELE_LEGER)
    llm.appeler("s", "m")
    llm.appeler("s", "m", source_ancrage="source")
    assert [e["agent"] for e in llm.journal_appels()] == ["Profileur", "Sceptique", "Rédacteur"]


def test_erreur_acces_un_modele_ne_coupe_pas_l_autre_et_reprise(faux_boto3, monkeypatch):
    horloge = [100.]
    monkeypatch.setattr(llm, "_maintenant", lambda: horloge[0])
    monkeypatch.setenv("ALPHAFORGE_REESSAI_SECONDES", "7")
    faux_boto3["erreurs_modeles"][llm.MODELE_PRINCIPAL] = _erreur("AccessDeniedException")
    with pytest.raises(llm.LLMIndisponible):
        llm.appeler("s", "m")
    assert llm.actif() and not llm.actif(llm.MODELE_PRINCIPAL)
    assert llm.appeler("s", "m", llm.MODELE_LEGER) == "ok"
    faux_boto3["erreurs_modeles"].clear()
    with pytest.raises(llm.LLMIndisponible):
        llm.appeler("s", "m")  # aucun nouvel appel avant l'échéance
    assert len(faux_boto3["appels"]) == 2
    horloge[0] += 7
    assert llm.appeler("s", "m") == "ok"
    journal = llm.journal_appels()
    assert len(journal) == 3 and journal[0]["request_id"] is None
    assert journal[0]["stop_reason"] == "erreur:AccessDeniedException"


def test_identifiants_renouveles_sans_redemarrage_et_sts_non_collant(faux_boto3, monkeypatch):
    horloge = [100.]
    monkeypatch.setattr(llm, "_maintenant", lambda: horloge[0])
    monkeypatch.setenv("ALPHAFORGE_REESSAI_SECONDES", "5")
    faux_boto3["sts_erreur"] = _erreur("NoCredentialsError")
    assert not llm.acces_verifie()
    faux_boto3["sts_erreur"] = None
    assert not llm.acces_verifie()
    horloge[0] += 5
    assert llm.acces_verifie()
    faux_boto3["erreur"] = _erreur("ExpiredTokenException")
    with pytest.raises(llm.LLMIndisponible):
        llm.appeler("s", "m")
    assert not llm.actif()
    faux_boto3["erreur"] = None
    horloge[0] += 5
    assert llm.appeler("s", "m") == "ok"
    assert len([c for c in faux_boto3["configs"] if c[0] == "bedrock-runtime"]) == 2


def test_portee_abandonnee_ne_pollue_pas_la_suivante(faux_boto3):
    with pytest.raises(RuntimeError):
        with llm.portee_analyse():
            llm.appeler("s", "m")
            raise RuntimeError("analyse interrompue")
    with llm.portee_analyse():
        assert llm.journal_appels() == []


def test_hors_ligne_sans_import_boto3_et_reference_inchangee(monkeypatch):
    import builtins
    from pathlib import Path
    from alphaforge.orchestrateur import analyser
    from alphaforge.personas import PERSONAS
    from test_reference_personas import sans_variations
    original = builtins.__import__
    def sans_sdk(nom, *args, **kwargs):
        assert not nom.startswith(("boto3", "botocore")), nom
        return original(nom, *args, **kwargs)
    monkeypatch.setenv("ALPHAFORGE_LLM", "off")
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.setattr(builtins, "__import__", sans_sdk)
    p = PERSONAS["robert"]
    obtenu = analyser(p["profil"], p["demande"])
    attendu = json.loads((Path(__file__).with_name("reference") / "robert.json").read_text(encoding="utf-8"))
    assert sans_variations(obtenu) == sans_variations(attendu)
    assert obtenu["appels_modele"] == [] and not llm.acces_verifie()


def test_deux_analyses_http_en_flux_concurrentes_isolent_les_appels(faux_boto3):
    from concurrent.futures import ThreadPoolExecutor
    import socket
    import time
    import urllib.request
    import uvicorn
    from api import app
    from alphaforge.personas import PERSONAS
    barriere = threading.Barrier(2)
    numeros = {}
    verrou = threading.Lock()
    def converse(_kw):
        identite = threading.get_ident()
        with verrou:
            numeros[identite] = numeros.get(identite, 0) + 1
            n = numeros[identite]
        if n == 1:
            barriere.wait(timeout=10)
        return {"ResponseMetadata": {"RequestId": f"{identite}:{n}"}, "stopReason": "end_turn",
                "usage": {"inputTokens": 1, "outputTokens": 1}, "metrics": {"latencyMs": 1},
                "output": {"message": {"content": [{"text": "{}"}]}}}
    faux_boto3["hook"] = converse
    socket_serveur = socket.socket()
    socket_serveur.bind(("127.0.0.1", 0))
    port = socket_serveur.getsockname()[1]
    serveur = uvicorn.Server(uvicorn.Config(app, log_level="error", lifespan="off"))
    fil = threading.Thread(target=lambda: serveur.run(sockets=[socket_serveur]), daemon=True)
    fil.start()
    def requete(nom):
        entree = PERSONAS[nom]
        corps = json.dumps({"profil": entree["profil"], "demande": entree["demande"]}).encode()
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/analyse/flux", data=corps,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as reponse:
            assert reponse.status == 200
            lignes = [json.loads(ligne) for ligne in reponse]
            return next(l["dossier"] for l in lignes if l["type"] == "dossier")
    try:
        echeance = time.monotonic() + 5
        while not serveur.started and time.monotonic() < echeance:
            time.sleep(0.01)
        assert serveur.started
        with ThreadPoolExecutor(max_workers=2) as pool:
            dossiers = list(pool.map(requete, ("robert", "amira")))
    finally:
        serveur.should_exit = True
        fil.join(timeout=5)
        socket_serveur.close()
    assert not fil.is_alive()
    groupes = [{e["request_id"].split(":")[0] for e in d["appels_modele"]} for d in dossiers]
    assert all(len(g) == 1 for g in groupes) and groupes[0].isdisjoint(groupes[1])
    for d in dossiers:
        assert len(d["appels_modele"]) >= 3  # y compris les essais de rédaction refusés
        assert any("refusé" in ligne for ligne in d["texte"]["controle"])
        for trace in d["trace"]:
            assert all(d["appels_modele"][i]["agent"] == trace["agent"] for i in trace["appels_modele"])
