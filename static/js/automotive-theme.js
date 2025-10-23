// AutoPeças Pro - JavaScript Interativo

document.addEventListener('DOMContentLoaded', function() {
    
    // Animações de Entrada
    function initAnimations() {
        const cards = document.querySelectorAll('.card');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeInUp 0.6s ease-out';
                }
            });
        });
        
        cards.forEach(card => observer.observe(card));
    }

    // Efeito de Hover Avançado nos Cards
    function initCardEffects() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                this.style.transform = 'translateY(-8px) scale(1.02)';
                this.style.boxShadow = '0 20px 40px rgba(0,0,0,0.15)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)';
            });
        });
    }

    // Busca Inteligente
    function initSmartSearch() {
        const searchInput = document.getElementById('buscaProduto');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    const searchTerm = this.value.toLowerCase();
                    const rows = document.querySelectorAll('#tabelaProdutos tbody tr');
                    
                    rows.forEach(row => {
                        const text = row.textContent.toLowerCase();
                        if (text.includes(searchTerm)) {
                            row.style.display = '';
                            row.style.animation = 'fadeInUp 0.3s ease-out';
                        } else {
                            row.style.display = 'none';
                        }
                    });
                }, 300);
            });
        }
    }

    // Indicador de Loading
    function showLoading(element) {
        element.innerHTML = '<div class="automotive-spinner"></div>';
    }

    // Notificações Toast Personalizadas
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `automotive-toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? 'var(--gradient-primary)' : 'var(--gradient-accent)'};
            color: white;
            padding: 15px 20px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideInFromRight 0.3s ease-out;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideInFromRight 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Contador Animado para Dashboard
    function animateCounters() {
        const counters = document.querySelectorAll('.dashboard-card h3');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
            const increment = target / 30;
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = counter.textContent.replace(/^\d+/, target);
                    clearInterval(timer);
                } else {
                    counter.textContent = counter.textContent.replace(/^\d+/, Math.floor(current));
                }
            }, 50);
        });
    }

    // Status de Conexão
    function initConnectionStatus() {
        function updateConnectionStatus() {
            const isOnline = navigator.onLine;
            const statusElement = document.getElementById('connection-status');
            if (statusElement) {
                statusElement.innerHTML = isOnline 
                    ? '<i class="fas fa-wifi text-success"></i> Online'
                    : '<i class="fas fa-wifi text-danger"></i> Offline';
            }
        }
        
        window.addEventListener('online', updateConnectionStatus);
        window.addEventListener('offline', updateConnectionStatus);
        updateConnectionStatus();
    }

    // Tema Dark Mode Toggle
    function initThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                document.body.classList.toggle('dark-theme');
                const isDark = document.body.classList.contains('dark-theme');
                localStorage.setItem('darkTheme', isDark);
                
                this.innerHTML = isDark 
                    ? '<i class="fas fa-sun"></i>' 
                    : '<i class="fas fa-moon"></i>';
            });
            
            // Carregar preferência salva
            if (localStorage.getItem('darkTheme') === 'true') {
                document.body.classList.add('dark-theme');
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            }
        }
    }

    // Validação de Formulário Inteligente
    function initFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    validateField(this);
                });
                
                input.addEventListener('input', function() {
                    clearFieldError(this);
                });
            });
        });
    }

    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.getAttribute('name') || field.getAttribute('id');
        
        // Remover erro anterior
        clearFieldError(field);
        
        // Validações específicas
        if (field.hasAttribute('required') && !value) {
            showFieldError(field, 'Este campo é obrigatório');
            return false;
        }
        
        if (field.type === 'email' && value && !isValidEmail(value)) {
            showFieldError(field, 'Email inválido');
            return false;
        }
        
        if (field.type === 'tel' && value && !isValidPhone(value)) {
            showFieldError(field, 'Telefone inválido');
            return false;
        }
        
        return true;
    }

    function showFieldError(field, message) {
        field.classList.add('is-invalid');
        const errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        errorElement.textContent = message;
        field.parentNode.appendChild(errorElement);
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function isValidPhone(phone) {
        return /^[\d\s\-\(\)\+]+$/.test(phone);
    }

    // Inicializar todas as funcionalidades
    initAnimations();
    initCardEffects();
    initSmartSearch();
    initConnectionStatus();
    initThemeToggle();
    initFormValidation();
    
    // Animação de contadores no dashboard
    if (window.location.pathname.includes('dashboard')) {
        setTimeout(animateCounters, 500);
    }

    // Adicionar classe de carregamento completo
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 100);

    // Global toast function
    window.showToast = showToast;
});

// Função para formatação de moeda brasileira
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Função para formatação de data brasileira
function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
}

// Função para copiar texto
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Texto copiado para a área de transferência!');
    });
}

// Função para download de arquivo
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}