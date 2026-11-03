"""Build dbt seeds from the REAL Olist Brazilian e-commerce dataset (Kaggle olistbr, CC BY-NC-SA 4.0,
raw CSVs mirrored at huggingface.co/datasets/bulutttt/olist-raw-data).
merchants = Olist marketplace sellers, payments = real order line items (price in BRL) of orders
that were not cancelled or unavailable. Olist sellers do pay a monthly plan, but the fee is NOT in
the data, so subscriptions are DERIVED: start = month of first sale, end = 90 days after last
sale if the seller stopped selling before 2018-06-01, MRR = assumed flat R$99. That part is a
labelled assumption, not real revenue."""
import csv, sys, datetime as dt
from collections import defaultdict
src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/olist"
orders = {r["order_id"]: r for r in csv.DictReader(open(f"{src}/olist_orders_dataset.csv"))}
ptype = {}
for r in csv.DictReader(open(f"{src}/olist_order_payments_dataset.csv")):
    ptype.setdefault(r["order_id"], r["payment_type"])
sellers = {r["seller_id"]: r for r in csv.DictReader(open(f"{src}/olist_sellers_dataset.csv"))}
sid = {s: i + 1 for i, s in enumerate(sorted(sellers))}
P, first, last = [], {}, {}
for r in csv.DictReader(open(f"{src}/olist_order_items_dataset.csv")):
    o = orders[r["order_id"]]
    if o["order_status"] in ("canceled", "unavailable"): continue
    d = dt.date.fromisoformat(o["order_purchase_timestamp"][:10]); m = sid[r["seller_id"]]
    P.append([len(P) + 1, m, d, r["price"], ptype.get(r["order_id"], "unknown")])
    first[m] = min(first.get(m, d), d); last[m] = max(last.get(m, d), d)
M = [[sid[s], sellers[s]["seller_state"], "marketplace_seller", first[sid[s]]] for s in sorted(sellers) if sid[s] in first]
S = [[m, m, "olist_plan_assumed", 99, f.replace(day=1), (last[m] + dt.timedelta(days=90)) if last[m] < dt.date(2018, 6, 1) else ""] for m, _, _, f in M]
for n, h, rows in [("raw_merchants", ["merchant_id", "region", "segment", "signup_date"], M),
                   ("raw_subscriptions", ["subscription_id", "merchant_id", "plan", "mrr", "start_date", "end_date"], S),
                   ("raw_payments", ["payment_id", "merchant_id", "payment_date", "gpv", "method"], P)]:
    w = csv.writer(open(f"seeds/{n}.csv", "w", newline="")); w.writerow(h); w.writerows(rows)
print(len(M), len(S), len(P), round(sum(float(p[3]) for p in P), 2))
