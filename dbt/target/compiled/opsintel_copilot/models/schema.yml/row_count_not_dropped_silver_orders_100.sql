
SELECT COUNT(*) AS row_count
FROM `workspace`.`opsintel_copilot`.`silver_orders`
HAVING COUNT(*) < 100
