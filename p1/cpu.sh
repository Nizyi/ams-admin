cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | tr -d '%')

json_output=$(echo "{\"cpu_usage\": $cpu_usage}")

echo $json_output