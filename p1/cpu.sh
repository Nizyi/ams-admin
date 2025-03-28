cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | tr -d '%' | tr ',' '.')
json_output=$(jq -n --arg usage "$cpu_usage" '{"cpu_usage": ($usage|tonumber)}')
echo $json_output