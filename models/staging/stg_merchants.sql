select merchant_id::int merchant_id, region, segment, signup_date::date signup_date from {{ ref('raw_merchants') }}
