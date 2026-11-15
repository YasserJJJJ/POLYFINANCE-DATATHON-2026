"""Accès à Bedrock simulé (aucun appel réseau) : délais bornés, repli correct, indicateur honnête."""
import sys
import types

import pytest

from alphaforge import llm


@pytest.fixture
def faux_boto3(monkeypatch):
    """Remplace boto3 par un faux module ; renvoie le journal des clients créés."""
    journal = {"configs": [], "erreur": None, "sts_erreur": None}

    class Client:
        def __init__(self, service, **kw):
            self.service = service
            journal["configs"].append((service, kw.get("config")))

        def converse(self, **kw):
            raise journal["erreur"]

        def get_caller_identity(self):
            if journal["sts_erreur"]:
                raise journal["sts_erreur"]
            return {"Account": "000000000000"}

    monkeypatch.setitem(sys.modules, "boto3", types.SimpleNamespace(client=lambda s, **kw: Client(s, **kw)))
    monkeypatch.setenv("ALPHAFORGE_LLM", "auto")
    monkeypatch.setattr(llm, "_etat", {"indisponible": None})
    monkeypatch.setattr(llm, "_client", {})
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
