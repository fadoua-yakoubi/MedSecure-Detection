from flask import Flask, request, jsonify, session, send_from_directory, render_template_string
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import os
from datetime import timedelta, datetime
import re
import threading
import time
import sys
import os
from security.security_logger import security_logger
from security.attack_detector import FixedAttackDetector  # Sans start_fixed_cleanup_thread
from blockchain.blockchain_client import blockchain_logger

FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

app = Flask(__name__, 
            static_folder=FRONTEND_FOLDER,
            static_url_path='')
app.secret_key = 'mediconnect-secret-key-2023'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = False  # False pour développement local
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Lax pour développement local

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ✅ Fonction de nettoyage définie localement
def start_fixed_cleanup_thread(detector, interval_minutes=5):
    """Démarre le thread de nettoyage des événements anciens"""
    def cleanup_loop():
        while True:
            time.sleep(interval_minutes * 60)
            try:
                detector.cleanup_old_events()
                detector.logger.info("🧹 Nettoyage des anciens événements effectué")
            except Exception as e:
                print(f"❌ Erreur nettoyage: {e}")
    
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    return thread

# Initialiser le détecteur BERT
print("🔄 Chargement du modèle de détection d'attaques BERT...")
try:
    # ✅ Chemin relatif depuis backend/ vers le modèle
    model_path = "../bert_attack_detector/final_model"
    
    # Vérifier si le modèle existe
    if not os.path.exists(model_path):
        # Essayer un autre chemin possible
        model_path = "../models/distilbert_attack_detector"
        if not os.path.exists(model_path):
            print(f"⚠️ Modèle introuvable. Chemins essayés:")
            print(f"   - ../bert_attack_detector/final_model")
            print(f"   - ../models/distilbert_attack_detector")
    
    detector = FixedAttackDetector(
        model_path=model_path,
        time_window_minutes=2,
        threshold=0.6
    )
    
    # Démarrer le thread de nettoyage
    cleanup_thread = start_fixed_cleanup_thread(detector, interval_minutes=5)
    print("✅ Détecteur BERT initialisé avec succès!")
    
except Exception as e:
    print(f"❌ Erreur initialisation détecteur BERT: {e}")
    detector = None

# Initialiser la blockchain
print("🔗 Initialisation de la connexion blockchain...")
try:
    contract_address = "0xB4D6018A9F2c3aF5d3Aa3D88D791299BdD57D729"
    
    # ✅ CHEMIN CORRIGÉ - Depuis backend/ vers blockchain/
    abi_path = "../blockchain/build/contracts/AttackLogger.json"
    
    # Vérifier que le fichier existe
    if os.path.exists(abi_path):
        blockchain_logger.setup_contract(contract_address, abi_path)
        print(f"✅ Connexion blockchain initialisée: {abi_path}")
    else:
        print(f"⚠️ Fichier blockchain introuvable: {abi_path}")
        print("   L'application fonctionnera sans blockchain")
        
except Exception as e:
    print(f"❌ Erreur initialisation blockchain: {e}")
    print("   L'application fonctionnera sans blockchain")

# Configuration PostgreSQL
INIT_DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Connexion à la base de données avec gestion d'erreurs"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion PostgreSQL: {e}")
        return None

def init_db():
    """Initialisation de la base de données"""
    conn = get_db_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return False
    
    try:
        cur = conn.cursor()
        
        # Table users
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                nom_complet VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telephone VARCHAR(20),
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'patient',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                est_actif BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Table consultations
        cur.execute('''
            CREATE TABLE IF NOT EXISTS consultations (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER REFERENCES users(id),
                medecin_id INTEGER REFERENCES users(id),
                date_consultation TIMESTAMP,
                duree INTEGER,
                statut VARCHAR(20) DEFAULT 'planifiee',
                symptomes TEXT,
                diagnostic TEXT,
                ordonnance TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour les logs de sécurité
        cur.execute('''
            CREATE TABLE IF NOT EXISTS security_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                email VARCHAR(100),
                ip_address VARCHAR(45),
                user_agent TEXT,
                successful BOOLEAN,
                failure_reason TEXT,
                is_attack_ip BOOLEAN DEFAULT FALSE,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vérifier si des médecins existent
        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'medecin'")
        if cur.fetchone()[0] == 0:
            doctor_password = hash_password("Medecin123!")
            cur.execute('''
                INSERT INTO users (nom_complet, email, telephone, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('Dr. Sophie Martin', 'medecin@mediconnect.fr', '+33123456789', doctor_password, 'medecin'))
            print("✅ Médecin de test créé: medecin@mediconnect.fr / Medecin123!")
        
        conn.commit()
        print("✅ Base de données initialisée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def hash_password(password):
    """Hachage simple avec SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password, hashed):
    """Vérification du mot de passe"""
    return hash_password(password) == hashed

def validate_email(email):
    """Validation d'email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def analyze_login_attempt(login_data, client_info):
    """Analyse une tentative de login avec BERT et blockchain"""
    if detector is None:
        return {'is_attack': False, 'confidence': 0.0, 'attack_type': 'system_offline'}
    
    try:
        analysis_data = {
            **login_data,
            'IP Address': client_info['ip_address'],
            'Country': client_info['country'],
            'Browser Name and Version': client_info['browser_name_version'],
            'OS Name and Version': client_info['os_name_version'],
            'Device Type': client_info['device_type'],
            'timestamp': datetime.now().isoformat()
        }
        
        result = detector.process_log_entry(analysis_data)
        
        # Logger sur blockchain si attaque détectée ET blockchain disponible
        if result.get('is_attack', False) and blockchain_logger.contract:
            attack_data = {
                'timestamp': datetime.now().isoformat(),
                'email': login_data.get('email', 'unknown'),
                'user_id': str(login_data.get('User ID', '')),
                'ip_address': client_info['ip_address'],
                'country': client_info['country'],
                'attack_type': result.get('attack_type', 'unknown'),
                'confidence': result.get('confidence', 0.0),
                'bert_probability': result.get('bert_probability', 0.0),
                'bert_used': True,
                'login_successful': login_data.get('Login Successful', False)
            }
            
            blockchain_tx_hash = blockchain_logger.log_attack_to_blockchain(attack_data)
            if blockchain_tx_hash:
                print(f"✅ Attaque loggée sur blockchain: {blockchain_tx_hash}")
                result['blockchain_tx_hash'] = blockchain_tx_hash
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur analyse login: {e}")
        return {'is_attack': False, 'confidence': 0.0, 'attack_type': 'analysis_error'}

@app.route('/')
def serve_index():
    """Servir la page d'accueil (index.html)"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        return jsonify({
            'error': f'Fichier index.html introuvable dans {app.static_folder}',
            'details': str(e)
        }), 404

@app.route('/<path:path>')
def serve_static_files(path):
    """Servir tous les autres fichiers statiques"""
    try:
        return send_from_directory(app.static_folder, path)
    except Exception as e:
        return jsonify({
            'error': f'Fichier {path} introuvable',
            'details': str(e)
        }), 404

@app.route('/api')
def home():
    """Page d'accueil de l'API"""
    blockchain_status = "Active" if blockchain_logger.contract else "Inactive"
    
    return jsonify({
        'message': 'API MediConnect - Télémédecine avec Détection BERT & Blockchain',
        'version': '1.0',
        'security': {
            'bert_detection': 'Active' if detector else 'Offline',
            'blockchain_logging': blockchain_status
        },
        'endpoints': {
            'register': 'POST /api/register',
            'login': 'POST /api/login',
            'security_analyze': 'POST /api/security/analyze-login',
            'security_stats': 'GET /api/security/stats',
            'blockchain_stats': 'GET /api/blockchain/stats',
            'profile': 'GET /api/user/profile'
        }
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Connexion de l'utilisateur avec détection d'attaques BERT et blockchain"""
    try:
        data = request.get_json()
        if not data:
            security_logger.log_login_attempt(
                user_id=None,
                email='unknown',
                successful=False,
                failure_reason='Données manquantes'
            )
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            security_logger.log_login_attempt(
                user_id=None,
                email=email,
                successful=False,
                failure_reason='Champs manquants'
            )
            return jsonify({'success': False, 'message': 'Email et mot de passe requis'}), 400
        
        # Analyse de sécurité avant l'authentification
        client_info = security_logger.get_client_info()
        security_analysis = analyze_login_attempt(
            {'email': email, 'Login Successful': False}, 
            client_info
        )
        
        # Si attaque détectée, bloquer immédiatement
        if security_analysis.get('is_attack', False):
            security_logger.log_login_attempt(
                user_id=None,
                email=email,
                successful=False,
                failure_reason=f"Attaque détectée: {security_analysis.get('attack_type', 'unknown')}",
                is_attack_ip=True
            )
            
            response_data = {
                'success': False, 
                'message': 'Activité suspecte détectée. Veuillez réessayer plus tard.',
                'blocked': True,
                'detection_details': security_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            if 'blockchain_tx_hash' in security_analysis:
                response_data['blockchain_logged'] = True
                response_data['blockchain_tx_hash'] = security_analysis['blockchain_tx_hash']
            
            return jsonify(response_data), 429
        
        # Continuer avec l'authentification normale
        conn = get_db_connection()
        if not conn:
            security_logger.log_login_attempt(
                user_id=None,
                email=email,
                successful=False,
                failure_reason='Base de données indisponible'
            )
            return jsonify({'success': False, 'message': 'Base de données indisponible'}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cur.execute('''
                SELECT id, nom_complet, email, telephone, password_hash, role 
                FROM users 
                WHERE email = %s AND est_actif = TRUE
            ''', (email,))
            
            user = cur.fetchone()
            
            if not user:
                security_logger.log_login_attempt(
                    user_id=None,
                    email=email,
                    successful=False,
                    failure_reason='Utilisateur non trouvé'
                )
                return jsonify({'success': False, 'message': 'Email ou mot de passe incorrect'}), 401
            
            if not verify_password(password, user['password_hash']):
                failed_attempt_analysis = analyze_login_attempt(
                    {'email': email, 'User ID': str(user['id']), 'Login Successful': False},
                    client_info
                )
                
                security_logger.log_login_attempt(
                    user_id=user['id'],
                    email=email,
                    successful=False,
                    failure_reason='Mot de passe incorrect',
                    is_attack_ip=failed_attempt_analysis.get('is_attack', False)
                )
                return jsonify({'success': False, 'message': 'Email ou mot de passe incorrect'}), 401
            
            # Connexion réussie
            success_analysis = analyze_login_attempt(
                {'email': email, 'User ID': str(user['id']), 'Login Successful': True},
                client_info
            )
            
            security_logger.log_login_attempt(
                user_id=user['id'],
                email=email,
                successful=True,
                is_attack_ip=success_analysis.get('is_attack', False)
            )
            
            # Session
            session['user_id'] = user['id']
            session['user_nom'] = user['nom_complet']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            
            response_data = {
                'success': True, 
                'message': 'Connexion réussie',
                'user': {
                    'id': user['id'],
                    'nom_complet': user['nom_complet'],
                    'email': user['email'],
                    'telephone': user['telephone'],
                    'role': user['role']
                },
                'security_check': {
                    'attack_detected': False,
                    'confidence': success_analysis.get('confidence', 0.0)
                }
            }
            
            if os.environ.get('DEBUG'):
                response_data['security_analysis'] = success_analysis
            
            return jsonify(response_data), 200
            
        except Exception as e:
            security_logger.log_login_attempt(
                user_id=None,
                email=email,
                successful=False,
                failure_reason=f'Erreur serveur: {str(e)}'
            )
            return jsonify({'success': False, 'message': 'Erreur lors de la connexion'}), 500
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        security_logger.log_login_attempt(
            user_id=None,
            email=data.get('email', 'unknown') if 'data' in locals() else 'unknown',
            successful=False,
            failure_reason=f'Erreur générale: {str(e)}'
        )
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400
        
        nom_complet = data.get('nom_complet', '').strip()
        email = data.get('email', '').strip().lower()
        telephone = data.get('telephone', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'patient')
        
        if not all([nom_complet, email, password]):
            return jsonify({'success': False, 'message': 'Tous les champs obligatoires doivent être remplis'}), 400
        
        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Format d\'email invalide'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Base de données indisponible'}), 500
        
        cur = conn.cursor()
        
        try:
            cur.execute('SELECT id FROM users WHERE email = %s', (email,))
            if cur.fetchone():
                return jsonify({'success': False, 'message': 'Cet email est déjà utilisé'}), 409
            
            password_hash = hash_password(password)
            cur.execute('''
                INSERT INTO users (nom_complet, email, telephone, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
            ''', (nom_complet, email, telephone, password_hash, role))
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Compte créé avec succès'}), 201
            
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'message': 'Erreur lors de la création du compte'}), 500
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    """Récupérer le profil de l'utilisateur connecté"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Non authentifié'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Base de données indisponible'}), 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute('''
            SELECT id, nom_complet, email, telephone, role, date_creation
            FROM users 
            WHERE id = %s
        ''', (session['user_id'],))
        
        user = cur.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
        
        return jsonify({'success': True, 'user': dict(user)}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/security/analyze-login', methods=['POST'])
def security_analyze_login():
    """Analyse une tentative de login en temps réel (API dédiée)"""
    try:
        data = request.get_json()
        
        if detector is None:
            return jsonify({
                'success': False,
                'error': 'Système de détection BERT non disponible'
            }), 503
        
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        result = detector.process_log_entry(data)
        
        response = {
            'success': True,
            'detection_result': result,
            'action_recommended': 'block' if result['is_attack'] else 'allow'
        }
        
        if result['is_attack']:
            return jsonify(response), 429
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/stats', methods=['GET'])
def get_security_stats():
    """Retourne les statistiques de sécurité"""
    if detector is None:
        return jsonify({
            'success': False,
            'error': 'Système de détection BERT non disponible'
        }), 503
    
    stats = detector.get_statistics()
    
    return jsonify({
        'success': True,
        'statistics': stats,
        'current_threshold': detector.threshold,
        'time_window_minutes': detector.time_window.total_seconds() / 60
    }), 200

@app.route('/api/blockchain/stats', methods=['GET'])
def get_blockchain_stats():
    """Retourne les statistiques de la blockchain"""
    try:
        if not blockchain_logger.contract:
            return jsonify({
                'success': False,
                'error': 'Blockchain non configurée'
            }), 503
        
        attack_count = blockchain_logger.contract.functions.getAttackCount().call()
        
        return jsonify({
            'success': True,
            'blockchain_stats': {
                'total_attacks_logged': attack_count,
                'contract_address': blockchain_logger.contract_address,
                'network': 'Ganache Local',
                'is_connected': blockchain_logger.w3.is_connected() if blockchain_logger.w3 else False
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Déconnexion de l'utilisateur"""
    session.clear()
    return jsonify({'success': True, 'message': 'Déconnexion réussie'}), 200

@app.route('/api/security/run-test', methods=['POST'])
def run_security_test():
    """Exécute un test de sécurité spécifique"""
    try:
        data = request.get_json()
        test_type = data.get('test_type', 'full_test')
        
     
        import sys
        import os
        
        test_dir = os.path.join(os.path.dirname(__file__), '..', 'test')
        if test_dir not in sys.path:
            sys.path.append(test_dir)
        
        try:
            from test_attack_scenarios import run_specific_test  
            results = run_specific_test(test_type)
            
            return jsonify({
                'success': True,
                'test_type': test_type,
                'results': results,
                'summary': f"Test {test_type} terminé - {len(results)} événements"
            })
            
        except ImportError as e:
            return jsonify({
                'success': False, 
                'error': f"Impossible de charger le module de test: {str(e)}"
            }), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session/check', methods=['GET'])
def check_session():
    """Vérifie si l'utilisateur est connecté"""
    if 'user_id' in session:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'Base de données indisponible'
            }), 500
        
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('''
                SELECT id, nom_complet, email, telephone, role 
                FROM users 
                WHERE id = %s AND est_actif = TRUE
            ''', (session['user_id'],))
            
            user = cur.fetchone()
            
            if user:
                return jsonify({
                    'success': True,
                    'authenticated': True,
                    'user': {
                        'id': user['id'],
                        'nom_complet': user['nom_complet'],
                        'email': user['email'],
                        'telephone': user['telephone'],
                        'role': user['role']
                    }
                }), 200
            else:
                session.clear()
                return jsonify({
                    'success': True,
                    'authenticated': False,
                    'message': 'Utilisateur non trouvé'
                }), 200
                
        except Exception as e:
            print(f"❌ Erreur vérification session: {e}")
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'Erreur serveur'
            }), 500
        finally:
            cur.close()
            conn.close()
    else:
        return jsonify({
            'success': True,
            'authenticated': False,
            'message': 'Non authentifié'
        }), 200

if __name__ == '__main__':
    print("🚀 Démarrage de MediConnect avec détection BERT & Blockchain...")
    print("📊 Initialisation de la base de données...")
    if init_db():
        print("✅ Base de données prête")
        print("🤖 Système de détection BERT activé")
        print("🔗 Système blockchain intégré")
        print("🌐 Serveur API démarré sur http://localhost:5000")
        
        app.run(debug=True, port=5000, host='0.0.0.0')
    else:
        print("❌ Échec de l'initialisation")