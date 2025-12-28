// home.js - Fonctionnalités spécifiques à la page d'accueil

document.addEventListener('DOMContentLoaded', function() {
    initializeHomePage();
});

function initializeHomePage() {
    initializeNavigation();
    initializeFeatureTabs();
    initializeAnimations();
    initializeSmoothScrolling();
}

// Navigation
function initializeNavigation() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mainNav = document.querySelector('.main-nav');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Menu mobile
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            mainNav.classList.toggle('active');
            this.innerHTML = mainNav.classList.contains('active') ? 
                '<i class="fas fa-times"></i>' : 
                '<i class="fas fa-bars"></i>';
        });
    }
    
    // Navigation active state
    window.addEventListener('scroll', function() {
        const scrollPosition = window.scrollY;
        
        // Update active nav link based on scroll position
        document.querySelectorAll('section').forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.clientHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
        
        // Header background on scroll
        const header = document.querySelector('.main-header');
        if (scrollPosition > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.95)';
            header.style.backdropFilter = 'blur(10px)';
        } else {
            header.style.background = 'var(--white)';
            header.style.backdropFilter = 'none';
        }
    });
}

// Feature Tabs
function initializeFeatureTabs() {
    const featureTabs = document.querySelectorAll('.feature-tab');
    const featurePanels = document.querySelectorAll('.feature-panel');
    
    featureTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Update active tab
            featureTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding panel
            featurePanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === `${targetTab}-panel`) {
                    panel.classList.add('active');
                }
            });
        });
    });
}

// Animations
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.service-card, .feature-item, .stat').forEach(el => {
        observer.observe(el);
    });
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        .service-card,
        .feature-item,
        .stat {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }
        
        .service-card.animate-in,
        .feature-item.animate-in,
        .stat.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        .service-card:nth-child(odd) { transition-delay: 0.1s; }
        .service-card:nth-child(even) { transition-delay: 0.2s; }
        .feature-item:nth-child(odd) { transition-delay: 0.1s; }
        .feature-item:nth-child(even) { transition-delay: 0.2s; }
    `;
    document.head.appendChild(style);
}

// Smooth Scrolling
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const headerHeight = document.querySelector('.main-header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                const mobileMenu = document.querySelector('.main-nav');
                const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
                if (mobileMenu && mobileMenu.classList.contains('active')) {
                    mobileMenu.classList.remove('active');
                    mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
                }
            }
        });
    });
}

// Statistics Counter Animation
function animateStatistics() {
    const stats = document.querySelectorAll('.stat-number');
    const duration = 2000; // 2 seconds
    
    stats.forEach(stat => {
        const target = parseInt(stat.textContent);
        const increment = target / (duration / 16); // 60fps
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            stat.textContent = Math.floor(current) + (stat.textContent.includes('+') ? '+' : '');
        }, 16);
    });
}

// Initialize statistics animation when in view
const statsObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateStatistics();
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

// Observe hero section for stats animation
const heroSection = document.querySelector('.hero');
if (heroSection) {
    statsObserver.observe(heroSection);
}

// Export functions for global access
window.HomePage = {
    initializeHomePage,
    initializeNavigation,
    initializeFeatureTabs,
    initializeAnimations,
    initializeSmoothScrolling,
    animateStatistics
};