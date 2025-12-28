import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
backend_dir = Path(__file__).parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration de connexion initiale
INIT_DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

DB_NAME = os.getenv('DB_NAME', 'mediconnect')

def create_database():
    """Créer la base de données si elle n'existe pas"""
    try:
        print(f"🔍 Connexion à PostgreSQL avec: {INIT_DB_CONFIG['user']}@{INIT_DB_CONFIG['host']}:{INIT_DB_CONFIG['port']}")
        
        # Se connecter à PostgreSQL
        conn = psycopg2.connect(**INIT_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Créer la base de données
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f'CREATE DATABASE {DB_NAME}')
            print(f" Base de données '{DB_NAME}' créée avec succès")
        else:
            print(f"  Base de données '{DB_NAME}' existe déjà")
        
        cur.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f" Erreur de connexion à PostgreSQL: {e}")
        print("\n Dépannage:")
        print("1. Vérifiez que PostgreSQL est installé et démarré")
        print("2. Vérifiez vos identifiants dans le fichier .env:")
        print(f"   - DB_HOST: {INIT_DB_CONFIG['host']}")
        print(f"   - DB_PORT: {INIT_DB_CONFIG['port']}")
        print(f"   - DB_USER: {INIT_DB_CONFIG['user']}")
        print(f"   - DB_PASSWORD: {'***' if INIT_DB_CONFIG['password'] else 'NON DÉFINI'}")
        print("3. Le serveur PostgreSQL écoute sur le port 5432")
        print("\n Testez la connexion avec: psql -h localhost -U postgres")
        return False
    except Exception as e:
        print(f" Erreur lors de la création de la base de données: {e}")
        return False

if __name__ == '__main__':
    print(" Initialisation de la base de données MediConnect...")
    print("=" * 50)
    
    if create_database():
        print("\n Initialisation terminée avec succès!")
        print("\n Prochaines étapes:")
        print("1. Lancez l'application: python backend/app.py")
        print("2. Accédez à: http://localhost:5000")
        print("3. Utilisez les identifiants par défaut:")
        print("   - Email: medecin@mediconnect.fr")
        print("   - Mot de passe: Medecin123!")
    else:
        print("\nÉchec de l'initialisation")
        sys.exit(1)