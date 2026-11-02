# dbt finance and GTM metrics layer with contracts

**Problem.** For a POS company like Lightspeed, MRR, churn and GPV must mean the same thing in Looker, in finance decks and in AI tools reading the docs. This prototype is a small dbt project that defines those metrics once and tests that they reconcile.

**Architecture.** `scripts/make_seeds.py` creates seeded synthetic data with 800 merchants, 800 subscriptions and 14,261 payments. There are staging views, an enforced contract on `fct_mrr_monthly`, an MRR bridge (`mrr_movements`) and `fct_gpv_monthly`. Custom tests check 3 things. Opening plus new plus expansion minus churn must equal closing for every month. GPV in the mart must equal GPV in the source. No MRR may appear after a churn date. DuckDB runs it locally, and the same SQL runs on BigQuery.

**Results** (`dbt build --profiles-dir .`)

| item | value |
|---|---|
| dbt build | PASS 24, ERROR 0 (3 seeds, 6 models, 15 tests), 3.9 s |
| merchant months in fct_mrr_monthly | 9,881 |
| Dec 2025 MRR bridge | opening 336,470, churned 7,009, closing 329,461 |
| 2025 churned MRR total | 51,839 |

**Limits.** The seeds have no plan changes, so expansion is 0. A real version would add upgrades, currency conversion and a semantic layer for Looker.
