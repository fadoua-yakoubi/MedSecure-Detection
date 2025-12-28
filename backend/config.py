"""
Configuration centralisée pour MediConnect Security
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# === DATABASE ===
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'mediconnect'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# === FLASK ===
FLASK_CONFIG = {
    'SECRET_KEY': os.getenv('SECRET_KEY', 'change-me-in-production'),
    'SESSION_LIFETIME_HOURS': 24,
    'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
    'HOST': os.getenv('FLASK_HOST', '0.0.0.0'),
    'PORT': int(os.getenv('FLASK_PORT', '5000'))
}

# === CORS ===
CORS_CONFIG = {
    'origins': ['http://localhost:8000', 'http://127.0.0.1:8000'],
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
    'supports_credentials': True
}

# === ML MODEL ===
MODEL_CONFIG = {
    'model_path': os.path.join(BASE_DIR, 'models/distilbert_attack_detector'),
    'model_name': 'distilbert-base-uncased',
    'threshold': float(os.getenv('DETECTION_THRESHOLD', '0.6')),
    'time_window_minutes': int(os.getenv('TIME_WINDOW_MINUTES', '2')),
    'max_length': 256
}

# === BLOCKCHAIN ===
BLOCKCHAIN_CONFIG = {
    'provider_url': os.getenv('ETH_PROVIDER_URL', 'http://127.0.0.1:7545'),
    'contract_address': os.getenv('CONTRACT_ADDRESS', ''),
    'abi_path': os.path.join(BASE_DIR, 'blockchain/build/contracts/AttackLogger.json'),
    'private_key': os.getenv('ETH_PRIVATE_KEY', '')
}

# === LOGGING ===
LOGGING_CONFIG = {
    'security_log': os.path.join(BASE_DIR, 'logs/security_events.log'),
    'attack_log': os.path.join(BASE_DIR, 'logs/attack_detection.log'),
    'detected_attacks_file': os.path.join(BASE_DIR, 'logs/detected_attacks.jsonl'),
    'security_logs_json': os.path.join(BASE_DIR, 'logs/security_logs.json'),
    'security_logs_csv': os.path.join(BASE_DIR, 'logs/security_logs.csv'),
    'level': os.getenv('LOG_LEVEL', 'INFO')
}

# === SECURITY ===
SECURITY_CONFIG = {
    'max_login_attempts': int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')),
    'lockout_duration_minutes': int(os.getenv('LOCKOUT_DURATION', '15')),
    'suspicious_countries': ['RU', 'CN', 'KP', 'IR'],
    'min_password_length': 6
}

# === PATHS ===
PATHS = {
    'frontend': os.path.join(BASE_DIR, 'frontend'),
    'static': os.path.join(BASE_DIR, 'frontend'),
    'templates': os.path.join(BASE_DIR, 'frontend'),
    'data': os.path.join(BASE_DIR, 'data'),
    'logs': os.path.join(BASE_DIR, 'logs')
}

# Créer les dossiers nécessaires
for path in PATHS.values():
    os.makedirs(path, exist_ok=True)
os.makedirs(os.path.dirname(LOGGING_CONFIG['security_log']), exist_ok=True)

# === VALIDATION ===
def validate_config():
    """Valide la configuration au démarrage"""
    errors = []
    warnings = []
    
    # Vérifier les variables obligatoires
    if not DB_CONFIG['password']:
        errors.append("❌ DB_PASSWORD n'est pas défini dans .env")
    
    if FLASK_CONFIG['SECRET_KEY'] == 'change-me-in-production':
        warnings.append("⚠️  SECRET_KEY est la valeur par défaut. Changez-la en production.")
    
    # Vérifier que le modèle existe
    if not os.path.exists(MODEL_CONFIG['model_path']):
        errors.append(f"❌ Modèle introuvable: {MODEL_CONFIG['model_path']}")
    
    # Vérifier la blockchain (optionnel)
    if not BLOCKCHAIN_CONFIG['private_key']:
        warnings.append("⚠️  ETH_PRIVATE_KEY non défini. La blockchain sera inactive.")
    elif not BLOCKCHAIN_CONFIG['contract_address']:
        warnings.append("⚠️  CONTRACT_ADDRESS non défini. La blockchain sera inactive.")
    elif not os.path.exists(BLOCKCHAIN_CONFIG['abi_path']):
        warnings.append(f"⚠️  ABI blockchain introuvable: {BLOCKCHAIN_CONFIG['abi_path']}")
    
    # Afficher les avertissements
    if warnings:
        print("\n⚠️  Avertissements:")
        for warning in warnings:
            print(f"   {warning}")
    
    # Afficher les erreurs
    if errors:
        print("\n❌ Problèmes de configuration:")
        for error in errors:
            print(f"   {error}")
        return False
    
    print("\n✅ Configuration validée avec succès")
    return True

if __name__ == '__main__':
    print("🔍 Validation de la configuration...")
    validate_config()
    print(f"📂 Racine du projet: {BASE_DIR}")
    print(f"🤖 Modèle ML: {MODEL_CONFIG['model_path']}")
    print(f"🔗 Blockchain: {'Activée' if BLOCKCHAIN_CONFIG['private_key'] else 'Désactivée'}")
    print(f"🗄️ Base de données: {DB_CONFIG['dbname']}@{DB_CONFIG['host']}")