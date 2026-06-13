
  
    
        create or replace table `workspace`.`opsintel_copilot`.`gold_data_quality_results`
      
      
    using delta
  
      
      
      
      
      
      
      
      
      as
      SELECT
    order_id,
    amount,
    currency,
    created_at,
    CASE
        WHEN amount <= 0    THEN 'negative_amount'
        WHEN amount > 10000 THEN 'suspicious_amount'
        ELSE 'ok'
    END                 AS quality_flag,
    CURRENT_TIMESTAMP() AS checked_at
FROM `workspace`.`opsintel_copilot`.`silver_orders`
  