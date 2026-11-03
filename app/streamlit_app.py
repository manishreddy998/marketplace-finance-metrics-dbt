import duckdb, streamlit as st
from pathlib import Path
D = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="Metrics layer", layout="wide")
st.title("Finance metrics layer on real marketplace data")
st.caption("GPV from real Olist order lines (BRL). MRR is derived from seller activity with an ASSUMED flat R$99 plan, see README.")
c = duckdb.connect(str(D / "ls.duckdb"), read_only=True)
g = c.sql("select month, sum(gpv) gpv from fct_gpv_monthly group by 1 order by 1").df()
m = c.sql("select * from mrr_movements order by month").df()
a, b, k = st.columns(3)
a.metric("Total GPV (BRL)", f"{g.gpv.sum():,.0f}"); b.metric("Closing MRR Aug 2018 (assumed fee)", f"{m.closing_mrr.iloc[-1]:,.0f}")
k.metric("Bridge rows that do not balance", int(((m.opening_mrr + m.new_mrr + m.expansion_mrr - m.churned_mrr - m.closing_mrr).abs() > 0.01).sum()))
l, r = st.columns(2)
l.subheader("Monthly GPV"); l.bar_chart(g, x="month", y="gpv")
r.subheader("MRR bridge"); r.dataframe(m.tail(12), use_container_width=True, hide_index=True)
