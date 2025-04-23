# AMS - Admin Monitoring System

## Description
AMS est un système de surveillance système qui collecte des données sur l'utilisation CPU, RAM et disque, les stocke dans une base de données SQLite, et les affiche sur une interface web. Le système peut également envoyer des alertes par email lorsque certains seuils sont dépassés et affiche les alertes CERT-FR récentes.

## Structure du projet

### Organisation des dossiers
- **p1/** : Sondes de collecte des données (CPU, RAM, disque)
- **p2/** : Gestion des données et des bases de données
- **p3/** : Système d'alertes et de génération de graphiques
- **p4/** : Interface web pour visualiser les données

### Détails des composants

#### p1 - Sondes système
- `cpu.py` : Récupère l'utilisation CPU en pourcentage
- `ram.py` : Récupère l'utilisation mémoire en pourcentage
- `disk.py` : Récupère l'utilisation disque en pourcentage et d'autres métriques

#### p2 - Gestion des données
- `storage_manager.py` : Stocke les données collectées dans la base SQLite
- `Parser.py` : Récupère les alertes CERT-FR à partir du site web officiel
- Bases de données :
  - `alertes.sqlite` : Stocke les données des sondes système
  - `cert_alertes.sqlite` : Stocke les alertes CERT récupérées

#### p3 - Alertes et graphiques
- `alertes.py` : Vérifie si les métriques dépassent les seuils critiques et envoie des alertes
- `GraphGenerator` : Génère des graphiques de tendance pour les métriques
- `logs/` : Stocke l'historique des alertes

#### p4 - Interface web
- `website.py` : Serveur web Flask pour afficher les données et les graphiques
- `templates/` : Contient les templates HTML pour l'interface web
- `static/` : Stocke les graphiques générés et les ressources statiques

## Installation

1. Assurez-vous que Python 3.9+ est installé
2. Installez les dépendances :