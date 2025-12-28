from web3 import Web3
import json
import logging
import os

class BlockchainLogger:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
        self.contract_address = None
        self.contract = None
        self.account = None
        
    def setup_contract(self, contract_address, abi_path):
        """Configurer le contrat déployé"""
        try:
            # Charger l'ABI depuis le fichier de build Truffle
            with open(abi_path, 'r') as f:
                abi_data = json.load(f)
                abi = abi_data['abi']
            
            self.contract_address = contract_address
            self.contract = self.w3.eth.contract(
                address=contract_address,
                abi=abi
            )
            
            # Utiliser le premier compte Ganache
            self.account = self.w3.eth.accounts[0]
            logging.info(f"Contrat Blockchain configuré: {contract_address}")
            logging.info(f"Compte utilisé: {self.account}")
            return True
            
        except Exception as e:
            logging.error(f"Erreur configuration blockchain: {e}")
            return False
    
    def log_attack_to_blockchain(self, attack_data):
        """Logger une attaque sur la blockchain"""
        if not self.contract:
            logging.warning("Contrat blockchain non configuré")
            return False
            
        try:
            # Convertir les floats en integers (solidity ne supporte pas les floats)
            confidence_scaled = int(attack_data['confidence'] * 10000)
            bert_prob_scaled = int(attack_data['bert_probability'] * 10000)
            
            # Préparer la transaction
            transaction = self.contract.functions.logAttack(
                attack_data['timestamp'],
                attack_data['email'],
                str(attack_data['user_id'] or ""),
                attack_data['ip_address'],
                attack_data['country'],
                attack_data['attack_type'],
                confidence_scaled,
                bert_prob_scaled,
                attack_data['bert_used'],
                attack_data['login_successful']
            ).build_transaction({
                'from': self.account,
                'gas': 2000000,
                'gasPrice': self.w3.to_wei('50', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account)
            })
            
            # ⚠️ CORRECTION: Utiliser raw_transaction au lieu de rawTransaction
            private_key = "0x21bbca70eed8f21b371ce6e3369d855e790986f10410cc141bb2ebf6dcffff60"
            
            # Signer et envoyer - CORRIGÉ
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)  # ← raw_transaction au lieu de rawTransaction
            
            # Attendre la confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logging.info(f"Attaque loggée sur blockchain: {tx_hash.hex()}")
            logging.info(f"Block: {receipt.blockNumber}, Gas utilisé: {receipt.gasUsed}")
            
            return tx_hash.hex()
            
        except Exception as e:
            logging.error(f"Erreur blockchain: {e}")
            return False

    def get_blockchain_stats(self):
        """Récupérer les statistiques de la blockchain"""
        try:
            if not self.contract:
                return None
            
            attack_count = self.contract.functions.getAttackCount().call()
            
            return {
                'total_attacks_logged': attack_count,
                'contract_address': self.contract_address,
                'account': self.account,
                'is_connected': self.w3.is_connected(),
                'latest_block': self.w3.eth.block_number
            }
            
        except Exception as e:
            logging.error(f"Erreur récupération stats blockchain: {e}")
            return None

# Instance globale
blockchain_logger = BlockchainLogger()