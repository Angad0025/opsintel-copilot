
  
    
        create or replace table `workspace`.`opsintel_copilot`.`silver_security_logs`
      
      
    using delta
  
      
      
      
      
      
      
      
      
      as
      SELECT
    event_id,
    event_type,
    user_email,
    source_ip,
    region,
    event_time,
    success,
    
    CASE WHEN event_type = 'brute_force' THEN TRUE ELSE FALSE END
          AS is_brute_force,
    
    CASE WHEN event_type = 'privilege_escalation' THEN TRUE ELSE FALSE END
  AS is_escalation,
    
    CASE WHEN event_type = 'impossible_travel' THEN TRUE ELSE FALSE END
     AS is_impossible_travel,
    
    CASE WHEN event_type = 'large_data_export' THEN TRUE ELSE FALSE END
     AS is_large_export,
    
    CASE WHEN event_type = 'api_token_rotation' THEN TRUE ELSE FALSE END
    AS is_token_rotation
FROM `workspace`.`opsintel_copilot`.`stg_security_logs`
WHERE 
    event_time IS NOT NULL
    AND event_time >= '2020-01-01'
    AND event_time <= CURRENT_TIMESTAMP()

  AND event_id IS NOT NULL
  