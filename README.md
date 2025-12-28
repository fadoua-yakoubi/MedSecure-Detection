🛡️ MediConnect - Système de Sécurité avec Détection BERT & Blockchain
📖 Description
Système de sécurité intelligent pour application de télémédecine combinant :

Détection d'attaques avec modèle BERT fine-tuné

Logging immuable sur blockchain Ethereum

Dashboard de monitoring en temps réel

🚀 Fonctionnalités Principales
🤖 Détection IA : Modèle DistilBERT pour identifier les tentatives d'intrusion

⛓️ Blockchain : Journalisation immuable des attaques détectées

📊 Dashboard : Interface de monitoring en temps réel

🧪 Tests intégrés : Simulateur d'attaques pour valider le système

🔒 Multi-couches : Combinaison IA + règles comportementales + analyse IP

⚙️ Installation Rapide
1. Prérequis
bash
Python 3.8+
PostgreSQL 12+
Git
2. Configuration
bash
# Clonez le projet
git clone <votre-repo>
cd mediconnect

# Configuration backend
cd backend
cp .env-example .env
# Éditez .env avec vos identifiants PostgreSQL
3. Installation
bash
# Environnement virtuel
python -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` sur Windows

# Dépendances
pip install -r requirements.txt

# Base de données
python init_database.py

# Lancement
python app.py
🌐 Accès
Application : http://localhost:5000
Dashboard sécurité : http://localhost:5000 → Section "Sécurité BERT"