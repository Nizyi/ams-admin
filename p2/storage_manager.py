import sqlite3
import json
import subprocess
from datetime import datetime
import os


class StorageManager:
    def __init__(self):
        self.name= "alertes.sqlite"
        self.limit = 1
        
        conn = sqlite3.connect(self.name)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sonde (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sonde_name TEXT NOT NULL,
            value TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

    def insert(self, sonde_name, value):
        try:
            conn = sqlite3.connect(self.name)
            cursor = conn.cursor()

            if not isinstance(value, str):
                value = str(value)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            cursor.execute(
                "INSERT INTO sonde (sonde_name, value, timestamp) VALUES (?, ?, ?)",
                (sonde_name, value, timestamp)
            )
            
            conn.commit()
            conn.close()
            print(f"Données bien insérées dans {sonde_name}.")
        except Exception as e:
            print(f"Erreur lors de l'insertion des données dans {sonde_name} {e}.")

    def old_delete(self):

        try:
            conn = sqlite3.connect(self.name)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM sonde WHERE timestamp < datetime('now', '-' || ? || ' day')",
                (self.limit,)
            )
            
            conn.commit()
            conn.close()
            print(f"Ancinnes données effectué.")
        except Exception as e:
            print(f"Erreur lors de la suppression des données.")
    

    def set_limit(self, limit):
        self.limit = limit
        print(f"Limit fixé à {limit}.")

    def get_limit(self):
        return self.limit

    def backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}_{self.name}"
            
            conn = sqlite3.connect(self.name)
            backup_conn = sqlite3.connect(backup_name)

            conn.backup(backup_conn)
            conn.close()
            backup_conn.close()
            
            print(f"Sauvegarde créée: {backup_name}")
            return backup_name
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {str(e)}")
            return None

    def restore(self, backup_file):
        try:
            if os.path.exists(backup_file):

                source_conn = sqlite3.connect(backup_file)
                dest_conn = sqlite3.connect(self.name)
                
                source_conn.backup(dest_conn)
                
                source_conn.close()
                dest_conn.close()

                print(f"Base de données restaurée depuis: {backup_file}")
                return True
            else:
                print(f"Fichier de sauvegarde non trouvé: {backup_file}")
                return False
        except Exception as e:
            print(f"un pb est survenu")
    
class Sondes :
    def __init__(self, sondes):
        self.bdd = StorageManager()
        self.sondes = sondes  
        self.p1_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'p1')

    def get_all_sondes(self):
        try:
            all_data = {}
            
            for sonde_file in self.sondes:

                sonde_name = os.path.splitext(sonde_file)[0]
                
                data = self.execute_sonde(sonde_file)
                
                if data:

                    all_data[sonde_name] = data
                    
                    json_data = json.dumps(data) 
                    self.bdd.insert(sonde_name, json_data)
                    print(f"données de {sonde_name} insérées.")
                else:
                    all_data[sonde_name] = None
                    print(f"Pas de données pour {sonde_name}.")
            
            return all_data
        except Exception as e:
            print(f"Erreur lors de l'exécution des sondes")
            return {}

    def execute_sonde(self, sonde_name):
        try:
            path = os.path.join(self.p1_dir, sonde_name)
            
            if not os.path.exists(path):
                print(f"Script non trouvé: {path}")
                return None
            
            if sonde_name.endswith('.py'):
                data_ex = subprocess.check_output(['python', path])

            elif sonde_name.endswith('.sh'):
                data_ex = subprocess.check_output(['bash', path])

            data = json.loads(data_ex.decode('utf-8'))

            return data
        except Exception as e:
            print(f"script {sonde_name} non exécuté : {e}")

if __name__ == "__main__":

    import sys
    
    """
    print("\nList sondes:")
    sondes = ['cpu.py', 'ram.py', 'disk.py']
    test = Sondes(sondes)
    for sonde in sondes:
        print(f" - {sonde}") 
    

    print("\nall sondes:")
    results = test.get_all_sondes()
    for sonde_name, data in results.items():
        print(f"\n{sonde_name} result:")
        print(json.dumps(data, indent=2))
    


    if sondes:
        test_sonde = sondes[0]
        print(f"\n1 sonde '{test_sonde}':")
        result = test.execute_sonde(test_sonde)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("No result returned") 
    

    """