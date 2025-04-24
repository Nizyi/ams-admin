import sys
import os
import time
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import json
import matplotlib.dates as mdates
import certifi
import ssl

# import p2
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from p2.storage_manager import StorageManager
from p2.Parser import Parser
from p2.storage_manager import Sondes

class Alertes:
    def __init__(self):
        self.storage_manager = StorageManager(db_name="alertes.sqlite")
        self.parser = Parser(db_name="cert_alertes.sqlite")
        self.sonde_list =sondes = ["cpu.sh", "ram.py", "disk.py"]
        self.Sondes = Sondes(self.sonde_list)
        self.last_email_sent = None
        self.history_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'alert_history.txt')
        self.init_history()
        self.limit_history = 10
        self.crisis_seuil = {
            "crisis_seuil": {
                "cpu_usage": 90,
                "ram_usage": 90,
                "disk_usage": 90
            }
        }

    def crisis_check(self):
        import locale

        #Linux
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8') 
        #Windows
        #locale.setlocale(locale.LC_TIME, 'fra_fra')  

        data= self.Sondes.get_all_sondes()
        crisis= False
        msg=[]
        sondes = ["cpu", "ram", "disk"]

        for sonde in sondes:
            if sonde in data:
                sonde_data = data[sonde]
                if sonde_data:
                    for key, value in sonde_data.items():
                        if key == "cpu_usage" and value >= self.crisis_seuil["crisis_seuil"]["cpu_usage"]:
                            msg.append(f"alerte: CPU usage a {value}% avec seuil {self.crisis_seuil['crisis_seuil']['cpu_usage']}%")
                            crisis = True
                        elif key == "ram_usage" and value >= self.crisis_seuil["crisis_seuil"]["ram_usage"]:
                            msg.append(f"alerte: RAM usage a {value}% avec seuil {self.crisis_seuil['crisis_seuil']['ram_usage']}%")
                            crisis = True
                        elif key == "disk_usage" and value >= self.crisis_seuil["crisis_seuil"]["disk_usage"]:
                            msg.append(f"alerte: Disk usage a {value}% avec seuil {self.crisis_seuil['crisis_seuil']['disk_usage']}%")
                            crisis = True

        latest_alert = self.parser.get_latest_alert()
        print(f"latest alert: {latest_alert}")
        if latest_alert:
            alert_date = datetime.strptime(latest_alert['date'], "%d %B %Y")
            print(f"Date de l'alerte: {alert_date}")
            if (datetime.now() - alert_date).days <= 10:  
                msg.append(f"ALERT: Recent CERT alert - {latest_alert['reference']}: {latest_alert['title']}")
                crisis = True

        if(crisis):
            self.add_to_history(f"Crise détectée: {', '.join(msg)}")
            if (self.last_email_sent is None or (datetime.now() - self.last_email_sent).total_seconds() / 60 > 30):
                self.last_email_sent = datetime.now()
                self.send_email(msg)
        else:
            print("No crisis detected")
        return crisis

    def send_email(self, msg):
        from config import PASSWORD
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        password = PASSWORD
        context= ssl.create_default_context(cafile=certifi.where())
        smtp_server = "partage.univ-avignon.fr"
        smtp_port = 465
        sender = "tom.senechal@alumni.univ-avignon.fr"
        recipients = "tom.senechal@alumni.univ-avignon.fr"

        subject = "ALERT: Crisis detected"
        content = "\n".join(msg)

        mail = MIMEMultipart()
        mail['From'] = sender
        mail['To'] = recipients
        mail['Subject'] = subject
        mail.attach(MIMEText(content, 'plain'))

        try:
            
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(sender, password)
                server.sendmail(sender, recipients, mail.as_string())
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
    
    def init_history(self):

        if not os.path.exists(os.path.dirname(self.history_path)):
            os.makedirs(os.path.dirname(self.history_path))

        # Créer le fichier s'il n'existe pas
        if not os.path.exists(self.history_path):
            with open(self.history_path, 'w') as f:
                f.write(f"# Historique des alertes - Créé le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def add_to_history(self, message):

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.history_path, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
        self.del_history()

    def del_history(self):
        with open(self.history_path, 'r') as f:
            lines = f.readlines()

        if len(lines) > self.limit_history + 1:
            lines = lines[-self.limit_history - 1:]

        with open(self.history_path, 'w') as f:
            f.writelines("Historique des alertes \n")
            f.writelines(lines)


class GraphGenerator:
    
    def __init__(self, db_name="alertes.sqlite"):

        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'p2', db_name)
        self.sondes=["cpu", "ram", "disk"] 
        self.limit=20

        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'p4', 'static')
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    
    def get_sonde_data(self, sonde_name, limit):

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT value, timestamp FROM sonde WHERE sonde_name = ? ORDER BY timestamp DESC LIMIT ?",
                (sonde_name, limit)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            values = []
            timestamps = []
            
            for row in results:
                try:
                    value_dict = json.loads(row[0])
                    timestamp = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                    timestamps.append(timestamp)
                    values.append(value_dict)
                except Exception as e:
                    print(f"erreur get sonde {e}")
                    continue
            
            return list(reversed(values)), list(reversed(timestamps))
        
        except Exception as e:
            print(f"Error retrieving data for {sonde_name}: {e}")
            return [], []
    
    def generate_graph(self, sonde_name, limit):

        values, timestamps = self.get_sonde_data(sonde_name, limit)
        
        if not values or not timestamps:
            print(f"pas data {sonde_name}")
            return None
        
        try:
            plt.figure(figsize=(12, 6))
            
            if sonde_name == "cpu":
                cpu_values = [data.get('cpu_usage', 0) for data in values]
                plt.plot(timestamps, cpu_values, 'b-o', label='CPU Usage (%)')
                plt.title('CPU Usage')
                plt.ylabel('CPU Usage (%)')
                plt.ylim(0, 100)
            
            elif sonde_name == "ram":
                ram_values = [data.get('ram_usage', 0) for data in values]
                plt.plot(timestamps, ram_values, 'g-o', label='RAM Usage (%)')
                plt.title('RAM Usage')
                plt.ylabel('RAM Usage (%)')
                plt.ylim(0, 100)
            
            elif sonde_name == "disk":
                # timestamps en abscisse et l'utilisation du disque en ordonnée
                # 'ro-' : r = rouge, o = points/cercles, - = ligne continue entre les points
                disk_usage = [data.get('disk_usage', 0) for data in values]
                plt.plot(timestamps, disk_usage, 'ro-', label='Disk Usage (%)')
                plt.title('Disk Usage')
                plt.ylabel('Disk Usage (%)')
                #limites de l'axe Y
                plt.ylim(0, 100)

            
            plt.xlabel('Time')
            #grille de fond
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            #date formatter + pas de supperposition
            plt.gcf().autofmt_xdate()
            formatter = mdates.DateFormatter('%Y-%m-%d %H:%M')
            #applique au graphique
            plt.gca().xaxis.set_major_formatter(formatter)

            plt.savefig(f'{self.output_dir}/{sonde_name}_usage.png')
            
            plt.close()
            return None
        
        except Exception as e:
            print(f"graphe non genere {sonde_name}: {e}")
            plt.close()
            return None
    
    def generate_all_graphs(self):
        graph_paths = []
        
        for sonde_name in self.sondes:
            graph_path = self.generate_graph(sonde_name, self.limit)
            if graph_path:
                graph_paths.append(graph_path)
        
        return graph_paths
    
    def set_limit(self, limit):
        self.limit = limit
        print(f"Limit fixé à {limit}.")
    



def main():

    import argparse

    parser = argparse.ArgumentParser(description="alertes")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    alertes = Alertes()
    alertes.send_email("coucou")

    if args.check:
        alertes.crisis_check()
        return

    try:
        while True:

            alertes.crisis_check()
            time.sleep(30)

    except KeyboardInterrupt:
        print("Arrêt du système d'alertes")
        print("Système d'alertes arrêté.")

if __name__ == "__main__":
    main()
