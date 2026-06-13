SELECT
    order_id,
    customer_id,
    service_name,
    order_status,
    amount,
    currency,
    region,
    created_at,
    updated_at,
    payment_method,
    is_priority_order
FROM {{ ref('stg_orders') }}
WHERE {{ is_valid_timestamp('created_at') }}
  AND {{ is_valid_currency('currency') }}
  AND amount > 0
  AND order_id IS NOT NULL
