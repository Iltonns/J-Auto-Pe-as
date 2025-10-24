/**
 * Layout Toggle - Controle de Layout Compacto
 * Permite alternar entre layout normal e compacto
 */

// Função para alternar o layout
function toggleLayout() {
    const body = document.body;
    const isCompact = body.classList.contains('layout-compacto');
    
    if (isCompact) {
        // Desativar layout compacto
        body.classList.remove('layout-compacto');
        localStorage.setItem('layout-mode', 'normal');
        updateToggleButton(false);
    } else {
        // Ativar layout compacto
        body.classList.add('layout-compacto');
        localStorage.setItem('layout-mode', 'compact');
        updateToggleButton(true);
    }
}

// Atualizar texto do botão
function updateToggleButton(isCompact) {
    const button = document.getElementById('layout-toggle-btn');
    if (button) {
        if (isCompact) {
            button.innerHTML = '<i class="fas fa-expand"></i> Normal';
            button.title = 'Alternar para layout normal';
        } else {
            button.innerHTML = '<i class="fas fa-compress"></i> Compacto';
            button.title = 'Alternar para layout compacto';
        }
    }
}

// Carregar preferência salva
function loadLayoutPreference() {
    const savedMode = localStorage.getItem('layout-mode');
    // Por padrão, ativar o layout compacto se não houver preferência salva
    if (savedMode === 'normal') {
        document.body.classList.remove('layout-compacto');
        updateToggleButton(false);
    } else {
        // Ativar compacto por padrão
        document.body.classList.add('layout-compacto');
        updateToggleButton(true);
        if (!savedMode) {
            localStorage.setItem('layout-mode', 'compact');
        }
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    loadLayoutPreference();
    
    // Adicionar listener do botão se existir
    const toggleBtn = document.getElementById('layout-toggle-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleLayout);
    }
});

// Atalho de teclado Ctrl+Shift+L para alternar layout
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey && e.key === 'L') {
        e.preventDefault();
        toggleLayout();
    }
});