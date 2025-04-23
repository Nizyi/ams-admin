import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import os


class Parser:

    def __init__(self, db_name="cert_alertes.sqlite"):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_name)
        self.init_database()

    def init_database(self):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT UNIQUE,
            date TEXT,
            title TEXT,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()

    def get_alerts(self):
        try:
            url = "https://www.cert.ssi.gouv.fr/"
            response = requests.get(url)
            
            soup = BeautifulSoup(response.content, 'html.parser')

            alerts_section = soup.find('div', class_="items-list")
            
            if not alerts_section:
                print("Section d'alertes non trouvée sur la page")
                return []
            
            alerts = []
            
            alert_items = alerts_section.find_all("div", class_="item cert-alert open")
            
            for item in alert_items:
                try:
                    print(f"1 alerte trouvé")
                    reference_elem = item.find("div", {'class': 'item-ref'})
                    reference = reference_elem.text.strip() if reference_elem else "reference non trouvée"
                    
                    date_elem = item.find("span", class_='item-date')
                    date = date_elem.text.strip() if date_elem else "date non trouvée"
                    
                    title_elem = item.find("div", class_='item-title')
                    title = title_elem.text.strip() if title_elem else " titre non trouvé"
                    
                    alerts.append({
                        'reference': reference,
                        'date': date,
                        'title': title
                    })
                except Exception as e:
                    print(f"1 alrte pas trouvé")
                    continue
            
            return alerts
        
        except Exception as e:
            print(f"alertes non trouvé {e}")
            return []
    
    def insert_alerts(self, alerts):

        if not alerts:
            print("Aucune alerte à enregistrer")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for alert in alerts:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO alertes (reference, date, title, last_update) VALUES (?, ?, ?, ?)",
                        (alert['reference'], alert['date'], alert['title'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    )

                except Exception as e:
                    print(f"alerte {alert['reference']} non inserée {e}")
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"ausune alerte inserée")
            return False
    
    def update_alerts(self):
        alerts = self.get_alerts()
        self.clear_database()  
        self.insert_alerts(alerts)
        print(f"update faite")
        return True
    
    def clear_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM alertes")
            
            conn.commit()
            conn.close()
            
            print("Base de données vidée avec succès")
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression des données: {str(e)}")
            return False
    
    def get_latest_alert(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            self.update_alerts()
            
            cursor.execute(
                "SELECT reference, date, title FROM alertes ORDER BY date ASC LIMIT 1"
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'reference': result[0],
                    'date': result[1],
                    'title': result[2]
                }
            else:
                print("pas d alerte dans la base de données")
                return None
        except Exception as e:
            print(f"erreur recuperation donnée {e}")
            return None

if __name__ == "__main__":

    parser = Parser()
    
    while True:
        print("\n===== Gestionnaire d'alertes CERT-FR =====")
        print("1. Mettre à jour les alertes")
        print("2. Afficher la dernière alerte")
        print("3. Afficher toutes les alertes disponibles en ligne")
        print("4. Quitter")
        
        choice = input("\nChoisissez une option (1-4): ")
        
        if choice == "1":
            print("\nMise à jour des alertes en cours...")
            parser.update_alerts()
            
        elif choice == "2":
            print("\nRécupération de la dernière alerte...")
            latest_alert = parser.get_latest_alert()
            
            if latest_alert:
                print("\n----- Dernière alerte -----")
                print(f"Référence: {latest_alert['reference']}")
                print(f"Date: {latest_alert['date']}")
                print(f"Titre: {latest_alert['title']}")
            
        elif choice == "3":
            print("\nRécupération des alertes en ligne...")
            online_alerts = parser.get_alerts()
            
            if online_alerts:
                print(f"\n{len(online_alerts)} alertes trouvées:")
                for i, alert in enumerate(online_alerts, 1):
                    print(f"\n----- Alerte {i} -----")
                    print(f"Référence: {alert['reference']}")
                    print(f"Date: {alert['date']}")
                    print(f"Titre: {alert['title']}")
            else:
                print("Aucune alerte trouvée en ligne.")
                
        elif choice == "4":
            print("\nAu revoir!")
            break
            
        else:
            print("\nOption invalide. Veuillez choisir une option entre 1 et 4.")
