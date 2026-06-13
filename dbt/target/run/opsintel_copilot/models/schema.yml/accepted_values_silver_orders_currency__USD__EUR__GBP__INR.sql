
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        currency as value_field,
        count(*) as n_records

    from `workspace`.`opsintel_copilot`.`silver_orders`
    group by currency

)

select *
from all_values
where value_field not in (
    'USD','EUR','GBP','INR'
)



  
  
      
    ) dbt_internal_test