
    
    

select
    admin_event_id as unique_field,
    count(*) as n_records

from `workspace`.`opsintel_copilot`.`silver_admin_events`
where admin_event_id is not null
group by admin_event_id
having count(*) > 1


