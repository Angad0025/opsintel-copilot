
      
  
    
        create or replace table `workspace`.`opsintel_copilot_snapshots`.`incident_status_snapshot`
      
      
    using delta
  
      
      
      
      
      
      
      
      
      as
      select *,
        md5(coalesce(cast(event_id as string ), '')
         || '|' || coalesce(cast(
    current_timestamp()
 as string ), '')
        ) as dbt_scd_id,
        
    current_timestamp()
 as dbt_updated_at,
        
    current_timestamp()
 as dbt_valid_from,
        
  
  coalesce(nullif(
    current_timestamp()
, 
    current_timestamp()
), null)
  as dbt_valid_to

    from (
        SELECT
    event_id,
    event_type,
    user_email,
    is_brute_force,
    is_escalation,
    is_impossible_travel,
    event_time
FROM `workspace`.`opsintel_copilot`.`silver_security_logs`
    ) sbq


  
  