
  
    
        create or replace table `workspace`.`opsintel_copilot`.`silver_admin_events`
      
      
    using delta
  
      
      
      
      
      
      
      
      
      as
      SELECT
    admin_event_id,
    admin_user,
    action,
    target_service,
    region,
    event_time,
    
    CASE WHEN action = 'config_change' THEN TRUE ELSE FALSE END
        AS is_config_change,
    
    CASE WHEN action = 'privilege_escalation' THEN TRUE ELSE FALSE END
 AS is_escalation,
    
    CASE WHEN action = 'user_deletion' THEN TRUE ELSE FALSE END
        AS is_user_deletion
FROM `workspace`.`opsintel_copilot`.`stg_admin_events`
WHERE 
    event_time IS NOT NULL
    AND event_time >= '2020-01-01'
    AND event_time <= CURRENT_TIMESTAMP()

  AND admin_event_id IS NOT NULL
  