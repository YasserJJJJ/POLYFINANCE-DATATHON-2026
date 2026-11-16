"""Dessine le schéma d'architecture d'AlphaForge en SVG, sans dépendance.

    uv run python research/outils/schema_architecture.py

Écrit docs/refonte/architecture/schemas/architecture.svg. Les positions sont fixées à la main pour la lisibilité ;
le contenu suit les contrats des documents 02, 03 et 04.
"""

from pathlib import Path
from xml.sax.saxutils import escape

W, H = 1660, 1010
COL = {
    "agent": ("#eef4ff", "#2b5fb4", "#10233f"),
    "code": ("#f4f4f1", "#6b6b63", "#1c1c1a"),
    "humain": ("#fff6e5", "#b07a12", "#3d2c05"),
    "garde": ("#eaf7ef", "#2f7d4f", "#12331f"),
    "aws": ("#fdf0ea", "#c0562a", "#3f1b0c"),
}
out = []
labels = []


def box(x, y, w, h, kind, lines, rx=10, bold_first=True, size=13):
    fill, stroke, ink = COL[kind]
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    lh = size + 4
    y0 = y + h / 2 - lh * (len(lines) - 1) / 2 + size / 3
    for i, line in enumerate(lines):
        weight = "600" if (i == 0 and bold_first) else "400"
        out.append(f'<text x="{x + w / 2}" y="{y0 + i * lh:.1f}" text-anchor="middle" font-size="{size}" font-weight="{weight}" fill="{ink}">{escape(line)}</text>')


def label(x, y, s, size=12, anchor="middle", ink="#333", italic=False, bg=True):
    style = ' font-style="italic"' if italic else ""
    if bg:
        w = len(s) * size * 0.56 + 8
        x0 = x - w / 2 if anchor == "middle" else (x - 4 if anchor == "start" else x - w + 4)
        labels.append(f'<rect x="{x0:.1f}" y="{y - size}" width="{w:.1f}" height="{size + 5}" fill="#ffffff"/>')
    labels.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{ink}"{style}>{escape(s)}</text>')


def path(d, kind="fin"):
    style = {"epais": 'stroke="#10233f" stroke-width="4" marker-end="url(#fe)"',
             "retour": 'stroke="#8a3b12" stroke-width="1.8" stroke-dasharray="6 5" marker-end="url(#fr)"',
             "fin": 'stroke="#6b6b63" stroke-width="1.3" marker-end="url(#ff)"',
             "double": 'stroke="#6b6b63" stroke-width="1.3" marker-end="url(#ff)" marker-start="url(#ffd)"'}[kind]
    out.append(f'<path d="{d}" fill="none" {style}/>')


out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="-apple-system, Helvetica, Arial, sans-serif">')
out.append('<defs>'
           '<marker id="fe" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="14" refX="13" refY="7" orient="auto"><path d="M0,0 L16,7 L0,14 z" fill="#10233f"/></marker>'
           '<marker id="fr" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="10" refX="10" refY="5" orient="auto"><path d="M0,0 L12,5 L0,10 z" fill="#8a3b12"/></marker>'
           '<marker id="ff" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#6b6b63"/></marker>'
           '<marker id="ffd" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="8" refX="1" refY="4" orient="auto"><path d="M10,0 L0,4 L10,8 z" fill="#6b6b63"/></marker>'
           '</defs>')
out.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
out.append('<text x="60" y="34" font-size="18" font-weight="600" fill="#10233f">AlphaForge — architecture proposée</text>')
out.append('<text x="60" y="54" font-size="12" fill="#555">Quatre agents autour d\'un dossier de décision partagé et versionné · proposition du 15 novembre 2026, non construite</text>')

# Personne et interface
box(560, 70, 400, 52, "humain", ["La personne", "demande, répond, corrige, signale un changement, explore une variante"])
box(60, 160, 1280, 46, "code", ["Interface (code) — parcours lisible · affichages enregistrés · trois gestes : « je me suis trompé », « ma situation a changé », « et si… »"], bold_first=False)
path("M700,122 L700,157", "epais")
path("M820,160 L820,125", "epais")
label(640, 145, "demande, réponses", 11, bg=False)
label(880, 145, "affichages", 11, bg=False)

# Agents
box(60, 320, 240, 140, "agent", ["Agent 0", "Qualification et formalisation", "", "décision, profil, objectifs,", "inconnues, contradictions,", "questions"])
box(350, 320, 240, 140, "agent", ["Agent 1", "Recherche critique", "", "preuves, conditions, contradictions,", "limites, plan des méthodes ;", "spécialiste : lecteur de document"])
out.append('<rect x="635" y="306" width="420" height="186" rx="12" fill="#f7faff" stroke="#2b5fb4" stroke-width="1.2" stroke-dasharray="4 3"/>')
out.append('<text x="845" y="484" text-anchor="middle" font-size="12" font-weight="600" fill="#2b5fb4">Responsabilité 2 — analyse, confrontation comprise</text>')
box(648, 320, 172, 140, "agent", ["Agent 2", "Analyse et résolution", "", "options, plan scellé,", "conclusion typée"])
box(880, 320, 162, 140, "agent", ["Contradicteur", "spécialiste, contexte neuf", "", "objections de la grille ;", "verdict par le code"])
box(1100, 320, 240, 140, "agent", ["Agent 3", "Restitution et interaction", "", "trois profondeurs,", "questions, réactions"])

# Parcours principal
path("M230,206 L230,316", "epais")
label(222, 228, "demande", 11, anchor="end", bg=False)
path("M300,390 L346,390", "epais")
path("M590,390 L644,390", "epais")
path("M820,362 L876,362", "fin")
label(848, 352, "note", 10, bg=False)
path("M1055,390 L1096,390", "epais")
path("M1220,320 L1220,210", "epais")
label(1228, 228, "restitution, question", 11, anchor="start", bg=False)

# Retours et approfondissements
path("M880,418 L824,418", "retour")
label(850, 438, "verdict", 10, ink="#8a3b12", bg=False)
path("M380,320 C380,284 280,284 280,316", "retour")
label(336, 281, "hypothèse du parent en cause", 11, ink="#8a3b12")
path("M690,320 C690,262 560,262 560,316", "retour")
label(626, 272, "méthode manquante", 11, ink="#8a3b12")
path("M1150,320 C1150,236 500,236 500,316", "retour")
label(960, 258, "source contestée", 11, ink="#8a3b12")
path("M1000,206 C1000,252 100,232 100,316", "retour")
label(690, 243, "précision, correction, changement, variante", 11, ink="#8a3b12")
path("M160,316 L160,210", "fin")
label(166, 262, "question", 10, anchor="start", bg=False, ink="#555")

# Pièces sous les agents
for x, s in ((180, "fiche de qualification"), (462, "dossier de preuves · plan des méthodes"), (734, "plan scellé · note d'analyse"), (961, "objections, en un lot"), (1220, "restitution · questions")):
    label(x, 512, s, 11, italic=True, ink="#2b5fb4", bg=False)

# Portes et dossier
box(60, 540, 1280, 40, "code", ["Portes (code) — chaque pièce d'un rôle est contrôlée contre son contrat avant d'entrer au dossier ; un refus garde son motif"], bold_first=False)
for x in (180, 462, 734, 961, 1220):
    path(f"M{x},518 L{x},537", "fin")
box(60, 620, 1280, 96, "garde", ["Dossier de décision", "pièces immuables identifiées par leur empreinte · journal en ajout seul · état en vigueur déduit · branches pour les variantes",
                                "graphe de questions · graphe de preuves · graphe de tâches · états : refusée, en vigueur, remplacée, périmée, erronée · support : fichiers"], rx=22)
path("M700,580 L700,617", "fin")

# Organisation
box(60, 770, 290, 84, "code", ["Greffier (code)", "tâches, versions, invalidations, reprise ;", "lance la batterie et le contradicteur"])
box(385, 770, 270, 84, "code", ["Calculs (code)", "formulations, batterie fixe, rendus,", "tests de condition, verdicts"])
box(690, 770, 270, 84, "code", ["Qualification des données (code)", "empreintes, fenêtre, conventions,", "limites"])
box(995, 770, 345, 84, "garde", ["Catalogue versionné", "les règles écrites d'avance : gabarits de décision,", "formulations, seuils, grilles ; fiches qualifiées"])
path("M205,770 L205,720", "double")
path("M520,770 L520,720", "fin")
path("M825,770 L825,720", "fin")
box(1040, 900, 255, 48, "humain", ["L'équipe, hors exécution", "tient le catalogue, qualifie, relit"])
path("M1167,900 L1167,858", "fin")
label(700, 884, "Le catalogue porte les décisions prises d'avance ; le greffier, les portes et les calculs le lisent ; seule l'équipe le modifie.", 11, bg=False, ink="#555")

# Route AWS
out.append('<rect x="1395" y="286" width="235" height="470" rx="12" fill="#fffaf7" stroke="#c0562a" stroke-width="1.2" stroke-dasharray="4 3"/>')
out.append('<text x="1512" y="304" text-anchor="middle" font-size="12" font-weight="600" fill="#c0562a">Route AWS</text>')
box(1410, 322, 205, 84, "aws", ["Amazon Bedrock", "tous les appels de modèle : quatre", "agents, contradicteur, lecteur ;", "reclassement des fiches"], size=12)
box(1410, 426, 205, 58, "aws", ["CloudTrail et CloudWatch", "trace des appels de modèle,", "retrouvés par leur identifiant"], size=12)
box(1410, 506, 205, 58, "aws", ["AgentCore", "recherche web (agent 1)"], size=12)
box(1410, 632, 205, 70, "aws", ["S3 versionné", "miroir du dossier,", "sous accord du porteur"], size=12)
path("M1340,352 L1406,352", "fin")
label(1373, 344, "appels", 10, bg=False, ink="#555")
label(1373, 372, "(cadres", 9, bg=False, ink="#555")
label(1373, 383, "bleus)", 9, bg=False, ink="#555")
label(1373, 660, "miroir", 10, bg=False, ink="#8a3b12")
path("M1512,406 L1512,423", "fin")
path("M580,460 L580,498 L1372,498 L1372,535 L1406,535", "retour")
label(1090, 494, "recherche pendant la demande", 11, ink="#8a3b12")
path("M1340,668 L1406,668", "retour")

# Légende
out.append('<rect x="60" y="902" width="900" height="92" rx="8" fill="#fafafa" stroke="#cccccc"/>')
out.append('<text x="76" y="922" font-size="12" font-weight="600" fill="#333">Légende</text>')
path("M76,942 L136,942", "epais")
label(146, 946, "parcours principal d'une étude", 12, anchor="start", bg=False)
path("M76,964 L136,964", "retour")
label(146, 968, "approfondissement ou retour : une question est rouverte chez un autre rôle", 12, anchor="start", bg=False)
path("M76,984 L136,984", "fin")
label(146, 988, "coordination : contrôle, rangement, remise des pièces", 12, anchor="start", bg=False)
for i, (kind, s) in enumerate((("agent", "agent ou spécialiste : un modèle sur Amazon Bedrock"), ("code", "code, sans modèle"), ("humain", "personnes"), ("garde", "ce qui est conservé"), ("aws", "service AWS"))):
    fill, stroke, _ = COL[kind]
    y = 914 + i * 16
    out.append(f'<rect x="640" y="{y}" width="16" height="11" rx="3" fill="{fill}" stroke="{stroke}"/>')
    label(664, y + 10, s, 11, anchor="start", bg=False)
out.extend(labels)
out.append("</svg>")

cible = Path(__file__).resolve().parents[2] / "docs" / "refonte" / "architecture" / "schemas" / "architecture.svg"
cible.parent.mkdir(parents=True, exist_ok=True)
cible.write_text("\n".join(out))
print("écrit :", cible)
apercu = Path("/tmp/af_schemas/apercu.svg")  # même dessin sur un fond carré, pour un aperçu complet
if apercu.parent.exists():
    apercu.write_text("\n".join(out).replace(f'viewBox="0 0 {W} {H}" width="{W}" height="{H}"', f'viewBox="0 0 {W} {W}" width="{W}" height="{W}"'))
