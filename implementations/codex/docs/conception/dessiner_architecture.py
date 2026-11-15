"""Rendu documentaire SVG/PNG. Ne construit ni interface ni moteur AlphaForge."""
from pathlib import Path
from html import escape
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 2200, 1450
BG = "#f5f7fb"
INK = "#172b45"
MUTED = "#475970"
BLUE = "#245b9e"
TEAL = "#087b7c"
PURPLE = "#7750a5"
ORANGE = "#b7650b"
GREY = "#738093"
im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<title>AlphaForge : architecture proposée à quatre agents</title>',
    '<desc>Quatre agents transforment un dossier partagé. Le noyau déterministe '
    'contrôle les versions et les écritures. Les retours ciblés rouvrent les '
    'questions de besoin, de preuve ou de calcul. Les interventions humaines '
    'restent distinctes. Conception à valider, non construite.</desc>',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
]


def font(size, bold=False):
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/" + name, size)


def rect(x, y, w, h, fill, stroke=None, radius=18, width=2):
    d.rounded_rectangle((x, y, x+w, y+h), radius, fill, stroke, width)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
               f'fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}"/>')


def text(x, y, lines, size=24, color=INK, bold=False, lineheight=None, maxwidth=None):
    if isinstance(lines, str):
        lines = [lines]
    lh = lineheight or size * 1.35
    f = font(size, bold)
    for i, line in enumerate(lines):
        if maxwidth is not None and d.textlength(line, font=f) > maxwidth:
            raise ValueError(f"Texte trop large : {line}")
        yy = y + i*lh
        d.text((x, yy), line, font=f, fill=color, anchor="lt")
        svg.append(f'<text x="{x}" y="{yy}" fill="{color}" font-size="{size}" '
                   f'font-family="Arial, sans-serif" font-weight="{700 if bold else 400}" '
                   f'dominant-baseline="hanging">{escape(line)}</text>')


def path(points, color, width=3, dash=False, end=False, start=False):
    coords = " ".join(f"{x},{y}" for x, y in points)
    svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" '
               f'stroke-width="{width}" stroke-linejoin="round" '
               f'{"stroke-dasharray=\"10 8\"" if dash else ""}/>')
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        length = math.hypot(x2-x1,y2-y1)
        if dash and length:
            for a in range(0, int(length), 18):
                b=min(a+10,length)
                d.line((x1+(x2-x1)*a/length,y1+(y2-y1)*a/length,
                        x1+(x2-x1)*b/length,y1+(y2-y1)*b/length),fill=color,width=width)
        else:
            d.line((x1,y1,x2,y2),fill=color,width=width)
    def head(p, prev):
        angle=math.atan2(p[1]-prev[1],p[0]-prev[0])
        n=12
        pts=[p,(p[0]-n*math.cos(angle)+n*.55*math.sin(angle),
                p[1]-n*math.sin(angle)-n*.55*math.cos(angle)),
               (p[0]-n*math.cos(angle)-n*.55*math.sin(angle),
                p[1]-n*math.sin(angle)+n*.55*math.cos(angle))]
        d.polygon(pts,fill=color)
        svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="{color}"/>')
    if end: head(points[-1],points[-2])
    if start: head(points[0],points[1])


text(60, 40, "AlphaForge — quatre agents, un dossier de décision", 43, bold=True)
text(60, 99, "Architecture proposée pour validation • Les agents proposent ; le noyau contrôle et versionne.", 26, MUTED)
for x, color, label, dashed in [
    (65, TEAL, "Parcours principal", False),
    (490, BLUE, "Dossier / échanges", False),
    (920, PURPLE, "Retours et approfondissements", False),
    (1515, ORANGE, "Interventions humaines", True),
]:
    path([(x,161),(x+58,161)],color,4,dashed,end=True)
    text(x+75,147,label,23,color)

# Human loop is distinct from the main workflow and from dossier commits.
path([(2140,690),(2180,690),(2180,203),(190,203),(190,230)],
     ORANGE,3,True,end=True)
text(1270, 179, "Questions et résultats à examiner", 20, ORANGE)

rect(60,230,280,215,"#fff4e7",ORANGE)
text(82,251,"PERSONNE",23,ORANGE,True)
text(82,297,["Exprime le besoin","Précise si nécessaire","Corrige ou explore","Choisit explicitement"],23,lineheight=33,maxwidth=242)
path([(200,445),(200,515),(170,515),(170,550)],ORANGE,3,True,end=True)

rect(400,230,1100,215,"#eaf1fb",BLUE)
text(430,250,"DOSSIER PARTAGÉ ET VERSIONNÉ",29,BLUE,True)
text(430,301,["Mandat et assertions • Questions • Preuves • Méthodes",
              "Calculs et contrôles • Conclusions • Vues • Événements"],
     25,lineheight=36,maxwidth=1030)
text(430,385,"Révisions immuables • Dépendances • Historique • Variantes explicites",23,BLUE,maxwidth=1030)

rect(1560,230,580,215,"#edf0f5",GREY)
text(1585,251,"NOYAU DÉTERMINISTE",28,INK,True)
text(1585,298,["Contrôle droits, références et versions",
               "Commet et invalide les dépendances",
               "Planifie, attend et reprend les tâches"],24,lineheight=34,maxwidth=530)
text(1585,410,"Logiciel de coordination, pas un 5e agent",21,MUTED)
path([(1560,338),(1500,338)],BLUE,4,end=True)
text(1505,292,"commit",16,BLUE)

# Blue bus: read snapshots and return proposed changes; sole writer is the kernel.
path([(950,445),(950,493)],BLUE,3,end=True)
path([(290,500),(2020,500),(2020,445)],BLUE,3,end=True)
text(1030,463,"Révision lue + propositions ChangeSet",21,BLUE)

cards = [
    {
      "x":60,"num":"0","title":"QUALIFIER","name":"Qualification et formalisation",
      "body":["Comprend la décision et ses échéances.","Distingue faits, préférences, contraintes.","Choisit les clarifications utiles."],
      "out":["Mandat + questions + critères"],
      "tools":["Déclarations et historique du dossier","Règles professionnelles • Schéma typé","Contrôles de contradiction"],
    },
    {
      "x":600,"num":"1","title":"RECHERCHER","name":"Recherche et revue critique",
      "body":["Examine sources et méthodes.","Cherche les limites et contre-arguments.","Peut contester une hypothèse parent."],
      "out":["Preuves + méthodes + lacunes"],
      "tools":["Corpus P2 • 00 / 00B / 01 • Notebook","Recherche AWS • Lecture HTTP/PDF","Dépôts GitHub • Sources primaires"],
    },
    {
      "x":1140,"num":"2","title":"RÉSOUDRE","name":"Analyse et résolution",
      "body":["Formule le problème financier.","Calcule avec des outils admis.","Vérifie, compare et borne la conclusion."],
      "out":["Plans + calculs + contrôles"],
      "tools":["Données qualifiées • Méthodes admises","Python / solveurs • Tests de référence","Scénarios • Sensibilité • Faisabilité"],
    },
    {
      "x":1680,"num":"3","title":"RESTITUER","name":"Restitution et interaction",
      "body":["Explique ce que les pièces soutiennent.","Montre alternatives, manques et limites.","Organise l’examen et les révisions."],
      "out":["Assertions + explication + retours"],
      "tools":["Registre de résultats • Passages cités","Valeurs liées au calcul • 5 contrôles","Historique des vues et changements"],
    },
]
for c in cards:
    x=c["x"]
    path([(x+230,500),(x+230,550)],BLUE,3,end=True,start=True)
    rect(x,550,460,400,"#ffffff","#c8d3e2")
    rect(x+20,570,54,46,TEAL,radius=10)
    text(x+37,578,c["num"],28,"#ffffff",True)
    text(x+89,576,c["title"],27,TEAL,True)
    text(x+23,636,c["name"],25,INK,True,maxwidth=416)
    text(x+23,682,c["body"],21,INK,lineheight=30,maxwidth=416)
    text(x+23,782,c["out"],23,TEAL,True,maxwidth=416)
    rect(x+15,825,430,108,"#f1f4f8",radius=10)
    text(x+27,840,c["tools"],19,MUTED,lineheight=27,maxwidth=410)
for x in (520,1060,1600):
    path([(x,718),(x+80,718)],TEAL,5,end=True)

rect(60,1020,2080,157,"#f1ebf8",PURPLE)
for x in (290,830,1370,1910):
    path([(x,950),(x,1020)],PURPLE,3,end=True,start=True)
text(88,1040,"APPROFONDIR ET ROUVRIR LE BON PROPRIÉTAIRE",27,PURPLE,True)
text(88,1085,"Besoin / contrainte → Agent0       Preuve / méthode → Agent1       Formulation / calcul → Agent2       Explication → Agent3",24,PURPLE,maxwidth=2000)
text(88,1128,"Une découverte peut invalider une hypothèse parent. Seules les dépendances touchées sont rouvertes ; les autres pièces restent réutilisables.",22,MUTED,maxwidth=2000)

rect(60,1217,820,155,"#ffffff","#c8d3e2")
text(82,1236,"INFÉRENCES : ROUTE AWS CONVENUE",23,BLUE,True)
text(82,1279,["Tous les rôles et auxiliaires : Amazon Bedrock",
               "alphaforge • us-east-1 • global.openai.gpt-6-astra",
               "Accès vérifié en P2 ; aucune résidence canadienne déduite."],21,MUTED,lineheight=28,maxwidth=775)
rect(910,1217,670,155,"#ffffff","#c8d3e2")
text(932,1236,"IMPLÉMENTATION PROPOSÉE",23,BLUE,True)
text(932,1279,["Local : SQLite + artefacts immuables",
               "LangGraph à qualifier ; Strands Graph alternative",
               "Le moteur reste distinct du dossier métier."],21,MUTED,lineheight=28,maxwidth=625)
rect(1610,1217,530,155,"#fff4e7",ORANGE)
text(1632,1236,"VALIDATION AVANT CONSTRUCTION",21,ORANGE,True)
text(1632,1279,["Questions ≠ tâches ≠ preuves",
               "Parcours présenté = projection du dossier",
               "Préparé ≠ affiché ≠ examiné ≠ accepté"],21,MUTED,lineheight=28,maxwidth=485)
text(60,1397,"Parcours logique : les flèches vertes ne représentent pas des écritures directes entre agents.",20,MUTED)
text(60,1425,"Conception documentaire • 15 novembre 2026 • Les contrats détaillent les entrées, droits, sorties et contrôles.",18,MUTED)

svg.append("</svg>")
(ROOT/"architecture.svg").write_text("\n".join(svg),encoding="utf-8")
im.save(ROOT/"architecture.png")
print("Architecture documentaire SVG et PNG produite.")
