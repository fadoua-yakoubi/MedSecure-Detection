// Fonctions de validation
document.addEventListener('DOMContentLoaded', function() {
    initializeFormValidation();
});

function initializeFormValidation() {
    // Validation en temps réel pour le formulaire de connexion
    const loginEmail = document.getElementById('login-email');
    const loginPassword = document.getElementById('login-password');
    
    if (loginEmail) {
        loginEmail.addEventListener('blur', function() {
            validateField(this, validateEmail);
        });
    }
    
    if (loginPassword) {
        loginPassword.addEventListener('blur', function() {
            validateField(this, validatePassword);
        });
    }
    
    // Validation en temps réel pour le formulaire d'inscription
    const registerName = document.getElementById('register-name');
    const registerEmail = document.getElementById('register-email');
    const registerPhone = document.getElementById('register-phone');
    const registerPassword = document.getElementById('register-password');
    const registerConfirmPassword = document.getElementById('register-confirm-password');
    
    if (registerName) {
        registerName.addEventListener('blur', function() {
            validateField(this, validateName);
        });
    }
    
    if (registerEmail) {
        registerEmail.addEventListener('blur', function() {
            validateField(this, validateEmail);
        });
    }
    
    if (registerPhone) {
        registerPhone.addEventListener('blur', function() {
            validateField(this, validatePhone);
        });
    }
    
    if (registerPassword) {
        registerPassword.addEventListener('blur', function() {
            validateField(this, validatePassword);
        });
    }
    
    if (registerConfirmPassword) {
        registerConfirmPassword.addEventListener('blur', function() {
            validateConfirmPassword();
        });
    }
}

function validateField(field, validationFunction) {
    const value = field.value.trim();
    const isValid = validationFunction(value);
    
    if (value === '') {
        removeValidationStyles(field);
        return;
    }
    
    if (isValid) {
        setFieldValid(field);
    } else {
        setFieldInvalid(field);
    }
}

function validateConfirmPassword() {
    const password = document.getElementById('register-password');
    const confirmPassword = document.getElementById('register-confirm-password');
    
    if (!password || !confirmPassword) return;
    
    const passwordValue = password.value;
    const confirmValue = confirmPassword.value;
    
    if (confirmValue === '') {
        removeValidationStyles(confirmPassword);
        return;
    }
    
    if (passwordValue === confirmValue && passwordValue.length >= 8) {
        setFieldValid(confirmPassword);
    } else {
        setFieldInvalid(confirmPassword);
    }
}

function setFieldValid(field) {
    field.style.borderColor = '#34c759';
    field.style.boxShadow = '0 0 0 3px rgba(52, 199, 89, 0.2)';
    clearFieldError(field);
}

function setFieldInvalid(field) {
    field.style.borderColor = '#ff3b30';
    field.style.boxShadow = '0 0 0 3px rgba(255, 59, 48, 0.2)';
    showFieldError(field, getErrorMessage(field));
}

function removeValidationStyles(field) {
    field.style.borderColor = '';
    field.style.boxShadow = '';
    clearFieldError(field);
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.textContent = message;
    errorElement.style.cssText = `
        color: #ff3b30;
        font-size: 0.85rem;
        margin-top: 5px;
    `;
    
    field.parentNode.appendChild(errorElement);
}

function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function getErrorMessage(field) {
    const fieldType = field.type || field.id;
    
    switch (fieldType) {
        case 'email':
        case 'login-email':
        case 'register-email':
            return 'Veuillez entrer une adresse email valide';
        
        case 'password':
        case 'login-password':
            return 'Le mot de passe doit contenir au moins 6 caractères';
        
        case 'register-password':
            return 'Le mot de passe doit contenir au moins 8 caractères';
        
        case 'register-confirm-password':
            return 'Les mots de passe ne correspondent pas';
        
        case 'text':
            if (field.id === 'register-name') {
                return 'Veuillez entrer un nom complet valide';
            }
            break;
        
        case 'tel':
        case 'register-phone':
            return 'Veuillez entrer un numéro de téléphone valide';
        
        default:
            return 'Ce champ contient une erreur';
    }
}

// Fonctions de validation spécifiques
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function validateRegisterPassword(password) {
    return password.length >= 8;
}

function validateName(name) {
    return name.length >= 2 && name.includes(' ');
}

function validatePhone(phone) {
    return phone;
}

// Export pour utilisation dans d'autres fichiers
window.FormValidation = {
    validateEmail,
    validatePassword,
    validateRegisterPassword,
    validateName,
    validatePhone
};