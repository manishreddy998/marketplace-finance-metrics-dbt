select f.* from {{ ref('fct_mrr_monthly') }} f join {{ ref('stg_subscriptions') }} s using (merchant_id) where s.end_date is not null and f.month >= s.end_date
