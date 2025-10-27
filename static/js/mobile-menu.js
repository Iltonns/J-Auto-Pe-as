/**
 * Mobile Menu Handler - Sistema AutoPeças
 * Gerencia o menu lateral em dispositivos móveis
 */

(function() {
    'use strict';
    
    // Elementos do DOM
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    
    // Verificar se os elementos existem
    if (!sidebarToggle || !sidebar || !sidebarOverlay) {
        console.warn('Elementos do menu mobile não encontrados');
        return;
    }
    
    /**
     * Abre o menu lateral
     */
    function openSidebar() {
        sidebar.classList.add('show');
        sidebarOverlay.classList.add('show');
        document.body.style.overflow = 'hidden'; // Prevenir scroll do body
    }
    
    /**
     * Fecha o menu lateral
     */
    function closeSidebar() {
        sidebar.classList.remove('show');
        sidebarOverlay.classList.remove('show');
        document.body.style.overflow = ''; // Restaurar scroll do body
    }
    
    /**
     * Alterna o menu lateral
     */
    function toggleSidebar() {
        if (sidebar.classList.contains('show')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }
    
    // Event Listeners
    sidebarToggle.addEventListener('click', toggleSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);
    
    // Fechar menu ao clicar em um link (apenas em mobile)
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    });
    
    // Fechar menu ao pressionar ESC
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && sidebar.classList.contains('show')) {
            closeSidebar();
        }
    });
    
    // Fechar menu ao redimensionar para desktop
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 768 && sidebar.classList.contains('show')) {
                closeSidebar();
            }
        }, 250);
    });
    
    // Touch swipe para fechar menu
    let touchStartX = 0;
    let touchEndX = 0;
    
    sidebar.addEventListener('touchstart', function(event) {
        touchStartX = event.changedTouches[0].screenX;
    }, false);
    
    sidebar.addEventListener('touchend', function(event) {
        touchEndX = event.changedTouches[0].screenX;
        handleSwipe();
    }, false);
    
    function handleSwipe() {
        // Swipe para a esquerda fecha o menu
        if (touchStartX - touchEndX > 50) {
            closeSidebar();
        }
    }
    
    console.log('Mobile menu handler inicializado');
    
})();
