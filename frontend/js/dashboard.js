// Configuration
const API_BASE = 'http://localhost:5000/api';

// ============================================
// SECURITY TESTER CLASS - Version simplifiée
// ============================================
class SecurityTester {
    constructor() {
        this.baseUrl = 'http://localhost:5000';
        this.isTesting = false;
        this.currentTest = null;
        this.statsUpdateInterval = null;
    }

    async runTest(testType) {
        if (this.isTesting) {
            showNotification('Un test est déjà en cours', 'warning');
            return;
        }

        this.isTesting = true;
        this.currentTest = testType;
        
        this.clearResults();
        this.showProgress(true);
        this.updateProgress(0, 'Initialisation...');

        try {
            const response = await fetch(`${API_BASE}/security/run-test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ test_type: testType }),
                credentials: 'include'
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`Erreur serveur ${response.status}: ${errorData.error || response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.processTestResults(data);
                showNotification(`Test ${testType} terminé avec succès`, 'success');
            } else {
                throw new Error(data.error || 'Erreur inconnue');
            }

        } catch (error) {
            console.error('Erreur complète:', error);
            this.addLogEntry(`❌ Erreur: ${error.message}`, 'error');
            this.addLogEntry('⚠️ Vérifiez que le serveur backend est en cours d\'exécution', 'warning');
            showNotification('Erreur lors du test', 'error');
        } finally {
            this.isTesting = false;
            this.showProgress(false);
            // Mettre à jour les stats immédiatement après le test
            this.updateStats();
        }
    }

    processTestResults(data) {
        if (data.results && Array.isArray(data.results)) {
            const totalSteps = data.results.length;
            
            data.results.forEach((result, index) => {
                setTimeout(() => {
                    this.addLogEntry(result.message, result.type || 'info');
                    const progress = ((index + 1) / totalSteps) * 100;
                    this.updateProgress(progress, `Traitement... (${index + 1}/${totalSteps})`);
                }, index * 100);
            });
            
            // Dernière mise à jour à 100%
            setTimeout(() => {
                this.updateProgress(100, 'Test terminé !');
            }, (data.results.length + 1) * 100);
        }
        
        if (data.summary) {
            setTimeout(() => {
                this.addLogEntry(`📊 ${data.summary}`, 'success');
            }, (data.results?.length || 0) * 100 + 200);
        }
    }

    addLogEntry(message, type = 'info') {
        const resultsContainer = document.getElementById('security-results');
        
        // Supprimer le placeholder s'il existe
        const placeholder = resultsContainer.querySelector('.log-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.innerHTML = message;
        
        resultsContainer.appendChild(logEntry);
        resultsContainer.scrollTop = resultsContainer.scrollHeight;
    }

    clearResults() {
        document.getElementById('security-results').innerHTML = `
            <div class="log-placeholder">
                <i class="fas fa-terminal"></i>
                <p>Les résultats des tests s'afficheront ici en temps réel</p>
            </div>
        `;
    }

    showProgress(show) {
        const progress = document.getElementById('test-progress');
        if (progress) {
            if (show) {
                progress.classList.remove('hidden');
            } else {
                progress.classList.add('hidden');
            }
        }
    }

    updateProgress(percent, text) {
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const progressPercent = document.getElementById('progress-percent');
        
        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }
        if (progressText) progressText.textContent = text;
        if (progressPercent) progressPercent.textContent = `${Math.round(percent)}%`;
    }

    async updateStats() {
        try {
            const response = await fetch(`${API_BASE}/security/stats`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success && data.statistics) {
                    updateSecurityUI(data.statistics);
                }
            } else {
                console.error('Erreur réponse stats:', response.status);
            }
        } catch (error) {
            console.error('Erreur mise à jour stats:', error);
        }
    }

    startAutoUpdate(intervalSeconds = 5) {
        // Arrêter l'intervalle précédent si existant
        if (this.statsUpdateInterval) {
            clearInterval(this.statsUpdateInterval);
        }
        
        // Démarrer un nouvel intervalle
        this.statsUpdateInterval = setInterval(() => {
            this.updateStats();
        }, intervalSeconds * 1000);
    }

    stopAutoUpdate() {
        if (this.statsUpdateInterval) {
            clearInterval(this.statsUpdateInterval);
            this.statsUpdateInterval = null;
        }
    }
}

// Initialiser le Security Tester globalement
const securityTester = new SecurityTester();

// ============================================
// MISE À JOUR DES STATS
// ============================================
function updateSecurityUI(stats) {
    const totalAttacksEl = document.getElementById('total-attacks');
    const detectedAttacksEl = document.getElementById('detected-attacks');
    const detectionRateEl = document.getElementById('detection-rate');
    const bertStatusEl = document.getElementById('bert-status');
    
    // Total des requêtes/test d'attaques
    if (totalAttacksEl) {
        const total = stats.total_requests || stats.total_tests || stats.total_attempts || 0;
        totalAttacksEl.textContent = total.toLocaleString();
    }
    
    // Attaques détectées
    if (detectedAttacksEl) {
        const detected = stats.detected_attacks || stats.attacks_detected || 0;
        detectedAttacksEl.textContent = detected.toLocaleString();
    }
    
    // Taux de détection
    if (detectionRateEl) {
        const total = stats.total_requests || stats.total_tests || 1;
        const detected = stats.detected_attacks || stats.attacks_detected || 0;
        const detectionRate = total > 0 ? (detected / total) * 100 : 0;
        detectionRateEl.textContent = `${detectionRate.toFixed(1)}%`;
    }
    
    // Statut BERT
    if (bertStatusEl) {
        const isActive = stats.bert_available || stats.bert_active || false;
        bertStatusEl.textContent = isActive ? '🟢 Actif' : '🔴 Inactif';
        bertStatusEl.className = isActive ? 'status-active' : 'status-inactive';
    }
}

// ============================================
// SECURITY PAGE INITIALIZATION
// ============================================
function initializeSecurityPage() {
    console.log('🔧 Initialisation de la page sécurité...');
    
    // Test buttons event listeners
    document.querySelectorAll('.test-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const testType = this.dataset.test;
            console.log(`🚀 Lancement du test: ${testType}`);
            securityTester.runTest(testType);
        });
    });

    // Clear results button
    const clearBtn = document.getElementById('clear-results');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            securityTester.clearResults();
            showNotification('Résultats effacés', 'info');
        });
    }

    // Export results button
    const exportBtn = document.getElementById('export-results');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            exportTestResults();
        });
    }

    // Charger les stats immédiatement
    securityTester.updateStats();
    
    // Démarrer la mise à jour automatique
    securityTester.startAutoUpdate(5); // Toutes les 5 secondes
    
    console.log('✅ Page sécurité initialisée');
}

// Export function
function exportTestResults() {
    const results = document.getElementById('security-results');
    let textContent = `=== Rapport de Sécurité BERT ===\n`;
    textContent += `Date: ${new Date().toLocaleString('fr-FR')}\n`;
    textContent += `Généré par: ${document.getElementById('user-name')?.textContent || 'Utilisateur'}\n`;
    textContent += `\n=== Résultats des Tests ===\n\n`;
    
    const logEntries = results.querySelectorAll('.log-entry');
    logEntries.forEach(entry => {
        textContent += entry.textContent + '\n';
    });
    
    if (!textContent.trim() || logEntries.length === 0) {
        showNotification('Aucun résultat à exporter', 'warning');
        return;
    }
    
    const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `security-report-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Rapport exporté avec succès', 'success');
}

// ============================================
// DASHBOARD INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation du dashboard...');
    
    // Vérifier la session et charger les données utilisateur
    checkSessionAndLoadDashboard();
    
    // Bouton de déconnexion
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Initialiser la navigation
    initializeNavigation();
    
    console.log('✅ Dashboard initialisé');
});

async function checkSessionAndLoadDashboard() {
    try {
        const sessionCheck = await fetch(`${API_BASE}/session/check`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const sessionData = await sessionCheck.json();
        
        if (sessionData.authenticated) {
            loadUserData(sessionData.user);
            showNotification('Bienvenue ' + sessionData.user.nom_complet, 'success');
            loadDashboardData();
        } else {
            showNotification('Veuillez vous connecter', 'warning');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        }
        
    } catch (error) {
        console.error('Erreur vérification session:', error);
        showNotification('Erreur de connexion au serveur', 'error');
        loadMockUser();
    }
}

function loadUserData(user) {
    const userNameEl = document.getElementById('user-name');
    if (userNameEl) {
        userNameEl.textContent = user.nom_complet;
    }
    
    const userEmailEl = document.getElementById('user-email');
    if (userEmailEl) {
        userEmailEl.textContent = user.email;
    }
    
    const userRoleEl = document.getElementById('user-role');
    if (userRoleEl) {
        userRoleEl.textContent = user.role === 'medecin' ? 'Médecin' : 'Patient';
        userRoleEl.className = user.role === 'medecin' ? 'role-medecin' : 'role-patient';
    }
    
    const profileElements = {
        'profile-name': user.nom_complet,
        'profile-email': user.email,
        'profile-phone': user.telephone || 'Non renseigné',
        'profile-role': user.role === 'medecin' ? 'Médecin' : 'Patient'
    };
    
    Object.entries(profileElements).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = value;
        }
    });
    
    adjustUIForRole(user.role);
}

function adjustUIForRole(role) {
    if (role === 'patient') {
        document.querySelectorAll('.medecin-only').forEach(el => {
            el.style.display = 'none';
        });
    } else if (role === 'medecin') {
        document.querySelectorAll('.patient-only').forEach(el => {
            el.style.display = 'none';
        });
    }
}

function loadMockUser() {
    const mockUser = {
        nom_complet: 'Utilisateur Démo',
        email: 'demo@mediconnect.fr',
        telephone: '+33123456789',
        role: 'patient'
    };
    
    loadUserData(mockUser);
}

async function loadDashboardData() {
    try {
        await updateSecurityStats();
        loadConsultationStats();
        loadRecentConsultations();
    } catch (error) {
        console.error('Erreur chargement dashboard:', error);
        loadMockDashboardData();
    }
}

async function updateSecurityStats() {
    try {
        await securityTester.updateStats();
    } catch (error) {
        console.error('Erreur stats sécurité:', error);
    }
}

function loadConsultationStats() {
    const totalConsultationsEl = document.getElementById('total-consultations');
    const consultationsTermineesEl = document.getElementById('consultations-terminees');
    const consultationsPlanifieesEl = document.getElementById('consultations-planifiees');
    
    if (totalConsultationsEl) totalConsultationsEl.textContent = '8';
    if (consultationsTermineesEl) consultationsTermineesEl.textContent = '5';
    if (consultationsPlanifieesEl) consultationsPlanifieesEl.textContent = '3';
}

function loadRecentConsultations() {
    const container = document.getElementById('recent-consultations');
    if (!container) return;
    
    const mockConsultations = [
        {
            date: '2024-01-15 10:30',
            medecin_nom: 'Dr. Sophie Martin',
            statut: 'terminée',
            duree: 30
        },
        {
            date: '2024-01-10 14:00',
            medecin_nom: 'Dr. Jean Dupont',
            statut: 'planifiée',
            duree: 45
        },
        {
            date: '2024-01-05 09:15',
            medecin_nom: 'Dr. Marie Curie',
            statut: 'terminée',
            duree: 25
        }
    ];
    
    container.innerHTML = mockConsultations.map(consultation => `
        <div class="consultation-item">
            <div class="consultation-header">
                <span class="consultation-date">
                    ${new Date(consultation.date).toLocaleDateString('fr-FR', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    })}
                </span>
                <span class="consultation-status status-${consultation.statut}">
                    ${consultation.statut}
                </span>
            </div>
            <div class="consultation-details">
                Médecin: ${consultation.medecin_nom} • Durée: ${consultation.duree} min
            </div>
        </div>
    `).join('');
}

function loadMockDashboardData() {
    loadConsultationStats();
    loadRecentConsultations();
}

async function handleLogout() {
    try {
        const response = await fetch(`${API_BASE}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            // Arrêter la mise à jour automatique avant la déconnexion
            securityTester.stopAutoUpdate();
            window.location.href = 'index.html';
        }
    } catch (error) {
        console.error('Erreur déconnexion:', error);
        window.location.href = 'index.html';
    }
}

// ============================================
// NAVIGATION
// ============================================
function initializeNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.getAttribute('data-page');
            switchPage(page);
        });
    });
}

function switchPage(page) {
    console.log(`📄 Changement de page: ${page}`);
    
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeNavItem = document.querySelector(`[data-page="${page}"]`);
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }

    const titles = {
        'dashboard': 'Tableau de Bord',
        'consultations': 'Mes Consultations',
        'medecins': 'Médecins',
        'profil': 'Mon Profil',
        'parametres': 'Paramètres',
        'security': 'Sécurité BERT'
    };
    const pageTitleEl = document.getElementById('page-title');
    if (pageTitleEl) {
        pageTitleEl.textContent = titles[page] || page;
    }

    document.querySelectorAll('.page').forEach(pageEl => {
        pageEl.classList.remove('active');
    });
    const targetPage = document.getElementById(`${page}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }

    if (page === 'security') {
        console.log('🔒 Initialisation de la page sécurité');
        setTimeout(() => {
            initializeSecurityPage();
        }, 100);
    } else if (page === 'dashboard') {
        setTimeout(() => {
            updateSecurityStats();
        }, 100);
    }
}

// ============================================
// NOTIFICATION SYSTEM
// ============================================
function showNotification(message, type = 'info') {
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        document.body.appendChild(notification);
    }
    
    const colors = {
        success: '#34c759',
        error: '#ff3b30',
        info: '#2a7de1',
        warning: '#ff9500'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    notification.style.transform = 'translateX(0)';
    
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 3000);
}

// Exporter pour une utilisation globale
window.dashboard = {
    showNotification,
    loadDashboardData,
    handleLogout,
    securityTester,
    updateSecurityStats
};

console.log('✅ Script dashboard.js chargé');