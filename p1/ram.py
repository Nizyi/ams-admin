import psutil
import json

ram_py = { "ram_usage" : psutil.virtual_memory().percent}

ram=json.dumps(ram_py)

print(ram)