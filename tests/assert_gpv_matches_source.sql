select 1 where abs((select sum(gpv) from {{ ref('fct_gpv_monthly') }}) - (select sum(gpv) from {{ ref('stg_payments') }})) > 0.01
