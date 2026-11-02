-- Monthly MRR bridge. Contract: opening + new + expansion - churn = closing.
with cur as (select month, merchant_id, sum(mrr) mrr from {{ ref('fct_mrr_monthly') }} group by 1,2),
j as (
  select coalesce(c.month, (p.month + interval 1 month)::date) as month, coalesce(c.merchant_id,p.merchant_id) merchant_id, coalesce(p.mrr,0) prev_mrr, coalesce(c.mrr,0) mrr
  from cur c full outer join cur p on c.merchant_id=p.merchant_id and c.month = (p.month + interval 1 month)::date)
select month, sum(prev_mrr) opening_mrr,
  sum(case when prev_mrr=0 and mrr>0 then mrr else 0 end) new_mrr,
  sum(case when prev_mrr>0 and mrr>0 then mrr-prev_mrr else 0 end) expansion_mrr,
  sum(case when prev_mrr>0 and mrr=0 then prev_mrr else 0 end) churned_mrr,
  sum(mrr) closing_mrr
from j where month <= date '2025-12-01' group by 1 order by 1
