-- One row per merchant per active month. MRR counts in a month if the subscription was active on the first day.
with months as (select unnest(generate_series(date '2016-09-01', date '2018-08-01', interval 1 month))::date as month)
select m.month, s.merchant_id, s.plan, s.mrr
from months m join {{ ref('stg_subscriptions') }} s
  on s.start_date <= m.month and (s.end_date is null or s.end_date > m.month)
