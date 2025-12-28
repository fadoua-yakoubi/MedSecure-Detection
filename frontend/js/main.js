// Gestion de l'onglet actif
document.addEventListener('DOMContentLoaded', function() {
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    
    if (loginTab && registerTab) {
        loginTab.addEventListener('click', function() {
            switchForm('login');
        });
    
        registerTab.addEventListener('click', function() {
            switchForm('register');
        });
    }
});

function switchForm(formType) {
    // Mise à jour des onglets
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    
    if (loginTab && registerTab) {
        loginTab.classList.toggle('active', formType === 'login');
        registerTab.classList.toggle('active', formType === 'register');
    }
    
    // Mise à jour des formulaires
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    if (loginForm && registerForm) {
        loginForm.classList.toggle('active', formType === 'login');
        registerForm.classList.toggle('active', formType === 'register');
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('MediConnect - Plateforme de télémédecine initialisée');
});