import os
import torch
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque
import threading
import time
import logging
from pathlib import Path

class FixedAttackDetector:
    def __init__(self, model_path, time_window_minutes=2, threshold=0.5):
        self.model_path = model_path
        self.threshold = threshold
        self.time_window = timedelta(minutes=time_window_minutes)
        
        # ✅ Définir le dossier logs à la racine
        project_root = Path(__file__).parent.parent.parent
        self.logs_dir = project_root / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
        # ✅ NE PAS charger le modèle immédiatement
        self.model = None
        self.tokenizer = None
        self.device = None
        self._model_loaded = False
        
        print(f"✅ Détecteur initialisé (modèle sera chargé à la première utilisation)")
        
        # Stockage des événements récents
        self.recent_events = deque(maxlen=10000)
        self.user_activity = defaultdict(lambda: deque(maxlen=50))
        self.ip_activity = defaultdict(lambda: deque(maxlen=100))
        
        # Statistiques - IMPORTANT: Initialisation correcte
        self.stats = {
            'total_requests': 0,
            'detected_attacks': 0,
            'false_positives': 0,
            'last_reset': datetime.now(),
            'bert_predictions': 0,
            'fallback_predictions': 0
        }
        
        # ✅ Ajouter un buffer pour les résultats récents
        self.recent_results = deque(maxlen=100)
        
        self.setup_logging()
    
    def _load_model_if_needed(self):
        """Charge le modèle seulement lors de la première utilisation"""
        if self._model_loaded:
            return True
        
        print("🔄 Chargement du modèle DistilBERT (première utilisation)...")
        try:
            # ⚠️ Import ici pour éviter le chargement au démarrage
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch.nn.functional as F
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)
            self.model.eval()
            
            self._model_loaded = True
            
            print("✅ Modèle DistilBERT chargé avec succès!")
            print(f"   📐 Modèle: {self.model.config.model_type}")
            print(f"   🔢 Hidden size: {self.model.config.hidden_size}")
            print(f"   🏷️ Labels: {self.model.config.id2label}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
            print("🔄 Utilisation du mode fallback...")
            self._model_loaded = False
            return False
    
    def setup_logging(self):
        """Configuration du système de logging"""
        self.logger = logging.getLogger('fixed_attack_detector')
        self.logger.setLevel(logging.INFO)
        
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # ✅ Fichier de log dans logs/
        file_handler = logging.FileHandler(
            self.logs_dir / 'attack_detection.log',
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # ✅ Garder aussi la console pour le débogage
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.propagate = False
    
    def process_log_entry(self, log_data):
        """Traite une entrée de log et détecte les attaques"""
        self.stats['total_requests'] += 1
        
        # Préparer le texte pour BERT
        text = self.prepare_text_for_bert(log_data)
        
        # Prédiction BERT (charge le modèle si nécessaire)
        try:
            if self._load_model_if_needed():
                bert_prediction = self.bert_predict(text)
                self.stats['bert_predictions'] += 1
            else:
                bert_prediction = {'probability_attack': 0.3, 'confidence': 0.5}
                self.stats['fallback_predictions'] += 1
        except Exception as e:
            print(f"❌ Erreur prédiction BERT: {e}")
            bert_prediction = {'probability_attack': 0.3, 'confidence': 0.0}
            self.stats['fallback_predictions'] += 1
        
        # Analyse comportementale basique
        behavioral_analysis = self.analyze_behavioral_patterns(log_data)
        
        # Décision finale
        is_attack, confidence, attack_type = self.combine_predictions(
            bert_prediction, behavioral_analysis, log_data
        )
        
        # Mettre à jour les statistiques
        self.update_activity_tracking(log_data)
        
        # ✅ Stocker le résultat pour l'interface
        result = {
            'is_attack': is_attack,
            'confidence': confidence,
            'attack_type': attack_type,
            'bert_probability': bert_prediction.get('probability_attack', 0.3),
            'behavioral_score': behavioral_analysis['score'],
            'bert_used': self._model_loaded,
            'timestamp': datetime.now().isoformat(),
            'email': log_data.get('email'),
            'ip': log_data.get('IP Address'),
            'country': log_data.get('Country'),
            'login_success': log_data.get('Login Successful', False)
        }
        
        self.recent_results.append(result)
        
        # ✅ Logger si attaque détectée (mais continuer à afficher dans la console)
        if is_attack:
            self.log_attack(log_data, confidence, attack_type, bert_prediction)
            self.stats['detected_attacks'] += 1
            # ✅ Afficher aussi dans la console pour l'interface
            print(f"🚨 ATTAQUE DÉTECTÉE: {attack_type} - Confiance: {confidence:.2%}")
        
        return result
    
    def bert_predict(self, text):
        """Prédiction avec le modèle DistilBERT"""
        if not self._model_loaded:
            return {'probability_attack': 0.3, 'confidence': 0.0}
        
        try:
            import torch.nn.functional as F
            
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                padding=True, 
                max_length=256
            )
            
            inputs = {key: value.to(self.device) for key, value in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = F.softmax(outputs.logits, dim=-1)
                
            attack_prob = probabilities[0][1].item()
            
            return {
                'probability_attack': attack_prob,
                'confidence': abs(attack_prob - 0.5) * 2,
                'raw_probabilities': {
                    'normal': probabilities[0][0].item(),
                    'attack': probabilities[0][1].item()
                }
            }
            
        except Exception as e:
            print(f"❌ Erreur prédiction BERT: {e}")
            return {'probability_attack': 0.3, 'confidence': 0.0}
    
    def prepare_text_for_bert(self, log_data):
        """Prépare le texte pour BERT de façon optimisée"""
        parts = []
        
        email = log_data.get('email', 'unknown')
        ip = log_data.get('IP Address', '0.0.0.0')
        country = log_data.get('Country', 'unknown')
        success = log_data.get('Login Successful', False)
        browser = log_data.get('Browser Name and Version', 'unknown')
        os_info = log_data.get('OS Name and Version', 'unknown')
        user_id = log_data.get('User ID', 'unknown')
        
        parts.append(f"User {user_id} from {ip} in {country}")
        parts.append(f"Email: {email}")
        parts.append(f"Browser: {browser} on {os_info}")
        parts.append(f"Login {'successful' if success else 'failed'}")
        
        if country in ['Unknown', 'RU', 'CN', 'KP', 'IR']:
            parts.append("Suspicious country")
        
        if ip in ['127.0.0.1', 'localhost', '0.0.0.0']:
            parts.append("Local IP address")
            
        if 'Unknown' in browser or 'python' in browser.lower():
            parts.append("Suspicious browser")
        
        return ". ".join(parts)
    
    def analyze_behavioral_patterns(self, log_data):
        """Analyse comportementale améliorée"""
        score = 0.0
        flags = []
        
        ip_address = log_data.get('IP Address')
        country = log_data.get('Country', 'Unknown')
        login_success = log_data.get('Login Successful', False)
        browser = log_data.get('Browser Name and Version', '')
        email = log_data.get('email', '')
        
        if ip_address in ['127.0.0.1', 'localhost']:
            score += 0.4
            flags.append('local_ip')
        
        if country == 'Unknown':
            score += 0.3
            flags.append('unknown_country')
        elif country in ['RU', 'CN', 'KP', 'IR']:
            score += 0.2
            flags.append('suspicious_country')
        
        if 'Unknown' in browser or 'python' in browser.lower():
            score += 0.3
            flags.append('suspicious_browser')
        
        if not login_success:
            score += 0.1
            flags.append('login_failed')
        
        if any(suspicious in email for suspicious in ['admin', 'root', 'test', 'hacker']):
            score += 0.2
            flags.append('suspicious_email')
        
        return {'score': min(score, 1.0), 'flags': flags}
    
    def combine_predictions(self, bert_prediction, behavioral_analysis, log_data):
        """Combine les prédictions BERT et comportementales"""
        bert_score = bert_prediction['probability_attack']
        behavioral_score = behavioral_analysis['score']
        
        if self._model_loaded:
            combined_score = (bert_score * 0.7) + (behavioral_score * 0.3)
        else:
            combined_score = behavioral_score
        
        is_attack = combined_score > self.threshold
        
        attack_type = "normal"
        if is_attack:
            if self._model_loaded and bert_score > 0.7:
                attack_type = "bert_detected"
            elif self._model_loaded and bert_score > 0.5:
                attack_type = "bert_suspected"
            else:
                attack_type = "behavioral_anomaly"
        
        return is_attack, combined_score, attack_type
    
    def update_activity_tracking(self, log_data):
        """Met à jour le suivi d'activité"""
        user_id = log_data.get('User ID')
        ip_address = log_data.get('IP Address')
        timestamp = datetime.now()
        
        event_data = {
            'timestamp': timestamp,
            'ip': ip_address,
            'success': log_data.get('Login Successful', False),
            'email': log_data.get('email', 'unknown')
        }
        
        if user_id:
            self.user_activity[user_id].append(event_data)
        
        if ip_address:
            self.ip_activity[ip_address].append(event_data)
        
        self.recent_events.append(event_data)
    
    def log_attack(self, log_data, confidence, attack_type, bert_prediction):
        """Log les attaques détectées - version améliorée"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'email': log_data.get('email'),
            'user_id': log_data.get('User ID'),
            'ip_address': log_data.get('IP Address'),
            'country': log_data.get('Country'),
            'attack_type': attack_type,
            'confidence': confidence,
            'bert_probability': bert_prediction.get('probability_attack'),
            'bert_used': self._model_loaded,
            'login_successful': log_data.get('Login Successful', False)
        }
        
        # ✅ Log dans le fichier
        self.logger.warning(f"🚨 ATTAQUE DÉTECTÉE: {json.dumps(log_entry)}")
        
        try:
            # ✅ Fichier JSONL dans logs/
            with open(self.logs_dir / 'detected_attacks.jsonl', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.logger.error(f"❌ Erreur écriture JSONL: {e}")
    
    def get_statistics(self):
        """Retourne les statistiques détaillées - version améliorée"""
        stats = self.stats.copy()
        stats['bert_available'] = self._model_loaded
        stats['active_users'] = len(self.user_activity)
        stats['active_ips'] = len(self.ip_activity)
        stats['bert_usage_rate'] = stats['bert_predictions'] / max(1, stats['total_requests'])
        
        # ✅ Calculer les taux
        if stats['total_requests'] > 0:
            stats['attack_rate'] = stats['detected_attacks'] / stats['total_requests']
            stats['false_positive_rate'] = stats['false_positives'] / max(1, stats['detected_attacks'])
        else:
            stats['attack_rate'] = 0
            stats['false_positive_rate'] = 0
        
        # ✅ Ajouter des informations sur les résultats récents
        stats['recent_attack_count'] = sum(1 for r in self.recent_results if r['is_attack'])
        stats['total_results'] = len(self.recent_results)
        
        return stats
    
    def get_recent_attacks(self, limit=10):
        """Retourne les attaques récentes pour l'interface"""
        attacks = [r for r in self.recent_results if r['is_attack']]
        return attacks[-limit:] if attacks else []
    
    def get_detailed_stats(self):
        """Retourne des statistiques détaillées pour l'affichage"""
        stats = self.get_statistics()
        
        return {
            'total_requests': stats['total_requests'],
            'detected_attacks': stats['detected_attacks'],
            'attack_rate': f"{stats['attack_rate']:.2%}",
            'bert_available': stats['bert_available'],
            'active_users': stats['active_users'],
            'active_ips': stats['active_ips'],
            'bert_usage': f"{stats['bert_usage_rate']:.2%}",
            'recent_attacks': stats['recent_attack_count'],
            'last_update': datetime.now().strftime('%H:%M:%S')
        }
    
    def cleanup_old_events(self):
        """Nettoie les événements anciens"""
        now = datetime.now()
        cutoff_time = now - self.time_window
        
        for user_id in list(self.user_activity.keys()):
            self.user_activity[user_id] = deque(
                [e for e in self.user_activity[user_id] if e['timestamp'] > cutoff_time],
                maxlen=50
            )
            if not self.user_activity[user_id]:
                del self.user_activity[user_id]
        
        for ip in list(self.ip_activity.keys()):
            self.ip_activity[ip] = deque(
                [e for e in self.ip_activity[ip] if e['timestamp'] > cutoff_time],
                maxlen=100
            )
            if not self.ip_activity[ip]:
                del self.ip_activity[ip]

def start_fixed_cleanup_thread(detector, interval_minutes=5):
    """Démarre le thread de nettoyage"""
    def cleanup_loop():
        while True:
            time.sleep(interval_minutes * 60)
            detector.cleanup_old_events()
            detector.logger.info("🧹 Nettoyage des anciens événements effectué")
    
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    return thread