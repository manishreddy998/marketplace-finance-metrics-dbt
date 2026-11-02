select * from {{ ref('mrr_movements') }} where abs(opening_mrr + new_mrr + expansion_mrr - churned_mrr - closing_mrr) > 0.01
