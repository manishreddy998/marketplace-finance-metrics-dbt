select payment_id::int payment_id, merchant_id::int merchant_id, payment_date::date payment_date, gpv::double gpv, method from {{ ref('raw_payments') }}
