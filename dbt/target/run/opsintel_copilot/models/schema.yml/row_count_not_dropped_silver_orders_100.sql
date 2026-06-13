
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
SELECT COUNT(*) AS row_count
FROM `workspace`.`opsintel_copilot`.`silver_orders`
HAVING COUNT(*) < 100

  
  
      
    ) dbt_internal_test