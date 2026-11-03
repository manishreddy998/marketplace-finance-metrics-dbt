"""Can a local LLM answer finance questions correctly from this metrics layer?
Qwen2.5 3B writes one DuckDB SQL query per question. Two settings:
  raw   = only the raw seed tables and their columns (what an AI tool sees without dbt)
  marts = the dbt marts with their Finance definitions from models/schema.yml
Gold answers come from hand written SQL on the marts. An answer is correct if it is within 0.5%."""
import json, re, duckdb
from pathlib import Path
from .llm import get_backend
D = Path(__file__).resolve().parent.parent
Q = [
 ("Total GPV in BRL across all months?", "select sum(gpv) from fct_gpv_monthly"),
 ("Total GPV in BRL for sellers in state RJ?", "select sum(gpv) from fct_gpv_monthly where region='RJ'"),
 ("GPV in BRL in November 2017?", "select sum(gpv) from fct_gpv_monthly where month='2017-11-01'"),
 ("Number of active merchants (with at least one payment) in March 2018?", "select count(distinct merchant_id) from stg_payments where date_trunc('month',payment_date)='2018-03-01'"),
 ("Closing MRR for August 2018?", "select closing_mrr from mrr_movements where month='2018-08-01'"),
 ("Total churned MRR in 2018?", "select sum(churned_mrr) from mrr_movements where year(month)=2018"),
 ("New MRR in January 2018?", "select new_mrr from mrr_movements where month='2018-01-01'"),
 ("Opening MRR for June 2018?", "select opening_mrr from mrr_movements where month='2018-06-01'"),
 ("Number of payments (order lines) paid by boleto?", "select count(*) from stg_payments where method='boleto'"),
 ("Average GPV per payment in BRL in 2017?", "select avg(gpv) from stg_payments where year(payment_date)=2017"),
]
RAW = "Tables: raw_merchants(merchant_id, region, segment, signup_date), raw_subscriptions(subscription_id, merchant_id, plan, mrr, start_date, end_date), raw_payments(payment_id, merchant_id, payment_date, gpv, method)."
MARTS = (RAW.replace("raw_", "stg_") + " Also: fct_gpv_monthly(month, region, segment, gpv, payments, active_merchants); "
         "mrr_movements(month, opening_mrr, new_mrr, expansion_mrr, churned_mrr, closing_mrr) is the Finance MRR bridge, "
         "use it for any MRR question. In both marts the column is named month and holds the first day of the month as a DATE, e.g. month = DATE '2018-01-01'. MRR counts in a month if the subscription was active on the first day.")
SYS = "You write one DuckDB SQL query that answers the question. Reply JSON {\"sql\": \"...\"}."


def val(c, sql):
    try: return float(c.sql(sql).fetchone()[0])
    except Exception: return None


def run():
    c = duckdb.connect(str(D / "ls.duckdb"), read_only=True); be = get_backend(); out = {}
    for name, ctx in (("raw", RAW), ("marts", MARTS)):
        rows = []
        for q, gold in Q:
            g = val(c, gold)
            try: sql = be.complete_json(SYS, f"{ctx}\nQuestion: {q}", 160).get("sql", "")
            except KeyError: raise
            except Exception: sql = ""
            v = val(c, sql) if sql else None
            rows.append({"q": q, "gold": g, "got": v, "sql": sql, "ok": v is not None and g is not None and abs(v - g) <= abs(g) * 0.005})
        out[name] = {"correct": sum(r["ok"] for r in rows), "of": len(rows), "rows": rows}
    (D / "docs/llm_sql_results.json").write_text(json.dumps(out, indent=1, default=str))
    print({k: f"{v['correct']}/{v['of']}" for k, v in out.items()}); return out

if __name__ == "__main__": run()
