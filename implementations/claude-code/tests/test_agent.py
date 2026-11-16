"""Boucle d'agent testée avec un client Bedrock simulé (aucun appel AWS)."""

import copy

from datathon2026 import tools as T
from datathon2026.agent import BedrockAgent


class FakeBedrock:
    """Rejoue des réponses Converse scriptées et garde les messages reçus."""

    def __init__(self, turns):
        self.turns, self.calls = list(turns), []

    def converse(self, **kw):
        self.calls.append(copy.deepcopy(kw))  # la boucle continue de modifier la liste de messages
        content = self.turns.pop(0)
        stop = "tool_use" if any("toolUse" in b for b in content) else "end_turn"
        return {"output": {"message": {"role": "assistant", "content": content}}, "stopReason": stop,
                "usage": {"inputTokens": 10, "outputTokens": 5}, "ResponseMetadata": {"RequestId": f"req-{len(self.calls)}"}}


def use(i, name, inp):
    return {"toolUse": {"toolUseId": f"t{i}", "name": name, "input": inp}}


def test_agent_loop_runs_tools_rejects_handwritten_number_then_accepts():
    sc = T.load_scenarios()["robert"]
    bad = {"titre": "t", "resume": "TSLA a perdu 70 %.", "affirmations": [{"section": "constat", "texte": "Pire baisse {{R-0003}}."}]}
    good = {"titre": "t", "resume": "TSLA a perdu jusqu'à {{R-0003}}.", "affirmations": [{"section": "constat", "texte": "Pire baisse {{R-0003}}."}]}
    fake = FakeBedrock([
        [use(1, "metriques_actif", {"ticker": "TSLA"})],
        [use(2, "soumettre_dossier", bad)],
        [use(3, "soumettre_dossier", good)],
    ])
    agent = BedrockAgent(client=fake, model="test-model", region="test-region")
    d = agent.run("robert-tsla", sc)
    assert d.verification()["ok"]
    assert [r["requestId"] for r in d.aws["appels"]] == ["req-1", "req-2", "req-3"]
    assert d.aws["corrections_demandees"] == 1
    # le vérificateur a renvoyé le problème à l'agent
    rejected = fake.calls[2]["messages"][-1]["content"][0]["toolResult"]
    assert rejected["status"] == "error" and "nombre non relié" in str(rejected["content"])
    assert d.trace[0]["outil"] == "asset_metrics"


def test_tool_error_is_returned_not_raised():
    sc = T.load_scenarios()["robert"]
    fake = FakeBedrock([
        [use(1, "metriques_actif", {"ticker": "INCONNU"})],
        [use(2, "soumettre_dossier", {"titre": "t", "resume": "", "affirmations": [{"section": "cadre", "texte": "Simulation."}]})],
    ])
    d = BedrockAgent(client=fake, model="m", region="r").run("robert-tsla", sc)
    assert "erreur" in d.trace[0]
    assert fake.calls[1]["messages"][-1]["content"][0]["toolResult"]["status"] == "error"


def test_agent_presentation_is_checked_then_rendered():
    from datathon2026 import report

    sc = T.load_scenarios()["robert"]
    sub = {"titre": "t", "resume": "Pire baisse de TSLA : {{R-0003}}.",
           "affirmations": [{"section": "constat", "texte": "Pire baisse {{R-0003}}, contre {{R-0014}} pour le portefeuille."}],
           "chiffres_cles": [{"libelle": "Pire baisse de TSLA", "valeur": "R-0003"}],
           "tableau": {"titre": "Options", "colonnes": ["Volatilité annualisée", "Pire baisse"],
                       "lignes": [{"nom": "TSLA", "cellules": ["R-0002", "R-0003"]}, {"nom": "Actuel", "cellules": ["R-0013"]}]},
           "graphique": {"type": "baisses", "series": ["TSLA", "Actuel"], "mise_en_evidence": "TSLA"}}
    bad = dict(sub, resume="TSLA dépasse tout : {{R-0003}}.", chiffres_cles=[{"libelle": "Pire baisse", "valeur": "R-0999"}])
    fake = FakeBedrock([
        [use(1, "metriques_actif", {"ticker": "TSLA"}), use(2, "metriques_portefeuille", {"nom": "Actuel", "poids": sc["portefeuille_actuel"]})],
        [use(3, "soumettre_dossier", bad)],
        [use(4, "soumettre_dossier", sub)],
    ])
    d = BedrockAgent(client=fake, model="m", region="r").run("robert-agent", sc)
    rejected = str(fake.calls[2]["messages"][-1]["content"][0]["toolResult"]["content"])
    assert "R-0999" in rejected and "comparaison écrite à la main" in rejected
    out = d.to_dict()
    assert out["verification"]["ok"] and d.aws["corrections_demandees"] == 1
    assert [h["valeur"] for h in out["chiffres_cles"]] == ["R-0003"]
    assert out["tableaux"][0]["lignes"][1]["cellules"] == ["R-0013", None]  # ligne complétée à la largeur du tableau
    assert list(out["graphiques"][0]["series"]) == ["TSLA", "Actuel"]
    page = report.render(out)
    assert "Graphique 1" in page and 'class="bad"' not in page


def test_agent_exposes_data_provenance_tool():
    sc = T.load_scenarios()["amira"]
    fake = FakeBedrock([
        [use(1, "sources_donnees", {})],
        [use(2, "soumettre_dossier", {"titre": "t", "resume": "", "affirmations": [
            {"section": "limite", "texte": "{{D-0006.label}} : {{D-0006}}. Échantillon : {{D-0005}}."}]})],
    ])
    d = BedrockAgent(client=fake, model="m", region="r").run("amira-agent", sc)
    assert d.verification()["ok"] and d.trace[0]["outil"] == "data_manifest"
    assert "biais du survivant" in d.to_dict()["affirmations"][0]["texte"]
