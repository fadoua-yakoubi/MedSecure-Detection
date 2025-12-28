// Gestion de l'authentification
const API_BASE = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const forgotPasswordLink = document.getElementById('forgot-password');
    
    // Soumission du formulaire de connexion
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Soumission du formulaire d'inscription
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Lien "Mot de passe oublié"
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', handleForgotPassword);
    }
});

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    // Validation basique
    if (!validateEmail(email)) {
        showNotification('Veuillez entrer une adresse email valide', 'error');
        return;
    }
    
    if (password.length < 6) {
        showNotification('Le mot de passe doit contenir au moins 6 caractères', 'error');
        return;
    }
    
    // Afficher le loading
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connexion...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Connexion réussie! Redirection...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showNotification(data.message || 'Erreur lors de la connexion', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion au serveur', 'error');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const phone = document.getElementById('register-phone').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    const acceptTerms = document.getElementById('accept-terms').checked;
    
    // Validation
    if (!validateName(name)) {
        showNotification('Veuillez entrer un nom complet valide', 'error');
        return;
    }
    
    if (!validateEmail(email)) {
        showNotification('Veuillez entrer une adresse email valide', 'error');
        return;
    }
    
    if (phone && !validatePhone(phone)) {
        showNotification('Veuillez entrer un numéro de téléphone valide', 'error');
        return;
    }
    
    if (password.length < 8) {
        showNotification('Le mot de passe doit contenir au moins 8 caractères', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showNotification('Les mots de passe ne correspondent pas', 'error');
        return;
    }
    
    if (!acceptTerms) {
        showNotification('Veuillez accepter les conditions d\'utilisation', 'error');
        return;
    }
    
    // Afficher le loading
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Création du compte...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                nom_complet: name, 
                email, 
                telephone: phone, 
                password 
            }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Compte créé avec succès! Redirection...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showNotification(data.message || 'Erreur lors de la création du compte', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion au serveur', 'error');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

function handleForgotPassword(e) {
    e.preventDefault();
    
    const email = prompt('Veuillez entrer votre adresse email pour réinitialiser votre mot de passe:');
    
    if (email && validateEmail(email)) {
        showNotification('Instructions de réinitialisation envoyées à ' + email, 'info');
    } else if (email) {
        showNotification('Adresse email invalide', 'error');
    }
}

// Fonction utilitaire pour afficher les notifications
function showNotification(message, type = 'info') {
    // Créer la notification si elle n'existe pas
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
    
    // Couleurs selon le type
    const colors = {
        success: '#34c759',
        error: '#ff3b30',
        info: '#2a7de1'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    notification.style.transform = 'translateX(0)';
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
    }, 5000);
}