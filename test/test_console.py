# import requests
# import time
# import json
# import random
# from datetime import datetime

# def run_specific_test(test_type):
#     """Exécute un test spécifique et retourne les résultats formatés pour l'interface web"""
#     results = []
#     base_url = "http://localhost:5000"
    
#     try:
#         if test_type == "bruteforce":
#             results.append({"message": "🧪 Démarrage du test Force Brute...", "type": "info"})
            
#             emails = ["admin@company.com", "root@system.com", "user@test.com", "victim@target.com"]
            
#             for i in range(10):  # Réduit à 10 pour les tests web
#                 try:
#                     response = requests.post(
#                         f'{base_url}/api/login', 
#                         json={
#                             'email': random.choice(emails), 
#                             'password': f'wrongpassword{i}'
#                         },
#                         headers={'User-Agent': 'python-requests/2.32.5'},
#                         timeout=2
#                     )
                    
#                     if response.status_code == 429:
#                         result_data = response.json()
#                         confidence = result_data.get('detection_details', {}).get('confidence', 0)
#                         attack_type = result_data.get('detection_details', {}).get('attack_type', 'unknown')
#                         results.append({
#                             "message": f"🚨 Tentative {i+1}: BLOQUÉE - {attack_type} (Confiance: {confidence:.2f})",
#                             "type": "error"
#                         })
#                     else:
#                         results.append({
#                             "message": f"⚠️ Tentative {i+1}: Réponse {response.status_code}",
#                             "type": "warning"
#                         })
                    
#                     time.sleep(0.1)
                    
#                 except Exception as e:
#                     results.append({
#                         "message": f"❌ Erreur tentative {i+1}: {str(e)}",
#                         "type": "error"
#                     })
            
#             results.append({"message": "✅ Test Force Brute terminé avec succès", "type": "success"})
            
#         elif test_type == "sql_injection":
#             results.append({"message": "🧪 Démarrage du test Injection SQL...", "type": "info"})
            
#             sql_payloads = [
#                 {"payload": "' OR '1'='1' --", "description": "Bypass d'authentification classique"},
#                 {"payload": "' UNION SELECT 1,2,3 --", "description": "Injection UNION"}, 
#                 {"payload": "'; DROP TABLE users --", "description": "Suppression de table"},
#                 {"payload": "' OR 1=1 --", "description": "Condition toujours vraie"},
#                 {"payload": "admin' --", "description": "Commentaire SQL"},
#                 {"payload": "' OR 'a'='a", "description": "Condition string"},
#                 {"payload": "') OR ('1'='1", "description": "Bypass parenthèses"},
#                 {"payload": "' OR 1=1#", "description": "Commentaire MySQL"}
#             ]
            
#             for payload_info in sql_payloads:
#                 try:
#                     response = requests.post(
#                         f'{base_url}/api/login',
#                         json={'email': payload_info['payload'], 'password': 'test'},
#                         timeout=2
#                     )
                    
#                     if response.status_code == 429:
#                         results.append({
#                             "message": f"🚨 Injection SQL détectée: {payload_info['description']}",
#                             "type": "error"
#                         })
#                     else:
#                         results.append({
#                             "message": f"⚠️ Payload passé: {payload_info['description']}",
#                             "type": "warning"
#                         })
                    
#                     time.sleep(0.1)
                    
#                 except Exception as e:
#                     results.append({
#                         "message": f"❌ Erreur payload: {str(e)}",
#                         "type": "error"
#                     })
            
#             results.append({"message": "✅ Test Injection SQL terminé avec succès", "type": "success"})
            
#         elif test_type == "suspicious_ips":
#             results.append({"message": "🧪 Démarrage du test IPs Suspectes...", "type": "info"})
            
#             suspicious_combinations = [
#                 {'ip': '185.220.101.1', 'country': 'DE', 'email': 'hacker@evil.com', 'desc': 'Allemagne (suspect)'},
#                 {'ip': '192.168.1.666', 'country': 'Unknown', 'email': 'bot@network.com', 'desc': 'IP invalide'},
#                 {'ip': '45.129.56.1', 'country': 'RU', 'email': 'attacker@mail.ru', 'desc': 'Russie'},
#                 {'ip': '103.216.154.1', 'country': 'CN', 'email': 'spy@china.com', 'desc': 'Chine'},
#                 {'ip': '127.0.0.1', 'country': 'Local', 'email': 'local@hack.com', 'desc': 'IP locale'},
#             ]
            
#             for combo in suspicious_combinations:
#                 try:
#                     security_data = {
#                         'email': combo['email'],
#                         'IP Address': combo['ip'],
#                         'Country': combo['country'],
#                         'Browser Name and Version': 'Unknown Bot',
#                         'OS Name and Version': 'Unknown',
#                         'Device Type': 'unknown',
#                         'Login Successful': False,
#                         'timestamp': datetime.now().isoformat()
#                     }
                    
#                     response = requests.post(
#                         f'{base_url}/api/security/analyze-login',
#                         json=security_data,
#                         timeout=5
#                     )
                    
#                     if response.status_code == 429:
#                         result_data = response.json()
#                         confidence = result_data.get('detection_result', {}).get('confidence', 0)
#                         results.append({
#                             "message": f"🚨 IP suspecte détectée: {combo['desc']} (Confiance: {confidence:.2f})",
#                             "type": "error"
#                         })
#                     else:
#                         results.append({
#                             "message": f"⚠️ IP analysée: {combo['desc']}",
#                             "type": "info"
#                         })
                    
#                     time.sleep(0.1)
                    
#                 except Exception as e:
#                     results.append({
#                         "message": f"❌ Erreur IP {combo['ip']}: {str(e)}",
#                         "type": "error"
#                     })
            
#             results.append({"message": "✅ Test IPs Suspectes terminé avec succès", "type": "success"})
            
#         elif test_type == "malicious_agents":
#             results.append({"message": "🧪 Démarrage du test User Agents...", "type": "info"})
            
#             malicious_agents = [
#                 {"ua": "Mozilla/5.0 (compatible; EvilBot/1.0; +http://evil.com/bot)", "desc": "Bot malveillant"},
#                 {"ua": "python-requests/2.25.1", "desc": "Script Python"},
#                 {"ua": "Go-http-client/1.1", "desc": "Client Go"},
#                 {"ua": "Java/1.8.0_251", "desc": "Application Java"},
#                 {"ua": "curl/7.68.0", "desc": "Client cURL"},
#                 {"ua": "Mozilla/5.0 (X11; Linux x86_64) Scanner/1.0", "desc": "Scanner sécurité"},
#                 {"ua": "Mozilla/5.0 (compatible; BruteForceBot/2.0)", "desc": "Bot force brute"},
#                 {"ua": "sqlmap/1.6#dev (http://sqlmap.org)", "desc": "Outil SQLMap"},
#                 {"ua": "nikto/2.1.6", "desc": "Scanner Nikto"},
#                 {"ua": "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.0)", "desc": "Vieil Internet Explorer"},
#             ]
            
#             for agent_info in malicious_agents:
#                 try:
#                     response = requests.post(
#                         f'{base_url}/api/login', 
#                         json={
#                             'email': f'bot{random.randint(1000,9999)}@network.com', 
#                             'password': 'botpassword'
#                         },
#                         headers={'User-Agent': agent_info['ua']},
#                         timeout=2
#                     )
                    
#                     if response.status_code == 429:
#                         results.append({
#                             "message": f"🚨 UA malveillant détecté: {agent_info['desc']}",
#                             "type": "error"
#                         })
#                     else:
#                         results.append({
#                             "message": f"⚠️ UA analysé: {agent_info['desc']}",
#                             "type": "warning"
#                         })
                    
#                     time.sleep(0.1)
                    
#                 except Exception as e:
#                     results.append({
#                         "message": f"❌ Erreur UA: {str(e)}",
#                         "type": "error"
#                     })
            
#             results.append({"message": "✅ Test User Agents terminé avec succès", "type": "success"})
            
#         elif test_type == "abnormal_behavior":
#             results.append({"message": "🧪 Démarrage du test Comportement Anormal...", "type": "info"})
            
#             mixed_behavior = [
#                 {'email': 'legit@user.com', 'success': True, 'ip': '10.0.0.1', 'desc': 'Connexion réussie'},
#                 {'email': 'legit@user.com', 'success': False, 'ip': '10.0.0.2', 'desc': 'Échec connexion'},
#                 {'email': 'legit@user.com', 'success': False, 'ip': '10.0.0.3', 'desc': 'Échec répété'},
#                 {'email': 'legit@user.com', 'success': True, 'ip': '10.0.0.4', 'desc': 'Changement IP rapide'},
#                 {'email': 'legit@user.com', 'success': False, 'ip': '10.0.0.5', 'desc': 'Comportement erratique'},
#             ]
            
#             for behavior in mixed_behavior:
#                 try:
#                     security_data = {
#                         'email': behavior['email'],
#                         'IP Address': behavior['ip'],
#                         'Country': 'US',
#                         'Browser Name and Version': 'Chrome/120.0.0.0',
#                         'OS Name and Version': 'Windows 10',
#                         'Device Type': 'desktop',
#                         'Login Successful': behavior['success'],
#                         'User ID': '12345',
#                         'timestamp': datetime.now().isoformat()
#                     }
                    
#                     response = requests.post(
#                         f'{base_url}/api/security/analyze-login',
#                         json=security_data,
#                         timeout=5
#                     )
                    
#                     if response.status_code == 429:
#                         result_data = response.json()
#                         confidence = result_data.get('detection_result', {}).get('confidence', 0)
#                         results.append({
#                             "message": f"🚨 Comportement anormal détecté: {behavior['desc']} (Confiance: {confidence:.2f})",
#                             "type": "error"
#                         })
#                     else:
#                         results.append({
#                             "message": f"⚠️ Comportement analysé: {behavior['desc']}",
#                             "type": "info"
#                         })
                    
#                     time.sleep(0.2)
                    
#                 except Exception as e:
#                     results.append({
#                         "message": f"❌ Erreur comportement: {str(e)}",
#                         "type": "error"
#                     })
            
#             results.append({"message": "✅ Test Comportement Anormal terminé avec succès", "type": "success"})
            
#         elif test_type == "full_test":
#             results.append({"message": "🎯 DÉMARRAGE DU TEST COMPLET DE SÉCURITÉ", "type": "info"})
            
#             # Exécute tous les tests dans l'ordre
#             test_types = ["bruteforce", "sql_injection", "suspicious_ips", "malicious_agents", "abnormal_behavior"]
            
#             for test in test_types:
#                 results.append({"message": f"🔧 Exécution du test: {test.upper()}", "type": "info"})
#                 test_results = run_specific_test(test)  # Appel récursif
#                 results.extend(test_results)
#                 results.append({"message": f"✅ Test {test} complété", "type": "success"})
#                 time.sleep(1)
            
#             results.append({"message": "🎉 TOUS LES TESTS DE SÉCURITÉ TERMINÉS AVEC SUCCÈS!", "type": "success"})
#             results.append({"message": "🛡️ Votre système BERT fonctionne parfaitement!", "type": "success"})
            
#         else:
#             results.append({
#                 "message": f"❌ Type de test inconnu: {test_type}",
#                 "type": "error"
#             })
            
#     except Exception as e:
#         results.append({
#             "message": f"❌ Erreur générale du test: {str(e)}",
#             "type": "error"
#         })
    
#     return results

# # Gardez votre fonction de test originale pour les tests en ligne de commande
# def test_attack_detection():
#     print("🔥 TEST AGGRESSIF DE DÉTECTION D'ATTAQUES BERT")
#     print("=" * 60)
    
#     base_url = "http://localhost:5000"
#     attack_count = 0
#     blocked_count = 0
    
#     # Votre code original reste ici...
#     # ... (le reste de votre fonction test_attack_detection existante)

# if __name__ == "__main__":
#     # Vérification que le serveur est démarré
#     print("🔍 Vérification du serveur...")
#     try:
#         response = requests.get("http://localhost:5000", timeout=5)
#         if response.status_code == 200:
#             print("✅ Serveur actif - Lancement des tests d'attaque...")
#             test_attack_detection()
#         else:
#             print("❌ Serveur non disponible ")
#     except Exception as e:
#         print(f"❌ Impossible de se connecter au serveur: {e}")
#         print("💡 Assurez-vous que le serveur est démarré: python start_server.py")


import requests
import time
import json
import random
from datetime import datetime

# ============================================================
#      VERSION CONSOLE : AFFICHAGE DIRECT AVEC PRINT()
# ============================================================

def run_specific_test_console(test_type):
    """Exécute un test et affiche les résultats uniquement dans la console."""
    base_url = "http://localhost:5000"

    print(f"\n🔧 Lancement du test : {test_type.upper()}")
    print("-" * 60)

    # -----------------------
    #       BRUTE FORCE
    # -----------------------
    if test_type == "bruteforce":
        print("🧪 Test Force Brute...")

        emails = ["admin@company.com", "root@system.com", "user@test.com", "victim@target.com"]

        for i in range(10):
            try:
                response = requests.post(
                    f'{base_url}/api/login',
                    json={'email': random.choice(emails), 'password': f'wrongpassword{i}'},
                    headers={'User-Agent': 'python-requests/2.32.5'},
                    timeout=2
                )

                if response.status_code == 429:
                    data = response.json()
                    conf = data.get('detection_details', {}).get('confidence', 0)
                    atk = data.get('detection_details', {}).get('attack_type', 'unknown')
                    print(f"🚨 Tentative {i+1}: BLOQUÉE → {atk}  (Confiance {conf:.2f})")
                else:
                    print(f"⚠️ Tentative {i+1}: Réponse HTTP {response.status_code}")

            except Exception as e:
                print(f"❌ Erreur tentative {i+1}: {e}")

            time.sleep(0.1)

        print("✅ Test Force Brute terminé")

    # -----------------------
    #       SQL INJECTION
    # -----------------------
    elif test_type == "sql_injection":
        print("🧪 Test Injection SQL...")

        sql_payloads = [
            {"payload": "' OR '1'='1' --", "description": "Bypass simple"},
            {"payload": "' UNION SELECT 1,2,3 --", "description": "Injection UNION"},
            {"payload": "'; DROP TABLE users --", "description": "DROP TABLE"},
            {"payload": "' OR 1=1 --", "description": "True condition"},
            {"payload": "admin' --", "description": "Commentaire SQL"},
            {"payload": "' OR 'a'='a", "description": "String always true"},
            {"payload": "') OR ('1'='1", "description": "Bypass parenthèses"},
            {"payload": "' OR 1=1#", "description": "Commentaire MySQL"}
        ]

        for p in sql_payloads:
            try:
                response = requests.post(
                    f'{base_url}/api/login',
                    json={'email': p['payload'], 'password': 'test'},
                    timeout=2
                )

                if response.status_code == 429:
                    print(f"🚨 Injection SQL détectée : {p['description']}")
                else:
                    print(f"⚠️ Payload passé : {p['description']}")

            except Exception as e:
                print(f"❌ Erreur payload : {e}")

            time.sleep(0.1)

        print("✅ Test Injection SQL terminé")

    # -----------------------
    #       IP SUSPECTES
    # -----------------------
    elif test_type == "suspicious_ips":
        print("🧪 Test IPs suspectes...")

        combos = [
            {'ip': '185.220.101.1', 'country': 'DE', 'email': 'hacker@evil.com', 'desc': 'Allemagne (suspect)'},
            {'ip': '192.168.1.666', 'country': 'Unknown', 'email': 'bot@network.com', 'desc': 'IP invalide'},
            {'ip': '45.129.56.1', 'country': 'RU', 'email': 'attacker@mail.ru', 'desc': 'Russie'},
            {'ip': '103.216.154.1', 'country': 'CN', 'email': 'spy@china.com', 'desc': 'Chine'},
            {'ip': '127.0.0.1', 'country': 'Local', 'email': 'local@hack.com', 'desc': 'IP locale'}
        ]

        for combo in combos:
            try:
                security_data = {
                    'email': combo['email'],
                    'IP Address': combo['ip'],
                    'Country': combo['country'],
                    'Browser Name and Version': 'Unknown Bot',
                    'OS Name and Version': 'Unknown',
                    'Device Type': 'unknown',
                    'Login Successful': False,
                    'timestamp': datetime.now().isoformat()
                }

                response = requests.post(
                    f'{base_url}/api/security/analyze-login',
                    json=security_data,
                    timeout=5
                )

                if response.status_code == 429:
                    data = response.json()
                    conf = data.get('detection_result', {}).get('confidence', 0)
                    print(f"🚨 IP suspecte détectée : {combo['desc']} (Conf {conf:.2f})")
                else:
                    print(f"ℹ️ IP analysée : {combo['desc']}")

            except Exception as e:
                print(f"❌ Erreur IP {combo['ip']} : {e}")

            time.sleep(0.1)

        print("✅ Test IPs suspectes terminé")

    # -----------------------
    #       USER AGENTS
    # -----------------------
    elif test_type == "malicious_agents":
        print("🧪 Test User Agents malveillants...")

        agents = [
            {"ua": "Mozilla/5.0 (compatible; EvilBot/1.0)", "desc": "Bot malveillant"},
            {"ua": "python-requests/2.25.1", "desc": "Script Python"},
            {"ua": "Go-http-client/1.1", "desc": "Client Go"},
            {"ua": "Java/1.8.0_251", "desc": "Java App"},
            {"ua": "curl/7.68.0", "desc": "cURL"},
            {"ua": "sqlmap/1.6#dev", "desc": "SQLMap"},
        ]

        for agent in agents:
            try:
                response = requests.post(
                    f'{base_url}/api/login',
                    json={'email': 'bot@test.com', 'password': 'bot'},
                    headers={'User-Agent': agent['ua']},
                    timeout=2
                )

                if response.status_code == 429:
                    print(f"🚨 UA détecté : {agent['desc']}")
                else:
                    print(f"⚠️ UA analysé : {agent['desc']}")

            except Exception as e:
                print(f"❌ Erreur UA : {e}")

        print("✅ Test User Agents terminé")

    # -----------------------
    #       COMPORTEMENT ANORMAL
    # -----------------------
    elif test_type == "abnormal_behavior":
        print("🧪 Test comportement anormal...")

        behaviors = [
            {'email': 'legit@user.com', 'success': True,  'ip': '10.0.0.1', 'desc': 'Connexion réussie'},
            {'email': 'legit@user.com', 'success': False, 'ip': '10.0.0.2', 'desc': 'Échec connexion'},
            {'email': 'legit@user.com', 'success': False, 'ip': '10.0.0.3', 'desc': 'Échec répété'},
            {'email': 'legit@user.com', 'success': True,  'ip': '10.0.0.4', 'desc': 'Changement IP rapide'},
        ]

        for b in behaviors:
            try:
                data = {
                    'email': b['email'],
                    'IP Address': b['ip'],
                    'Country': 'US',
                    'Browser Name and Version': 'Chrome',
                    'OS Name and Version': 'Windows 10',
                    'Device Type': 'desktop',
                    'Login Successful': b['success'],
                    'timestamp': datetime.now().isoformat()
                }

                response = requests.post(
                    f'{base_url}/api/security/analyze-login',
                    json=data,
                    timeout=5
                )

                if response.status_code == 429:
                    conf = response.json().get("detection_result", {}).get("confidence", 0)
                    print(f"🚨 Comportement anormal : {b['desc']} (Conf {conf:.2f})")
                else:
                    print(f"ℹ️ Comportement normal : {b['desc']}")

            except Exception as e:
                print(f"❌ Erreur comportement : {e}")

            time.sleep(0.2)

        print("✅ Test comportement terminé")


# ============================================================
#   FONCTION PRINCIPALE DE TEST (CONSOLE)
# ============================================================

def test_attack_detection():
    print("\n🔥 TEST COMPLET DES ATTAQUES")
    print("=" * 60)

    tests = [
        "bruteforce",
        "sql_injection",
        "suspicious_ips",
        "malicious_agents",
        "abnormal_behavior"
    ]

    for t in tests:
        run_specific_test_console(t)
        time.sleep(1)

    print("\n🎉 Tous les tests console sont terminés !")


# ============================================================
#                POINT D'ENTRÉE (MAIN)
# ============================================================

if __name__ == "__main__":
    print("🔍 Vérification du serveur...")

    try:
        response = requests.get("http://localhost:5000", timeout=5)

        if response.status_code == 200:
            print("✅ Serveur actif - Lancement des tests...")
            test_attack_detection()
        else:
            print("❌ Serveur non disponible.")

    except Exception as e:
        print(f"❌ Impossible de se connecter au serveur : {e}")
        print("💡 Lancez-le avec : python start_server.py")
