"""Essai 9 : ce que Strands trace de lui-même, et vers où.

Par défaut (essais 2 à 8) : aucun exportateur n'est monté, le fournisseur de traces est le
fournisseur vide d'OpenTelemetry, et le seul hôte contacté est celui de Bedrock.
Ici on monte un exportateur EN MÉMOIRE (rien ne sort de la machine) pour voir ce que Strands
écrirait si l'on branchait un collecteur. Un appel de modèle, en flux (mode par défaut de Strands).

Relance : uv run --with strands-agents python research/experiences/technique/strands/essai9_traces.py
"""
import json
import os

os.environ["OTEL_SDK_DISABLED"] = "false"  # nécessaire pour que le fournisseur en mémoire enregistre

import commun  # noqa: E402
from opentelemetry import metrics, trace  # noqa: E402
from opentelemetry.sdk.trace import TracerProvider  # noqa: E402
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # noqa: E402
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter  # noqa: E402

print("fournisseur de traces avant tout réglage :", type(trace.get_tracer_provider()).__name__)
print("fournisseur de mesures avant tout réglage :", type(metrics.get_meter_provider()).__name__)
print("variables OTEL_* présentes :", {k: v for k, v in os.environ.items() if k.startswith(("OTEL_", "LANGFUSE", "STRANDS_"))})

memoire = InMemorySpanExporter()
fournisseur = TracerProvider()
fournisseur.add_span_processor(SimpleSpanProcessor(memoire))
trace.set_tracer_provider(fournisseur)

from strands import Agent  # noqa: E402

MARQUE = "MARQUE-CONFIDENTIELLE-4721"
agent = Agent(name="agent3_restitution", model=commun.modele("essai9", max_tokens=200, streaming=True), callback_handler=None,
              system_prompt="Tu réponds en cinq mots au plus.")
res = agent(f"Dis bonjour. ({MARQUE})")
print("\nréponse :", str(res).strip(), "| jetons selon Strands (flux) :", res.metrics.accumulated_usage)

spans = memoire.get_finished_spans()
print(f"\n{len(spans)} segments enregistrés (en mémoire seulement) :")
vidage = []
for s in spans:
    attrs = dict(s.attributes or {})
    evts = [{"nom": e.name, "attributs": dict(e.attributes or {})} for e in s.events]
    vidage.append({"nom": s.name, "attributs": attrs, "evenements": evts})
    print("  -", s.name, "| attributs :", sorted(attrs)[:14], "| événements :", [e["nom"] for e in evts])
texte = json.dumps(vidage, ensure_ascii=False, default=str)
(commun.SORTIES / "essai9_segments.json").write_text(json.dumps(vidage, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print("\nle texte de la demande figure-t-il dans les segments ?", MARQUE in texte)
print("le texte de la réponse figure-t-il dans les segments ?", str(res).strip()[:12] in texte)
commun.bilan("essai9")
