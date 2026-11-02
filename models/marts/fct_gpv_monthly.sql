select date_trunc('month',payment_date)::date as month, m.region, m.segment, sum(gpv) gpv, count(*) payments, count(distinct p.merchant_id) active_merchants
from {{ ref('stg_payments') }} p join {{ ref('stg_merchants') }} m using (merchant_id) group by 1,2,3
