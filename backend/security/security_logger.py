import json
import csv
import logging
from datetime import datetime
from pathlib import Path
import requests
import user_agents
from flask import request
import hashlib
from collections import deque

class SecurityLogger:
    def __init__(self, log_file='security_logs.json', csv_file='security_logs.csv'):
        # ✅ Créer le dossier logs à la racine du projet
        project_root = Path(__file__).parent.parent.parent  # backend/security/ -> backend/ -> racine/
        self.logs_dir = project_root / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
        # ✅ Chemins corrigés vers logs/
        self.log_file = self.logs_dir / log_file
        self.csv_file = self.logs_dir / csv_file
        
        # ✅ Stockage en mémoire pour l'interface
        self.recent_logs = deque(maxlen=1000)  # Garde les 1000 derniers logs
        self.stats_cache = None
        self.last_stats_update = None
        
        self.setup_logging()
        
    def setup_logging(self):
        """Configuration du système de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'security_events.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('security')
        
    def get_client_info(self):
        """Récupère les informations du client"""
        try:
            # Adresse IP (gère les proxies)
            if request.headers.get('X-Forwarded-For'):
                ip = request.headers.get('X-Forwarded-For').split(',')[0]
            elif request.headers.get('X-Real-IP'):
                ip = request.headers.get('X-Real-IP')
            else:
                ip = request.remote_addr
            
            # User Agent
            user_agent_str = request.headers.get('User-Agent', 'Unknown')
            
            # Parse User Agent
            ua = user_agents.parse(user_agent_str)
            
            # Géolocalisation (simplifiée)
            geo_info = self.get_geo_info(ip)
            
            # Temps de réponse (approximatif)
            rtt = self.estimate_rtt()
            
            return {
                'ip_address': ip,
                'country': geo_info.get('country', 'Unknown'),
                'region': geo_info.get('region', 'Unknown'),
                'city': geo_info.get('city', 'Unknown'),
                'asn': geo_info.get('asn', 0),
                'user_agent_string': user_agent_str,
                'os_name_version': f"{ua.os.family} {ua.os.version_string}",
                'browser_name_version': f"{ua.browser.family} {ua.browser.version_string}",
                'device_type': self.get_device_type(ua),
                'round_trip_time': rtt,
                'timestamp': int(datetime.now().timestamp() * 1000),
                'human_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erreur récupération info client: {e}")
            return self.get_fallback_client_info()
    
    def get_geo_info(self, ip):
        """Récupère les informations géographiques (version simplifiée)"""
        try:
            if ip in ['127.0.0.1', 'localhost', '0.0.0.0']:
                return {'country': 'Local', 'region': 'Local', 'city': 'Local', 'asn': 0}
            
            # Tentative de géolocalisation basique
            if not ip.startswith('192.168.') and not ip.startswith('10.'):
                try:
                    # API gratuite pour test - limiter les appels
                    response = requests.get(f'http://ip-api.com/json/{ip}?fields=country,regionName,city,as', timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'country': data.get('country', 'Unknown'),
                            'region': data.get('regionName', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'asn': data.get('as', 0)
                        }
                except:
                    pass
            
            return {
                'country': 'Unknown',
                'region': 'Unknown', 
                'city': 'Unknown',
                'asn': 0
            }
        except:
            return {'country': 'Unknown', 'region': 'Unknown', 'city': 'Unknown', 'asn': 0}
    
    def get_device_type(self, ua):
        """Détermine le type d'appareil"""
        if ua.is_mobile:
            return 'mobile'
        elif ua.is_tablet:
            return 'tablet'
        elif ua.is_pc:
            return 'desktop'
        elif ua.is_bot:
            return 'bot'
        else:
            return 'unknown'
    
    def estimate_rtt(self):
        """Estime le temps de réponse (simplifié)"""
        return 50  # Valeur par défaut en ms
    
    def get_fallback_client_info(self):
        """Informations client par défaut en cas d'erreur"""
        return {
            'ip_address': '0.0.0.0',
            'country': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'asn': 0,
            'user_agent_string': 'Unknown',
            'os_name_version': 'Unknown',
            'browser_name_version': 'Unknown',
            'device_type': 'unknown',
            'round_trip_time': 0,
            'timestamp': int(datetime.now().timestamp() * 1000),
            'human_timestamp': datetime.now().isoformat()
        }
    
    def log_login_attempt(self, user_id, email, successful, failure_reason=None, is_attack_ip=False, is_account_takeover=False, attack_detection_result=None):
        """Log une tentative de connexion - version améliorée"""
        try:
            client_info = self.get_client_info()
            
            log_entry = {
                **client_info,
                'user_id': self.anonymize_user_id(user_id) if user_id else 0,
                'email': email,
                'login_successful': successful,
                'failure_reason': failure_reason,
                'is_attack_ip': is_attack_ip,
                'is_account_takeover': is_account_takeover,
                'session_id': hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:16],
                'log_id': hashlib.md5(f"{email}{client_info['timestamp']}".encode()).hexdigest()[:8]
            }
            
            # ✅ Ajouter les résultats de détection d'attaque si disponibles
            if attack_detection_result:
                log_entry['attack_detection'] = {
                    'is_attack': attack_detection_result.get('is_attack', False),
                    'confidence': attack_detection_result.get('confidence', 0),
                    'attack_type': attack_detection_result.get('attack_type', 'normal'),
                    'bert_used': attack_detection_result.get('bert_used', False)
                }
            
            # Sauvegarde JSON
            self.save_json_log(log_entry)
            
            # Sauvegarde CSV
            self.save_csv_log(log_entry)
            
            # ✅ Stocker en mémoire pour l'interface
            self.recent_logs.append(log_entry)
            
            # ✅ Invalider le cache des stats
            self.stats_cache = None
            
            # Logging structuré avec plus d'informations
            self.log_structured_event(log_entry)
            
            # Détection d'anomalies
            self.detect_anomalies(log_entry)
            
            # ✅ Afficher un résumé dans la console
            self.print_summary(log_entry)
            
            return log_entry
            
        except Exception as e:
            self.logger.error(f"Erreur logging tentative connexion: {e}")
            return None
    
    def anonymize_user_id(self, user_id):
        """Anonymise l'ID utilisateur pour la privacy"""
        return hashlib.sha256(str(user_id).encode()).hexdigest()[:16]
    
    def save_json_log(self, log_entry):
        """Sauvegarde en format JSON"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde JSON: {e}")
    
    def save_csv_log(self, log_entry):
        """Sauvegarde en format CSV"""
        try:
            # Vérifier si le fichier existe pour écrire l'en-tête
            file_exists = self.csv_file.exists()
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                # Créer une copie sans nested dict pour CSV
                csv_entry = log_entry.copy()
                if 'attack_detection' in csv_entry:
                    csv_entry['is_attack'] = csv_entry['attack_detection'].get('is_attack', False)
                    csv_entry['attack_confidence'] = csv_entry['attack_detection'].get('confidence', 0)
                    csv_entry['attack_type'] = csv_entry['attack_detection'].get('attack_type', 'normal')
                    del csv_entry['attack_detection']
                
                writer = csv.DictWriter(f, fieldnames=csv_entry.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(csv_entry)
                
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde CSV: {e}")
    
    def log_structured_event(self, log_entry):
        """Logging structuré pour analyse"""
        status = "SUCCESS" if log_entry['login_successful'] else "FAILED"
        attack_info = ""
        
        if 'attack_detection' in log_entry and log_entry['attack_detection'].get('is_attack', False):
            attack_info = f" - ATTACK:{log_entry['attack_detection']['attack_type']}({log_entry['attack_detection']['confidence']:.0%})"
        
        self.logger.info(
            f"LOGIN_ATTEMPT - IP:{log_entry['ip_address']} - "
            f"User:{log_entry['email']} - Status:{status} - "
            f"Device:{log_entry['device_type']} - Country:{log_entry['country']}"
            f"{attack_info}"
        )
    
    def print_summary(self, log_entry):
        """Affiche un résumé dans la console pour l'interface"""
        status = "✅ SUCCESS" if log_entry['login_successful'] else "❌ FAILED"
        attack_status = ""
        
        if 'attack_detection' in log_entry and log_entry['attack_detection'].get('is_attack', False):
            attack_status = f" | 🚨 ATTACK: {log_entry['attack_detection']['attack_type']}"
        
        print(f"[{log_entry['human_timestamp']}] {status} - {log_entry['email']} from {log_entry['ip_address']} ({log_entry['country']}){attack_status}")
    
    def detect_anomalies(self, log_entry):
        """Détection basique d'anomalies"""
        anomalies = []
        
        # IP suspecte
        if self.is_suspicious_ip(log_entry['ip_address']):
            anomalies.append("SUSPICIOUS_IP")
        
        # User Agent suspect
        if self.is_suspicious_user_agent(log_entry['user_agent_string']):
            anomalies.append("SUSPICIOUS_UA")
        
        # Nombre élevé de tentatives récentes
        recent_attempts = self.get_recent_attempts_count(log_entry['ip_address'], minutes=5)
        if recent_attempts > 10:
            anomalies.append("HIGH_FREQUENCY")
        
        if anomalies:
            log_entry['detected_anomalies'] = anomalies
            self.logger.warning(f"Anomalies détectées: {anomalies} pour IP: {log_entry['ip_address']}")
    
    def get_recent_attempts_count(self, ip, minutes=5):
        """Compte les tentatives récentes pour une IP"""
        cutoff = datetime.now().timestamp() * 1000 - (minutes * 60 * 1000)
        count = sum(1 for log in self.recent_logs 
                   if log['ip_address'] == ip and log['timestamp'] > cutoff)
        return count
    
    def is_suspicious_ip(self, ip):
        """Vérifie si l'IP est suspecte"""
        suspicious_ips = []  # À enrichir avec une liste dynamique
        return ip in suspicious_ips or ip == '0.0.0.0'
    
    def is_suspicious_user_agent(self, user_agent):
        """Vérifie si le User Agent est suspect"""
        suspicious_patterns = ['bot', 'crawler', 'scraper', 'python', 'curl', 'wget', 'headless']
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)
    
    def get_login_stats(self, hours=24):
        """Récupère les statistiques de connexion - version optimisée"""
        try:
            # Utiliser le cache si récent (moins de 5 secondes)
            if self.stats_cache and self.last_stats_update:
                time_since_update = (datetime.now() - self.last_stats_update).total_seconds()
                if time_since_update < 5:
                    return self.stats_cache
            
            # Calculer les stats
            cutoff_time = datetime.now().timestamp() * 1000 - (hours * 3600 * 1000)
            recent_logs = [log for log in self.recent_logs if log['timestamp'] > cutoff_time]
            
            if not recent_logs:
                # Charger depuis le fichier si la mémoire est vide
                if self.log_file.exists():
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        logs = [json.loads(line) for line in f if line.strip()]
                    recent_logs = [log for log in logs if log['timestamp'] > cutoff_time]
            
            if not recent_logs:
                stats = self.get_empty_stats()
            else:
                stats = self.calculate_stats(recent_logs)
            
            # Mettre en cache
            self.stats_cache = stats
            self.last_stats_update = datetime.now()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erreur calcul stats: {e}")
            return self.get_empty_stats()
    
    def calculate_stats(self, logs):
        """Calcule les statistiques à partir des logs"""
        attack_count = sum(1 for log in logs 
                          if log.get('attack_detection', {}).get('is_attack', False))
        
        countries = list(set(log['country'] for log in logs if log['country'] != 'Unknown'))
        
        return {
            'total_attempts': len(logs),
            'successful_logins': len([log for log in logs if log['login_successful']]),
            'failed_logins': len([log for log in logs if not log['login_successful']]),
            'unique_ips': len(set(log['ip_address'] for log in logs)),
            'unique_users': len(set(log['user_id'] for log in logs if log['user_id'])),
            'countries': countries,
            'country_count': len(countries),
            'suspicious_attempts': len([log for log in logs if log.get('detected_anomalies')]),
            'detected_attacks': attack_count,
            'attack_rate': attack_count / max(1, len(logs)),
            'success_rate': len([log for log in logs if log['login_successful']]) / max(1, len(logs)),
            'last_update': datetime.now().isoformat()
        }
    
    def get_empty_stats(self):
        """Retourne des stats vides"""
        return {
            'total_attempts': 0,
            'successful_logins': 0,
            'failed_logins': 0,
            'unique_ips': 0,
            'unique_users': 0,
            'countries': [],
            'country_count': 0,
            'suspicious_attempts': 0,
            'detected_attacks': 0,
            'attack_rate': 0,
            'success_rate': 0,
            'last_update': datetime.now().isoformat()
        }
    
    def get_recent_logs(self, count=20):
        """Retourne les logs récents pour l'interface"""
        return list(self.recent_logs)[-count:] if self.recent_logs else []
    
    def get_detailed_stats_for_ui(self):
        """Retourne des statistiques formatées pour l'interface"""
        stats = self.get_login_stats(24)
        
        return {
            'total_attempts': stats['total_attempts'],
            'successful_logins': stats['successful_logins'],
            'failed_logins': stats['failed_logins'],
            'unique_ips': stats['unique_ips'],
            'unique_users': stats['unique_users'],
            'country_count': stats['country_count'],
            'detected_attacks': stats['detected_attacks'],
            'suspicious_attempts': stats['suspicious_attempts'],
            'attack_rate': f"{stats['attack_rate']:.2%}",
            'success_rate': f"{stats['success_rate']:.2%}",
            'last_update': stats['last_update']
        }
    
    def clear_recent_logs(self):
        """Vide le buffer des logs récents"""
        self.recent_logs.clear()
        self.stats_cache = None
        self.logger.info("Buffer des logs récents vidé")

# Instance globale
security_logger = SecurityLogger()