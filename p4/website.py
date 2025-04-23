import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime

import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, redirect, url_for

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from p3.alertes import GraphGenerator

app = Flask(__name__)



@app.route('/')
def index():
    try:
        # Correct path to database
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'p2', 'alertes.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        latest_stats = {
            'cpu': 0,
            'ram': 0,
            'disk': 0
        }

        alertes = []

        # Fixed column names to match your storage_manager.py schema
        cursor.execute("SELECT value FROM sonde WHERE sonde_name='cpu' ORDER BY timestamp DESC LIMIT 1")
        cpu_result = cursor.fetchone()
        if cpu_result:
            # Parse the JSON string to extract the cpu_usage value
            import json
            cpu_data = json.loads(cpu_result[0])
            latest_stats['cpu'] = round(float(cpu_data.get('cpu_usage', 0)), 1)
            print(f"CPU data retrieved: {latest_stats['cpu']}%")

        # Fixed query for RAM
        cursor.execute("SELECT value FROM sonde WHERE sonde_name='ram' ORDER BY timestamp DESC LIMIT 1")
        ram_result = cursor.fetchone()
        if ram_result:
            import json
            ram_data = json.loads(ram_result[0])
            latest_stats['ram'] = round(float(ram_data.get('ram_usage', 0)), 1)
            print(f"RAM data retrieved: {latest_stats['ram']}%")

        # Fixed query for disk
        cursor.execute("SELECT value FROM sonde WHERE sonde_name='disk' ORDER BY timestamp DESC LIMIT 1")
        disk_result = cursor.fetchone()
        if disk_result:
            import json
            disk_data = json.loads(disk_result[0])
            latest_stats['disk'] = round(float(disk_data.get('disk_usage', 0)), 1)
            print(f"Disk data retrieved: {latest_stats['disk']}%")

        # Get CERT alerts with correct column names from Parser.py
        cert_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'p2', 'cert_alertes.sqlite')
        cert_conn = sqlite3.connect(cert_db_path)
        cert_cursor = cert_conn.cursor()
        cert_cursor.execute("SELECT reference, date, title FROM alertes ORDER BY date DESC")

        for row in cert_cursor.fetchall():
            alertes.append({"reference": row[0], "date": row[1], "titre": row[2]})
            print(f"Alert retrieved: {row[0]} - {row[1]} - {row[2]}")

        cert_conn.close()
        conn.close()

        graph_generator = GraphGenerator()
        graph_generator.generate_all_graphs()

        print(f"All stats successfully retrieved")
    except Exception as e:
        print(f"Error retrieving data: {str(e)}")
        import traceback
        traceback.print_exc()
        latest_stats = {'cpu': 0, 'ram': 0, 'disk': 0}
        alertes = []

    return render_template('index.html', stats=latest_stats, alertes=alertes, timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/refresh')
def refresh():
    try:
        # project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        print("Starting data collection...")


        # storage_manager.py
        stockage_main = os.path.join(project_root, "p2", "storage_manager.py")
        print(f"Running storage manager: {stockage_main}")
        result = subprocess.run([sys.executable, stockage_main, "--check"], 
                        timeout=30, 
                        capture_output=True, 
                        text=True)
        


        # alertes.py
        alertes_path = os.path.join(project_root, "p3", "alertes.py")
        print(f"Running alerts script: {alertes_path}")
        result = subprocess.run([sys.executable, alertes_path, "--check"], 
                        timeout=30, 
                        capture_output=True, 
                        text=True)
        

        # gen_graphes.py
        graph_generator = GraphGenerator()
        graph_generator.generate_all_graphs()

        print("Data collection completed successfully")

        # Redirect back to index page
        return redirect(url_for('index'))
    
    except Exception as e:
        error_message = f"Error updating data: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        return error_message

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)
    
