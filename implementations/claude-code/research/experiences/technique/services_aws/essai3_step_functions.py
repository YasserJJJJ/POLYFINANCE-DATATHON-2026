"""Essai 3 — Step Functions sans rien créer : validation de notre chaîne, puis essais d'états isolés.

A. validate_state_machine_definition sur chaine_alphaforge.asl.json (et sur une variante fautive,
   pour vérifier que le validateur voit vraiment les fautes).
B. test_state : exécute UN état de la définition avec une réponse simulée (« mock »). Aucun service
   n'est appelé, aucun rôle n'est passé, aucune machine n'existe. On y lit l'état suivant choisi.

Aucun appel de modèle.

    uv run python research/experiences/technique/services_aws/essai3_step_functions.py
"""

from __future__ import annotations

import copy
import json

from commun import ICI, client, ecrire, maintenant, sonde

DEFINITION = json.loads((ICI / "chaine_alphaforge.asl.json").read_text(encoding="utf-8"))
ENTREE = {"dossier": "robert-tesla", "tete": "sha256:aaaa", "donnees": {"empreinte": "sha256:d0"},
          "qualification": {"empreinte": "sha256:q1", "variable_manquante": True, "question": "Quel est votre portefeuille de départ ?"},
          "note": {"empreinte": "sha256:n1"}, "registre": {"empreinte": "sha256:r1", "verdict": "change", "amendements": 0}}


def valider(sfn, definition: dict, nom: str) -> dict:
    return sonde(f"validate[{nom}]", lambda: sfn.validate_state_machine_definition(definition=json.dumps(definition), type="STANDARD", severity="WARNING"),
                 lambda r: {"resultat": r["result"], "tronque": r.get("truncated"),
                            "diagnostics": [f"{d['severity']} {d['code']} @ {d.get('location', '')} : {d['message'][:160]}" for d in r["diagnostics"]]})


def variante_activites(definition: dict, compte: str = "000000000000") -> dict:
    """La même chaîne sans Lambda : chaque rôle devient une « activité ». Le produit, resté sur le poste,
    vient chercher la tâche (GetActivityTask, qui remet le jeton) et y répond (SendTaskSuccess)."""
    d = json.loads(json.dumps(definition).replace("$.Payload.", "$."))

    def convertir(etats: dict) -> None:
        for etat in etats.values():
            if etat["Type"] == "Map":
                convertir(etat["ItemProcessor"]["States"])
            if etat["Type"] != "Task" or "lambda:invoke" not in etat["Resource"]:
                continue
            attente_humaine = etat["Resource"].endswith(".waitForTaskToken")
            parametres = etat.pop("Parameters")
            etat["Resource"] = f"arn:aws:states:us-east-1:{compte}:activity:{parametres['FunctionName']}"
            if isinstance(parametres.get("Payload"), dict):
                etat["Parameters"] = {k: v for k, v in parametres["Payload"].items() if k != "jeton.$"}
            etat.pop("OutputPath", None)
            if not attente_humaine:
                etat["TimeoutSeconds"] = 900   # si le processus local meurt, l'état échoue au lieu d'attendre un an
    convertir(d["States"])
    d["Comment"] += " Variante à activités : aucun Lambda."
    return d


def essayer(sfn, nom: str, etat: str, entree: dict, definition: dict = DEFINITION, **options) -> dict:
    def appel():
        return sfn.test_state(definition=json.dumps(definition), stateName=etat, input=json.dumps(entree), inspectionLevel="INFO", **options)
    return sonde(f"test_state[{nom}]", appel,
                 lambda r: {"statut": r.get("status"), "etat_suivant": r.get("nextState"), "erreur": r.get("error"),
                            "sortie": (r.get("output") or "")[:400]})


def main() -> None:
    sfn = client("stepfunctions")
    fautive = copy.deepcopy(DEFINITION)
    fautive["States"]["Agent1"]["Next"] = "EtatQuiNExistePas"          # transition vers un état absent
    sans_jeton = copy.deepcopy(DEFINITION)
    del sans_jeton["States"]["QuestionALaPersonne"]["Parameters"]["Payload"]["jeton.$"]  # attente sans jeton transmis : personne ne pourra répondre
    activites = variante_activites(DEFINITION)
    (ICI / "sorties" / "chaine_variante_activites.asl.json").write_text(json.dumps(activites, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validations = [valider(sfn, DEFINITION, "notre chaîne"), valider(sfn, fautive, "variante fautive : transition vers un état absent"),
                   valider(sfn, sans_jeton, "variante fautive : attente sans jeton transmis"),
                   valider(sfn, activites, "variante à activités, sans Lambda")]

    jeton = {"Task": {"Token": "JETON-FICTIF"}, "Execution": {"Id": "essai"}}
    essais = [
        # Transitions : le code tranche, pas un modèle.
        essayer(sfn, "variable manquante -> question", "FautIlDemander", ENTREE),
        essayer(sfn, "rien ne manque -> agent 1", "FautIlDemander", ENTREE | {"qualification": {"variable_manquante": False}}),
        essayer(sfn, "verdict change, premier passage -> agent 2", "VerdictChange", ENTREE),
        essayer(sfn, "verdict change, déjà amendé -> interrompue", "VerdictChange", ENTREE | {"registre": {"verdict": "change", "amendements": 1}}),
        essayer(sfn, "verdict tient -> agent 3", "VerdictChange", ENTREE | {"registre": {"verdict": "tient", "amendements": 0}}),
        # Question à la personne : la réponse simulée tient lieu de SendTaskSuccess.
        essayer(sfn, "question : réponse reçue", "QuestionALaPersonne", ENTREE, context=json.dumps(jeton),
                mock={"result": json.dumps({"reponse": "60 % obligations, 40 % actions", "affichage": "sha256:aff1"})}),
        essayer(sfn, "question : délai dépassé", "QuestionALaPersonne", ENTREE, context=json.dumps(jeton),
                mock={"errorOutput": {"error": "States.Timeout", "cause": "aucune réponse en 24 h"}}),
        # Erreurs d'outils : réessai, puis renvoi vers « interrompue ».
        essayer(sfn, "agent 1 : limitation de débit, premier échec", "Agent1", ENTREE,
                mock={"errorOutput": {"error": "ThrottlingException", "cause": "débit"}}, stateConfiguration={"retrierRetryCount": 0}),
        essayer(sfn, "agent 1 : limitation de débit, réessais épuisés", "Agent1", ENTREE,
                mock={"errorOutput": {"error": "ThrottlingException", "cause": "débit"}}, stateConfiguration={"retrierRetryCount": 2}),
        essayer(sfn, "agent 0 : porte refusée", "Agent0", ENTREE,
                mock={"errorOutput": {"error": "PorteRefusee", "cause": "citation absente de la demande"}}),
        # Un rôle qui réussit : la sortie ne garde que l'empreinte de la pièce. Le contrôle strict de la réponse
        # simulée exige la forme de l'API (Payload et Body sont des chaînes, que l'intégration relit en JSON).
        essayer(sfn, "agent 1 : réussite", "Agent1", ENTREE, mock={"result": json.dumps({"Payload": json.dumps({"empreinte": "sha256:p1"}), "StatusCode": 200})}),
        essayer(sfn, "agent 1 : réussite, réponse non contrôlée", "Agent1", ENTREE,
                mock={"result": json.dumps({"Payload": {"empreinte": "sha256:p1"}}), "fieldValidationMode": "NONE"}),
        # Intégration directe Bedrock (réponse simulée : aucun modèle appelé).
        essayer(sfn, "agent 3 : intégration Bedrock directe", "Agent3", ENTREE,
                mock={"result": json.dumps({"Body": json.dumps({"content": [{"type": "text", "text": "restitution fictive"}]}), "ContentType": "application/json"})}),
        essayer(sfn, "agent 3 : intégration Bedrock directe, réponse non contrôlée", "Agent3", ENTREE,
                mock={"result": json.dumps({"Body": {"content": [{"type": "text", "text": "restitution fictive"}]}}), "fieldValidationMode": "NONE"}),
        # Variante à activités : le produit local répond avec le jeton reçu ; même enchaînement.
        essayer(sfn, "activités : question, réponse reçue", "QuestionALaPersonne", ENTREE, definition=activites,
                mock={"result": json.dumps({"reponse": "60 % obligations, 40 % actions"})}),
        essayer(sfn, "activités : agent 1 réussit", "Agent1", ENTREE, definition=activites, mock={"result": json.dumps({"empreinte": "sha256:p1"})}),
        essayer(sfn, "activités : processus local mort (délai)", "Agent1", ENTREE, definition=activites,
                mock={"errorOutput": {"error": "States.Timeout", "cause": "aucun travailleur"}}),
    ]
    ecrire("essai3_step_functions.json", {"quand": maintenant(), "validations": validations, "essais_d_etats": essais})
    for v in validations:
        print(v["sonde"], "->", v["etat"], v.get("resume") or f"{v.get('code')} {v.get('message')}")
    for e in essais:
        r = e.get("resume") or {}
        print(f"  {e['etat']:9} {e['sonde']:62} " + (f"{r.get('statut')} -> {r.get('etat_suivant')} {r.get('erreur') or ''} {r.get('sortie', '')[:150]}"
                                                    if e["etat"] == "autorise" else f"{e.get('code')} — {e.get('message', '')[:200]}"))


if __name__ == "__main__":
    main()
