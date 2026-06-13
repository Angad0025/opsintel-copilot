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
FROM `workspace`.`opsintel_copilot`.`stg_orders`
WHERE 
    created_at IS NOT NULL
    AND created_at >= '2020-01-01'
    AND created_at <= CURRENT_TIMESTAMP()

  AND 
    currency IN ('USD', 'EUR', 'GBP', 'INR')

  AND amount > 0
  AND order_id IS NOT NULL