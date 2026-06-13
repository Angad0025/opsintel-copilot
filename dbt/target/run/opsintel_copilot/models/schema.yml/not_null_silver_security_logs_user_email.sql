
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select user_email
from `workspace`.`opsintel_copilot`.`silver_security_logs`
where user_email is null



  
  
      
    ) dbt_internal_test