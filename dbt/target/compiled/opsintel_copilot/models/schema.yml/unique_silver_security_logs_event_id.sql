
    
    

select
    event_id as unique_field,
    count(*) as n_records

from `workspace`.`opsintel_copilot`.`silver_security_logs`
where event_id is not null
group by event_id
having count(*) > 1


