"""Parse already collected public notebook responses; no model or new HTTP call."""
import csv
from datetime import date
import hashlib
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CACHE = ROOT / "docs/recherche/collecte"
SOURCES = HERE.parent / "sources"


def cached(uid):
    m = json.loads((CACHE / (uid + ".json")).read_text())
    p = ROOT / "docs/recherche" / m["local_raw"]
    return p, m


fx_path, fx_meta = cached("U366")
fx = json.loads(fx_path.read_text())
obs = fx["observations"]
fx_records = [(r["d"], float(r["FXUSDCAD"]["v"])) for r in obs]
assert all(v > 0 for _, v in fx_records)
assert fx_records == sorted(fx_records)
assert len({d for d, _ in fx_records}) == len(fx_records)

fred_path = SOURCES / "fred_notebook.raw"
fred = list(csv.DictReader(io.StringIO(fred_path.read_text())))
value_rows = [r for r in fred if r.get("DGS10") not in ("", ".", None)]
assert value_rows and all(float(r["DGS10"]) >= 0 for r in value_rows)
fred_date_key = next(k for k in fred[0] if k != "DGS10")

sec_path, sec_meta = cached("U369")
sec = json.loads(sec_path.read_text())
revenue = sec["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
annual = [r for r in revenue if r["form"] == "10-K"
          and 350 <= (date.fromisoformat(r["end"]) - date.fromisoformat(r["start"])).days <= 380]
groups = {}
for r in annual:
    groups.setdefault(r["end"], []).append(r)
duplicates = [{"end":end, "count":len(rs),
               "filing_dates":sorted({r["filed"] for r in rs}),
               "values":sorted({r["val"] for r in rs})}
              for end, rs in sorted(groups.items()) if len(rs)>1]

result = {
    "scope": "Local parsing of public responses, not execution of the notebook.",
    "fx": {"source_id":"U366", "sha256":hashlib.sha256(fx_path.read_bytes()).hexdigest(),
           "rows":len(obs), "first":fx_records[0], "last":fx_records[-1],
           "series_detail":fx.get("seriesDetail",{}),
           "weekend_rows":sum(date.fromisoformat(d).weekday()>=5 for d,_ in fx_records),
           "lookahead_limit":"Reference dates and positive values do not establish historical publication times."},
    "fred": {"url":"https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10",
             "sha256":hashlib.sha256(fred_path.read_bytes()).hexdigest(),
             "date_column":fred_date_key, "rows":len(fred), "nonnull":len(value_rows),
             "first_nonnull":value_rows[0], "last_nonnull":value_rows[-1],
             "limit":"CSV is latest available series; no vintage or release-time columns."},
    "sec": {"source_id":"U369", "entity":sec["entityName"], "cik":sec["cik"],
            "annual_rows":len(annual), "distinct_end_dates":len(groups),
            "duplicate_end_groups":duplicates,
            "limit":"A duplicate period can reflect re-filings/comparatives, not necessarily value revision. Filter filed<=cutoff and select a documented form/unit/context."},
    "annualization_counterexample": {
        "returns":[.5,-.5], "mean_compounded_two_intervals":0.,
        "actual_two_interval_return":-.25,
        "meaning":"Compounding an arithmetic mean is not the observed geometric return."}
}
(HERE / "notebook_inputs.json").write_text(json.dumps(result, indent=2, allow_nan=False))
print(json.dumps(result, indent=2))
