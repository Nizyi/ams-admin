import psutil
import json

disk_py = { "disk_usage": psutil.disk_usage('/').percent,
            "disk_free": psutil.disk_usage('/').free / (1024**3),  # Conversion en GB
            "disk_total": psutil.disk_usage('/').total / (1024**3)  # Conversion en GB
}

disk=json.dumps(disk_py)

print(disk)