"""Rendu HTML autonome d'un dossier de décision (aucune dépendance externe).

Conventions de présentation (research/R05) : papier blanc, encre noire, gris ; une seule couleur
d'accent, réservée à l'élément mis en évidence (IBCS) ; hypothèses en italique (motif, pas couleur) ;
sections, graphiques et tableaux numérotés avec « Sources » et « Note » ; unités dans les en-têtes ;
barres à partir de zéro ; chiffres tabulaires. Chaque valeur reste reliée à son enregistrement.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime

from .evidence import _DECIMALS, CMP_EXPR, MINUS, PLACEHOLDER, comparison_word, format_value, join_comparison, rounded_value

STATUS_HELP = {
    "mesuré": "calculé par un outil sur les données",
    "déclaré": "énoncé du défi (profil fictif)",
    "scénario": "élément du scénario de démonstration",
    "hypothèse": "hypothèse de démonstration, modifiable",
    "inconnu": "information non fournie",
}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MOIS_COURT = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
SOURCE_DONNEES = "Yahoo Finance (cours ajustés) et Banque du Canada (USD/CAD), via le jeu de départ PolyFinances ; calculs AlphaForge."
_ID = re.compile(r"[A-Z]-\d{4}")


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def _tip(rec: dict) -> str:
    parts = [f"{rec['id']} · {rec['label']}", f"statut : {rec['status']}"]
    if rec.get("period"):
        parts.append(f"période : {_period(rec['period'])}")
    return " · ".join(parts)


def _hyp(rec: dict) -> str:
    return {"hypothèse": " hyp", "scénario": " hyp", "inconnu": " unk"}.get(rec["status"], "")


def _bare(rec: dict) -> str:
    """Valeur sans unité, quand l'unité est donnée par l'en-tête de colonne."""
    if rec["unit"] == "pct" and rec["value"] is not None:
        v = rec["value"] * 100
        s = f"{abs(v):.1f}".replace(".", ",")
        return (MINUS if v < 0 and round(abs(v), 1) != 0 else "") + s
    return rec["display"]


def value(rec: dict, bare: bool = False) -> str:
    kind = "num" if rec["unit"] != "text" else "txt"
    shown = _bare(rec) if bare else rec["display"]
    return (f'<a class="v {kind}{_hyp(rec)}" href="#{esc(rec["id"])}" data-tip="{esc(_tip(rec))}">{esc(shown)}'
            f'<sup class="rid">{esc(rec["id"])}</sup></a>')


def _cmp_word(kind: str, a: dict, b: dict) -> str | None:
    """Même calcul que le registre ; None si la comparaison est invalide (unités, valeur absente)."""
    if a["unit"] not in _DECIMALS or a["unit"] != b["unit"] or a["value"] is None or b["value"] is None:
        return None
    return comparison_word(kind, rounded_value(a["value"], a["unit"]), rounded_value(b["value"], b["unit"]))


def render_html(template: str, recs: dict) -> str:
    out, last = [], 0
    for m in PLACEHOLDER.finditer(template):
        out.append(esc(template[last : m.start()]))
        expr, last = m.group(1), m.end()
        ids = _ID.findall(expr)
        cmp = CMP_EXPR.fullmatch(expr)
        word = _cmp_word(cmp[1], recs[cmp[2]], recs[cmp[3]]) if cmp and all(i in recs for i in ids) else None
        if not ids or any(i not in recs for i in ids) or (cmp and word is None):
            out.append(f'<span class="bad">[{esc(expr)} ?]</span>')
        elif cmp:
            word, used = join_comparison(word, template[last:], template[: m.start()])
            last += used
            out.append(f'<span class="cmp" data-tip="{esc("comparaison calculée : " + cmp[2] + " / " + cmp[3])}">{esc(word)}</span>')
        elif expr.endswith(".label"):
            r = recs[ids[0]]
            out.append(f'<a class="v txt unk" href="#{esc(r["id"])}" data-tip="{esc(_tip(r))}">{esc(r["label"])}<sup class="rid">{esc(r["id"])}</sup></a>')
        else:
            out.append(value(recs[ids[0]]))
    out.append(esc(template[last:]))
    return "".join(out)


def _date_fr(iso: str) -> str:
    try:
        d = datetime.fromisoformat(iso)
    except ValueError:
        return iso
    return f"{d.day} {MOIS[d.month - 1]} {d.year}"


def _short(s: str) -> str:
    y, m, dd = s.split("-")
    return f"{int(dd)} {MOIS_COURT[int(m) - 1]} {y}"


def _period(p) -> str:
    return f"{_short(p[0])} – {_short(p[1])}" if p else ""


# ---------------------------------------------------------------- graphiques SVG


def _colors(names: list[str], highlight: str | None) -> list[str]:
    """Une seule couleur d'accent pour la série mise en évidence ; les autres en gris (IBCS)."""
    grays = ["var(--gray-1)", "var(--gray-2)", "var(--gray-3)"]
    out, gi = [], 0
    for n in names:
        if n == highlight:
            out.append("var(--accent)")
        else:
            out.append(grays[gi])
            gi += 1
    return out


def _pct(v: float) -> str:
    return format_value(v, "pct")


def _notes(sources: str, note: str, refs: list[str], last: str | None = None) -> str:
    refs_html = " ".join(f'<a href="#{esc(r)}">{esc(r)}</a>' for r in refs)
    return ('<div class="srcnote">'
            f"<p><span>Sources :</span> {esc(sources)}</p>"
            + (f"<p><span>Note :</span> {esc(note)}</p>" if note else "")
            + (f"<p><span>Dernière donnée :</span> {esc(last)}</p>" if last else "")
            + (f'<p class="refs"><span>Valeurs citées :</span> {refs_html}</p>' if refs else "") + "</div>")


def line_chart(c: dict, num: int) -> str:
    W, H, L, R, T, B = 760, 300, 56, 118, 14, 30
    names = list(c["series"])[:3]
    cols = _colors(names, c.get("mise_en_evidence", names[0]))
    xs = [p[0] for p in c["series"][names[0]]]
    allv = [p[1] for n in names for p in c["series"][n]]
    lo = min(-0.05, (int(min(allv) * 10) - 1) / 10)
    x_of = {x: L + i * (W - L - R) / max(1, len(xs) - 1) for i, x in enumerate(xs)}

    def y(v):
        return T + (0 - v) / (0 - lo) * (H - T - B)

    grid = []
    step = 0.1 if lo >= -0.6 else 0.2
    g = 0.0
    while g >= lo - 1e-9:
        grid.append(f'<line class="grid" x1="{L}" x2="{W - R}" y1="{y(g):.1f}" y2="{y(g):.1f}"/>'
                    f'<text class="ax" x="{L - 8}" y="{y(g) + 4:.1f}" text-anchor="end">{esc(_pct(g).replace(chr(160) + "%", ""))}</text>')
        g = round(g - step, 2)
    for yr in sorted({x[:4] for x in xs}):
        first = next(x for x in xs if x.startswith(yr))
        if first[5:7] == "01":
            grid.append(f'<line class="tick" x1="{x_of[first]:.1f}" x2="{x_of[first]:.1f}" y1="{H - B}" y2="{H - B + 5}"/>'
                        f'<text class="ax" x="{x_of[first]:.1f}" y="{H - 8}" text-anchor="middle">{yr}</text>')
    paths, labels = [], []
    order = sorted(range(len(names)), key=lambda i: cols[i] == "var(--accent)")  # l'accent dessiné en dernier
    for i in order:
        n = names[i]
        pts = c["series"][n]
        d = "M" + " L".join(f"{x_of[p[0]]:.1f},{y(p[1]):.1f}" for p in pts if p[0] in x_of)
        w = 2 if cols[i] == "var(--accent)" else 1.6
        paths.append(f'<path d="{d}" fill="none" stroke="{cols[i]}" stroke-width="{w}" stroke-linejoin="round"/>')
        labels.append((y(pts[-1][1]), c.get("etiquettes", {}).get(n, n), cols[i]))
    placed = []
    for yy, short, col in sorted(labels):
        if placed and yy - placed[-1] < 15:
            yy = placed[-1] + 15
        placed.append(yy)
        paths.append(f'<text class="dl" x="{W - R + 8}" y="{yy + 4:.1f}" fill="{col}">{esc(short)}</text>')
    data = {"x": xs, "series": {n: [p[1] for p in c["series"][n]] for n in names}}
    legend = "".join(f'<span class="key"><i style="background:{cols[i]}"></i>{esc(n)}</span>' for i, n in enumerate(names))
    rows = "".join(f"<tr><td>{esc(_short(xs[j]))}</td>" + "".join(f'<td class="n">{esc(_pct(data["series"][n][j]).replace(chr(160) + "%", ""))}</td>' for n in names) + "</tr>"
                   for j in range(0, len(xs), 4))
    return f"""
<figure class="fig" id="graphique-{num}">
  <figcaption><span class="fignum">Graphique {num}</span> {esc(c['titre'])}<span class="unit">En %, {esc(c.get('sous_titre', 'baisse par rapport au plus haut précédent'))}</span></figcaption>
  <div class="legend">{legend}</div>
  <div class="plot"><svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(c['titre'])}" data-line='{esc(json.dumps(data))}' data-l="{L}" data-r="{R}" data-w="{W}">
    {''.join(grid)}<line class="zero" x1="{L}" x2="{W - R}" y1="{y(0):.1f}" y2="{y(0):.1f}"/>
    {''.join(paths)}<line class="cross" x1="0" x2="0" y1="{T}" y2="{H - B}" visibility="hidden"/>
  </svg><div class="tooltip" hidden></div></div>
  {_notes(SOURCE_DONNEES, c.get('note', ''), c['sources'], _short(xs[-1]))}
  <details class="data"><summary>Données du graphique (une semaine sur quatre, en %)</summary><div class="wrap"><table class="tbl"><thead><tr><th>Semaine</th>{''.join(f'<th class="n">{esc(n)}</th>' for n in names)}</tr></thead><tbody>{rows}</tbody></table></div></details>
</figure>"""


def bar_chart(c: dict, num: int) -> str:
    names = list(c["series"])[:3]
    cols = _colors(names, c.get("mise_en_evidence"))
    cats = [p[0] for p in c["series"][names[0]]]
    vals = {n: dict((p[0], p[1]) for p in c["series"][n]) for n in names}
    W, L, R, barh, gap = 760, 196, 56, 13, 3
    rowh = (barh + gap) * len(names) + 16
    H = 40 + rowh * len(cats)
    vmax = max(max(max(v.values()) for v in vals.values()), c.get("repere", {}).get("valeur", 0))
    vmax = min(1.0, (int(vmax * 10) + 1) / 10)

    def x(v):
        return L + v / vmax * (W - L - R)

    out = []
    g = 0.0
    while g <= vmax + 1e-9:
        out.append(f'<line class="grid" x1="{x(g):.1f}" x2="{x(g):.1f}" y1="18" y2="{H - 20}"/>'
                   f'<text class="ax" x="{x(g):.1f}" y="{H - 5}" text-anchor="middle">{esc(_pct(g).replace(chr(160) + "%", ""))}</text>')
        g = round(g + 0.1, 2)
    for ci, cat in enumerate(cats):
        y0 = 24 + ci * rowh
        out.append(f'<text class="cat" x="{L - 12}" y="{y0 + len(names) * (barh + gap) / 2 + 2:.1f}" text-anchor="end">{esc(cat)}</text>')
        for si, n in enumerate(names):
            v = vals[n].get(cat, 0.0)
            yy = y0 + si * (barh + gap)
            w = max(0.0, x(v) - L)
            out.append(f'<g class="bar"><rect x="{L}" y="{yy}" width="{w:.1f}" height="{barh}" fill="{cols[si]}">'
                       f'<title>{esc(n)} — {esc(cat)} : {esc(_pct(v))}</title></rect>'
                       f'<text class="bl" x="{L + w + 5:.1f}" y="{yy + barh - 2}">{esc(_pct(v).replace(chr(160) + "%", ""))}</text></g>')
    out.append(f'<line class="zero" x1="{L}" x2="{L}" y1="18" y2="{H - 20}"/>')
    if c.get("repere"):
        xv = x(c["repere"]["valeur"])
        out.append(f'<line class="ref" x1="{xv:.1f}" x2="{xv:.1f}" y1="14" y2="{H - 20}"/>'
                   f'<text class="ax" x="{xv:.1f}" y="10" text-anchor="middle">{esc(c["repere"]["libelle"])} ({esc(_pct(c["repere"]["valeur"]))})</text>')
    legend = "".join(f'<span class="key"><i style="background:{cols[i]}"></i>{esc(n)}</span>' for i, n in enumerate(names))
    rows = "".join(f"<tr><td>{esc(cat)}</td>" + "".join(f'<td class="n">{esc(_pct(vals[n].get(cat, 0.0)).replace(chr(160) + "%", ""))}</td>' for n in names) + "</tr>" for cat in cats)
    return f"""
<figure class="fig" id="graphique-{num}">
  <figcaption><span class="fignum">Graphique {num}</span> {esc(c['titre'])}<span class="unit">En % du total</span></figcaption>
  <div class="legend">{legend}</div>
  <div class="plot"><svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(c['titre'])}">{''.join(out)}</svg></div>
  {_notes(SOURCE_DONNEES, c.get('note', ''), c['sources'])}
  <details class="data"><summary>Données du graphique (en %)</summary><div class="wrap"><table class="tbl"><thead><tr><th>Groupe</th>{''.join(f'<th class="n">{esc(n)}</th>' for n in names)}</tr></thead><tbody>{rows}</tbody></table></div></details>
</figure>"""


# ---------------------------------------------------------------- blocs


def kpis(d: dict, recs: dict) -> str:
    items = []
    for h in d.get("chiffres_cles", []):
        r = recs[h["valeur"]]
        items.append(f'<div class="kpi"><div class="kpi-l">{render_html(h["libelle"], recs)}</div>'
                     f'<div class="kpi-v">{value(r)}</div><div class="kpi-d">{render_html(h.get("detail", ""), recs)}</div></div>')
    return f'<div class="kpis">{"".join(items)}</div>' if items else ""


def profile_card(d: dict, recs: dict) -> str:
    cells = "".join(f'<div><dt>{esc(lbl)}</dt><dd>{esc(recs[i]["display"])}</dd></div>' for lbl, i in d.get("fiche_profil", []) if i in recs)
    return f'<dl class="profile">{cells}</dl>' if cells else ""


def tables(d: dict, recs: dict, start: int) -> tuple[str, int]:
    out = []
    n = start
    for t in d.get("tableaux", []):
        n += 1
        cols = t["colonnes"]
        all_pct = [all(recs[r["cellules"][j]]["unit"] == "pct" for r in t["lignes"] if r["cellules"][j]) for j in range(len(cols))]
        head = '<thead><tr><th></th>' + "".join(f'<th class="n">{esc(c)}{" (%)" if all_pct[j] else ""}</th>' for j, c in enumerate(cols)) + "</tr></thead>"
        body = "".join(
            f'<tr><th scope="row">{esc(row["nom"])}</th>'
            + "".join(f'<td class="n">{value(recs[c], bare=all_pct[j]) if c else "—"}</td>' for j, c in enumerate(row["cellules"])) + "</tr>"
            for row in t["lignes"]
        )
        refs = [c for row in t["lignes"] for c in row["cellules"] if c]
        out.append(f'<figure class="fig" id="tableau-{n}"><figcaption><span class="fignum">Tableau {n}</span> {esc(t["titre"])}</figcaption>'
                   f'<div class="wrap"><table class="tbl opts">{head}<tbody>{body}</tbody></table></div>'
                   + _notes(SOURCE_DONNEES, "En italique : valeur fixée par hypothèse de démonstration. Portefeuilles rééquilibrés chaque semaine ; aucune "
                            "de ces options n'est une recommandation.", refs[:0]) + "</figure>")
    return "".join(out), n


def claims(items: list, recs: dict) -> str:
    return '<ol class="claims">' + "".join(
        f'<li id="{esc(c["id"])}"><p>{render_html(c["gabarit"], recs)}</p>'
        f'<span class="stw" data-tip="{esc(STATUS_HELP.get(c["statut"], "aucun enregistrement cité"))}">{esc(c["statut"])}</span></li>'
        for c in items
    ) + "</ol>"


def _source(r: dict) -> str:
    if r["id"].startswith("D"):
        return "Jeu de départ"
    if r["status"] == "mesuré":
        return "Calcul"
    if r["origin"].startswith("énoncé"):
        return "Énoncé, " + r["origin"].split(", ", 1)[-1]
    if r["origin"].startswith("scénario"):
        return "Scénario"
    return r["origin"][:1].upper() + r["origin"][1:]


def _measure(r: dict) -> str:
    lbl, subj = r["label"], r.get("subject") or ""
    for s in (f" de {subj}", f" dans {subj}", f" {subj}", f" ({subj})"):
        if subj and lbl.endswith(s):
            return lbl[: -len(s)]
    return lbl


def _cited_ids(d: dict) -> set[str]:
    texts = [c["gabarit"] for c in d["affirmations"]] + [d["resume"]["gabarit"]] + [h.get("detail", "") for h in d.get("chiffres_cles", [])]
    ids = {i for t in texts for i in _ID.findall(t)}
    ids |= {h["valeur"] for h in d.get("chiffres_cles", [])}
    ids |= {c for t in d.get("tableaux", []) for row in t["lignes"] for c in row["cellules"] if c}
    ids |= {s for c in d.get("graphiques", []) for s in c.get("sources", [])}
    ids |= {i for c in d["affirmations"] for i in c["references"]}
    return ids


def registry(d: dict, recs: dict) -> str:
    """Registre en annexe : regroupé par sujet, valeurs citées d'abord, conventions en notes numérotées."""
    notes: list[str] = []
    for r in recs.values():
        for c in r.get("conventions") or []:
            if c not in notes:
                notes.append(c)
    cited = _cited_ids(d)

    def group(r):
        return {"P": "Profil et demande", "D": "Données sources"}.get(r["id"][0]) or r.get("subject") or "Autres"

    first: dict[str, int] = {}
    for r in recs.values():
        first.setdefault(group(r), len(first))
    rank = {"P": 0, "R": 1, "D": 2}
    items = sorted(recs.values(), key=lambda r: (rank.get(r["id"][0], 3), first[group(r)], r["id"]))

    # Conventions communes à tous les calculs : énoncées une fois, pas répétées à chaque ligne.
    calc = [set(r.get("conventions") or []) for r in recs.values() if r["status"] == "mesuré" and r.get("conventions")]
    common = {c for c in notes if sum(c in x for x in calc) > len(calc) / 2}  # partagées par la majorité des calculs
    notes = [x for x in notes if x in common] + [x for x in notes if x not in common]

    def status_text(r):
        src = _source(r)
        return src if r["status"] == "mesuré" or r["status"].lower() in src.lower() else f"{src}, {r['status']}"

    def shown(r):
        return "non renseigné" if r["value"] is None and r["status"] == "inconnu" else r["display"]

    def rows(sel):
        out, cur = [], None
        for r in sel:
            g = group(r)
            if g != cur:
                out.append(f'<tr class="grp"><th colspan="6" scope="colgroup">{esc(g[:1].upper() + g[1:])}</th></tr>')
                cur = g
            nref = ", ".join(str(notes.index(c) + 1) for c in (r.get("conventions") or []) if c not in common)
            num = r["unit"] != "text"
            if num or r.get("period"):
                val = (f'<td class="{"n" if num else "t"}{_hyp(r)}">{esc(shown(r))}</td>'
                       f'<td class="per">{esc(_period(r.get("period")))}</td>')
            else:  # texte long sans période : il occupe aussi la colonne Période
                val = f'<td class="t{_hyp(r)}" colspan="2">{esc(shown(r))}</td>'
            out.append(f'<tr id="{esc(r["id"])}"><td class="ref">{esc(r["id"])}</td><td>{esc(_measure(r))}</td>{val}'
                       f'<td class="srcc">{esc(status_text(r))}</td><td class="ref">{esc(nref)}</td></tr>')
        return "".join(out)

    cols = ('<colgroup><col style="width:9%"><col style="width:33%"><col style="width:14%"><col style="width:20%">'
            '<col style="width:17%"><col style="width:7%"></colgroup>')
    head = cols + '<thead><tr><th>Réf.</th><th>Mesure</th><th class="n">Valeur</th><th>Période</th><th>Source</th><th>Notes</th></tr></thead>'
    other = [r for r in items if r["id"] not in cited]
    k = len(common)
    return (
        f'<p class="lead-s">{len(cited & set(recs))} valeurs citées dans ce dossier, regroupées par sujet. '
        + (f"Sauf indication, les valeurs calculées suivent les conventions 1 à {k} ; la colonne Notes indique les conventions propres à une valeur.</p>"
           if k else "La colonne Notes renvoie aux conventions de calcul.</p>")
        + f'<div class="wrap"><table class="tbl reg">{head}<tbody>{rows([r for r in items if r["id"] in cited])}</tbody></table></div>'
        f'<p class="lead-s"><b>Conventions de calcul</b></p><ol class="convs">{"".join(f"<li>{esc(n)}</li>" for n in notes)}</ol>'
        + (f'<details class="data"><summary>{len(other)} autres résultats calculés, non cités</summary>'
           f'<div class="wrap"><table class="tbl reg">{head}<tbody>{rows(other)}</tbody></table></div></details>' if other else "")
    )


# ---------------------------------------------------------------- page

CSS = """
:root{color-scheme:light;--paper:#ffffff;--ink:#111111;--ink-2:#3d3d3d;--ink-3:#6b6b6b;--rule:#111111;--hair:#d9d9d9;--hair-2:#ececec;--tint:#f4f4f2;
--accent:#1d4f91;--gray-1:#4a4a4a;--gray-2:#9c9c9c;--gray-3:#c8c8c8;--bad:#b3261e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--paper:#141414;--ink:#ececea;--ink-2:#c9c9c6;--ink-3:#9a9a96;--rule:#ececea;--hair:#3a3a38;--hair-2:#262625;--tint:#1c1c1b;
--accent:#7fa9e3;--gray-1:#bdbdba;--gray-2:#7c7c79;--gray-3:#4f4f4d;--bad:#f28b82}}
:root[data-theme="dark"]{color-scheme:dark;--paper:#141414;--ink:#ececea;--ink-2:#c9c9c6;--ink-3:#9a9a96;--rule:#ececea;--hair:#3a3a38;--hair-2:#262625;--tint:#1c1c1b;
--accent:#7fa9e3;--gray-1:#bdbdba;--gray-2:#7c7c79;--gray-3:#4f4f4d;--bad:#f28b82}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-variant-numeric:tabular-nums}
a{color:inherit}
.serif,h1,h2,.fig figcaption,.annex>summary{font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif}
.page{max-width:980px;margin:0 auto;padding:0 20px 56px;overflow-wrap:anywhere}
.mast{display:flex;align-items:baseline;gap:16px;border-bottom:2px solid var(--rule);padding:18px 0 8px;font-size:13px;color:var(--ink-2)}
.mast b{color:var(--ink);font-size:15px;letter-spacing:.01em}.mast .sp{flex:1}
.linkbtn{font:inherit;font-size:13px;background:none;border:0;border-bottom:1px solid var(--ink-3);color:var(--ink-2);padding:0;cursor:pointer}
.linkbtn[aria-pressed="true"]{color:var(--accent);border-color:var(--accent)}
h1{font-size:36px;line-height:1.15;font-weight:600;letter-spacing:-.01em;margin:28px 0 10px;max-width:24ch}
.ask{font-size:18px;color:var(--ink-2);margin:0 0 6px;font-style:italic}
.meta{font-size:13px;color:var(--ink-3);margin:0 0 22px}
.profile{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));margin:0;border-top:1px solid var(--hair);border-bottom:1px solid var(--hair)}
.profile div{padding:10px 16px 10px 0}.profile dt{font-size:12px;color:var(--ink-3)}.profile dd{margin:2px 0 0;font-size:15px}
h2{font-size:24px;font-weight:600;margin:44px 0 4px;padding-top:12px;border-top:1px solid var(--hair)}
h2 .no{color:var(--ink-3);font-weight:400;margin-right:10px}
.sub{font-size:14px;color:var(--ink-3);margin:0 0 14px}
.synth{font-size:19px;line-height:1.65;margin:8px 0 10px;max-width:70ch}
.control{font-size:13px;color:var(--ink-3);margin:0 0 6px}.control.ko{color:var(--bad);font-weight:600}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));border-top:2px solid var(--rule);border-bottom:1px solid var(--hair);margin:22px 0 8px}
.kpi{padding:12px 18px 14px 0}.kpi+.kpi{padding-left:18px;border-left:1px solid var(--hair)}
.kpi-l{font-size:13px;color:var(--ink-2);line-height:1.35;min-height:2.7em}
.kpi-v{font-size:30px;line-height:1.2;margin:4px 0 2px}.kpi-v .v{text-decoration:none}
.kpi-d{font-size:13px;color:var(--ink-3)}
.claims{margin:0;padding:0 0 0 22px}.claims li{padding:7px 0;border-bottom:1px solid var(--hair-2);display:grid;grid-template-columns:1fr auto;gap:16px;align-items:baseline}
.claims li::marker{color:var(--ink-3);font-size:14px}.claims p{margin:0;max-width:72ch}
.stw{font-size:12px;color:var(--ink-3);white-space:nowrap;position:relative}
.v{text-decoration:underline dotted var(--ink-3);text-underline-offset:3px;text-decoration-thickness:1px;position:relative}
.v.num{white-space:nowrap;font-weight:600}.v.txt{text-decoration:none}.v.txt:hover{text-decoration:underline dotted}.v.hyp{font-style:italic}.v.unk{color:var(--ink-3);font-style:italic}
.v:hover,.v:focus-visible{color:var(--accent);text-decoration-color:var(--accent)}
.rid{display:none;font-size:10px;font-weight:400;font-style:normal;color:var(--ink-3);margin-left:2px}body.show-ids .rid{display:inline}
.cmp{text-decoration:underline dotted var(--ink-3);text-underline-offset:3px;position:relative}
[data-tip]:hover::after,[data-tip]:focus-visible::after{content:attr(data-tip);position:absolute;left:0;top:calc(100% + 4px);z-index:30;width:max-content;max-width:300px;white-space:normal;
background:var(--ink);color:var(--paper);font:400 12px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-style:normal;padding:6px 8px;text-align:left}
.stw[data-tip]:hover::after{left:auto;right:0}
.bad{color:var(--bad);font-weight:700}
.fig{margin:22px 0 8px}.fig figcaption{font-size:17px;font-weight:600;border-top:2px solid var(--rule);padding-top:8px;margin-bottom:8px}
.fignum{font-weight:700;margin-right:6px}.unit{display:block;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:13px;font-weight:400;color:var(--ink-3)}
.legend{display:flex;flex-wrap:wrap;gap:16px;font-size:13px;color:var(--ink-2);margin-bottom:4px}.key i{display:inline-block;width:16px;height:3px;margin-right:6px;vertical-align:middle}
.plot{position:relative}.fig svg{width:100%;height:auto;display:block}
.grid{stroke:var(--hair-2);stroke-width:1}.zero{stroke:var(--ink);stroke-width:1}.tick{stroke:var(--ink-3)}.ax{fill:var(--ink-3);font-size:11px}
.cat{fill:var(--ink-2);font-size:12px}.bl{fill:var(--ink-2);font-size:11px}.dl{font-size:12px;font-weight:600}.ref{stroke:var(--ink-2);stroke-dasharray:3 3}.cross{stroke:var(--ink-3)}
.tooltip{position:absolute;top:6px;pointer-events:none;background:var(--ink);color:var(--paper);font-size:12px;padding:6px 8px;white-space:nowrap;line-height:1.5}
.srcnote{border-top:1px solid var(--hair);margin-top:6px;padding-top:6px;font-size:12px;color:var(--ink-3)}.srcnote p{margin:1px 0}.srcnote span{font-weight:600;color:var(--ink-2)}
.srcnote .refs{display:none}body.show-ids .srcnote .refs{display:block}.srcnote a{color:var(--ink-3)}
.wrap{overflow-x:auto}
.tbl{border-collapse:collapse;width:100%;font-size:14px;overflow-wrap:normal}.opts{min-width:720px}.opts th[scope=row]{min-width:190px;width:24%}.tbl th,.tbl td{padding:6px 10px;text-align:left;vertical-align:baseline;border-bottom:1px solid var(--hair-2)}
.tbl thead th{font-size:12px;font-weight:600;color:var(--ink-2);border-bottom:1px solid var(--rule);vertical-align:bottom}
.tbl tbody tr:last-child td,.tbl tbody tr:last-child th{border-bottom:1px solid var(--rule)}
.tbl .n{text-align:right;white-space:nowrap}.tbl thead th.n{white-space:normal}.tbl th[scope=row]{font-weight:600}.tbl td.hyp{font-style:italic}
.opts tbody tr:hover th,.opts tbody tr:hover td{background:var(--tint)}
.tbl .v{font-weight:400;text-decoration:none}.tbl .v:hover{text-decoration:underline dotted}
.reg{font-size:13px;table-layout:fixed;min-width:760px}.reg .grp th{font-weight:700;padding-top:14px;color:var(--ink);border-bottom:1px solid var(--hair)}
.reg .ref{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;color:var(--ink-3);white-space:nowrap}.reg .per{color:var(--ink-3);white-space:nowrap}.reg td.t{max-width:36ch}
.reg tr:target td{background:var(--tint)}.reg .srcc{color:var(--ink-3)}.trace{font-size:13px}.trace .ref{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px}.trace .per{color:var(--ink-3)}
.lead-s{font-size:13px;color:var(--ink-2);margin:6px 0}.convs{font-size:12px;color:var(--ink-3);margin:4px 0 12px;padding-left:22px}
details.data{margin-top:8px}details.data summary{cursor:pointer;font-size:13px;color:var(--ink-2)}
.annex{margin-top:52px;border-top:2px solid var(--rule)}.annex>summary{font-size:20px;font-weight:600;padding:12px 0;cursor:pointer}
.annex h3{font-size:15px;margin:22px 0 6px}.annex p,.annex li{font-size:14px}
.legend-st{display:grid;grid-template-columns:max-content 1fr;gap:2px 14px;font-size:13px;color:var(--ink-2)}.legend-st b{font-weight:600;color:var(--ink)}
footer{max-width:980px;margin:0 auto;padding:16px 20px 40px;font-size:12px;color:var(--ink-3);border-top:1px solid var(--hair)}
@media (max-width:640px){h1{font-size:27px}.synth{font-size:17px}.kpi+.kpi{padding-left:0;border-left:0;border-top:1px solid var(--hair)}.claims li{grid-template-columns:1fr;gap:0}}
"""

JS = """
document.querySelectorAll('svg[data-line]').forEach(svg=>{
  const d=JSON.parse(svg.dataset.line),L=+svg.dataset.l,R=+svg.dataset.r,W=+svg.dataset.w,n=d.x.length;
  const tip=svg.parentElement.querySelector('.tooltip'),cross=svg.querySelector('.cross');
  const fmt=v=>(v*100).toFixed(1).replace('.',',').replace('-','\\u2212')+'\\u00a0%';
  svg.addEventListener('mousemove',e=>{const r=svg.getBoundingClientRect(),px=(e.clientX-r.left)*W/r.width;
    const i=Math.max(0,Math.min(n-1,Math.round((px-L)/(W-L-R)*(n-1))));const x=L+i*(W-L-R)/(n-1);
    cross.setAttribute('x1',x);cross.setAttribute('x2',x);cross.setAttribute('visibility','visible');
    tip.hidden=false;tip.innerHTML='<b>'+d.x[i]+'</b><br>'+Object.entries(d.series).map(([k,v])=>k+' : '+fmt(v[i])).join('<br>');
    const left=(x/W)*r.width;tip.style.left=(left>r.width*0.6?left-tip.offsetWidth-12:left+12)+'px';});
  svg.addEventListener('mouseleave',()=>{tip.hidden=true;cross.setAttribute('visibility','hidden');});
});
const b=document.getElementById('ids');if(b){b.addEventListener('click',()=>{const on=document.body.classList.toggle('show-ids');b.setAttribute('aria-pressed',on);});}
document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(!a)return;const t=document.getElementById(a.getAttribute('href').slice(1));
  if(!t)return;let p=t.parentElement;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}});
"""

SECTION_TITLES = [
    ("profil", "Profil et demande", "Ce que l'énoncé déclare, ce que le scénario suppose, ce qui manque."),
    ("constat", "Ce que montrent les données", "Mesures historiques en dollars canadiens sur la période observée ; elles décrivent le passé."),
    ("tension", "Tensions avec le profil", "Où la demande s'écarte de l'objectif ou des préférences déclarées."),
    ("alternative", "Options comparées", "Portefeuilles fictifs comparés sur la même base."),
    ("question", "Information décisive manquante", ""),
    ("condition", "Ce qui ferait changer la conclusion", ""),
    ("limite", "Limites", ""),
]


def render(d: dict) -> str:
    recs = d["enregistrements"]
    ver = d["verification"]
    by: dict[str, list] = {}
    for c in d["affirmations"]:
        by.setdefault(c["section"], []).append(c)

    figs = "".join(line_chart(c, k + 1) if c["type"] == "ligne" else bar_chart(c, k + 1) for k, c in enumerate(d.get("graphiques", [])))
    tabs, _ = tables(d, recs, 0)
    body, n = [], 0
    for key, title, sub in SECTION_TITLES:
        items = by.get(key, [])
        extra = figs if key == "constat" else tabs if key == "alternative" else ""
        if not items and not extra:
            continue
        n += 1
        body.append(f'<h2><span class="no">{n}</span>{esc(title)}</h2>' + (f'<p class="sub">{esc(sub)}</p>' if sub else "")
                    + (extra if key == "alternative" else "") + (claims(items, recs) if items else "") + (extra if key == "constat" else ""))

    ok = ver["ok"]
    control = (f'<p class="control">Contrôle automatique : les {ver["valeurs_reliees"]} valeurs citées proviennent du registre de calcul ; '
               "aucun chiffre ni sens de comparaison n'est saisi à la main. Survolez une valeur pour voir sa source.</p>"
               if ok else f'<p class="control ko">Contrôle automatique : {len(ver["affirmations_en_echec"])} élément(s) en échec, voir l\'annexe.</p>')
    aws = d.get("aws") or {}
    if aws:
        calls = "".join(f'<tr><td class="ref">{esc(c.get("requestId"))}</td><td class="n">{esc(c.get("inputTokens"))}</td><td class="n">{esc(c.get("outputTokens"))}</td>'
                        f'<td class="n">{esc(c.get("latenceMs"))}</td><td>{esc(c.get("stopReason"))}</td></tr>' for c in aws.get("appels", []))
        aws_html = (f"<p>{esc(aws.get('service'))}, modèle <code>{esc(aws.get('modele'))}</code>, région <code>{esc(aws.get('region'))}</code> ; "
                    f"corrections demandées par le vérificateur : {esc(aws.get('corrections_demandees'))}.</p>"
                    f'<div class="wrap"><table class="tbl reg"><thead><tr><th>RequestId</th><th class="n">Jetons entrée</th><th class="n">Jetons sortie</th>'
                    f'<th class="n">Latence (ms)</th><th>Arrêt</th></tr></thead><tbody>{calls}</tbody></table></div>')
    else:
        aws_html = f"<p>Exécution locale, sans appel AWS ({esc(d['mode'])}).</p>"
    trace_rows = "".join(
        f'<tr><td class="n">{i + 1}</td><td class="ref">{esc(t["outil"])}</td><td class="per">{esc(json.dumps(t["arguments"], ensure_ascii=False)[:110])}</td>'
        f'<td class="n">{len(t["enregistrements"])}</td><td class="n">{t["duree_ms"]}</td><td>{esc(t.get("erreur", ""))}</td></tr>'
        for i, t in enumerate(d["trace"])
    )
    problems = "" if ok else "<h3>Éléments en échec</h3><pre>" + esc(json.dumps(ver["problemes"], ensure_ascii=False, indent=2)) + "</pre>"
    legend = "".join(f"<b>{esc(k)}</b><span>{esc(v)}</span>" for k, v in STATUS_HELP.items())
    cadre = " ".join(c["texte"] for c in by.get("cadre", []))
    persona = d["persona"].capitalize()

    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(d.get('titre') or d['scenario'])} — AlphaForge</title><style>{CSS}</style></head>
<body><div class="page">
<div class="mast"><b>AlphaForge</b><span>Dossier de décision</span><span class="sp"></span><button class="linkbtn" id="ids" aria-pressed="false">Afficher les références</button></div>
<h1>{esc(d.get('titre') or d['scenario'])}</h1>
<p class="ask">« {esc(d['demande'])} »</p>
<p class="meta">Profil fictif : {esc(persona)} · Établi le {esc(_date_fr(d['cree_le']))} · {esc(d['mode'])} · Simulation, aucun conseil personnalisé</p>
{profile_card(d, recs)}
<h2>Synthèse</h2>
<p class="synth">{render_html(d['resume']['gabarit'], recs)}</p>
{control}
{kpis(d, recs)}
{''.join(body)}
<details class="annex"><summary>Annexe — registre des preuves, méthode et trace d'exécution</summary>
<h3>Registre des preuves</h3>{registry(d, recs)}
<h3>Statuts</h3><div class="legend-st">{legend}</div>
<p class="lead-s">En italique : valeur fixée par hypothèse ou scénario de démonstration. Grisé : information non fournie.</p>
<h3>Contribution AWS</h3>{aws_html}
{problems}
<h3>Trace d'exécution</h3><div class="wrap"><table class="tbl trace"><thead><tr><th class="n">#</th><th>Outil</th><th>Arguments</th><th class="n">Enregistrements</th><th class="n">Durée (ms)</th><th>Erreur</th></tr></thead><tbody>{trace_rows}</tbody></table></div>
</details>
</div>
<footer>{esc(cadre)}</footer>
<script>{JS}</script></body></html>"""


def render_index(dossiers: list[dict]) -> str:
    items = "".join(
        f'<li><a href="{esc(d["_lien"])}"><span class="serif" style="font-size:21px;font-weight:600">{esc(d.get("titre") or d["scenario"])}</span></a>'
        f'<p class="meta" style="margin:2px 0 6px">Profil fictif : {esc(d["persona"].capitalize())} · {esc(d["mode"])} · '
        f'contrôle : {"conforme" if d["verification"]["ok"] else "en échec"}, {d["verification"]["valeurs_reliees"]} valeurs reliées</p>'
        f'<p style="margin:0;max-width:72ch;color:var(--ink-2)">{esc(d["resume"]["texte"])}</p></li>'
        for d in dossiers
    )
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dossiers AlphaForge</title><style>{CSS}.idx{{list-style:none;padding:0;margin:0}}.idx li{{padding:18px 0;border-bottom:1px solid var(--hair)}}.idx a{{text-decoration:none}}.idx a:hover{{color:var(--accent)}}</style></head>
<body><div class="page"><div class="mast"><b>AlphaForge</b><span>Laboratoire de décision d'investissement</span></div>
<h1>Dossiers de décision</h1><p class="meta">Simulation sur profils fictifs. Chaque conclusion est reliée aux calculs et aux hypothèses qui la soutiennent.</p>
<ul class="idx">{items}</ul></div></body></html>"""
