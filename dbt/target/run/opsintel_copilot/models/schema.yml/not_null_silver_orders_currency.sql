
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select currency
from `workspace`.`opsintel_copilot`.`silver_orders`
where currency is null



  
  
      
    ) dbt_internal_test