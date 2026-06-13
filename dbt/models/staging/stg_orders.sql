SELECT
    CAST(order_id          AS STRING)        AS order_id,
    CAST(customer_id       AS STRING)        AS customer_id,
    CAST(service_name      AS STRING)        AS service_name,
    CAST(order_status      AS STRING)        AS order_status,
    CAST(amount            AS DECIMAL(18,2)) AS amount,
    UPPER(currency)                          AS currency,
    CAST(region            AS STRING)        AS region,
    CAST(created_at        AS TIMESTAMP)     AS created_at,
    CAST(updated_at        AS TIMESTAMP)     AS updated_at,
    CAST(payment_method    AS STRING)        AS payment_method,
    CAST(is_priority_order AS BOOLEAN)       AS is_priority_order
FROM {{ source('bronze', 'bronze_orders') }}
WHERE order_id IS NOT NULL
