
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select admin_event_id
from `workspace`.`opsintel_copilot`.`silver_admin_events`
where admin_event_id is null



  
  
      
    ) dbt_internal_test