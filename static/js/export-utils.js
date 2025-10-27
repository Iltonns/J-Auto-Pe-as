/**
 * Utilitários para exportação de relatórios
 * Sistema de Autopeças - Família
 */

// Função para adicionar loading aos botões durante exportação
function addLoadingState(button) {
    if (button) {
        button.classList.add('btn-loading');
        button.disabled = true;
        const originalText = button.innerHTML;
        button.setAttribute('data-original-text', originalText);
        
        // Remover loading após 3 segundos (tempo estimado de processamento)
        setTimeout(() => {
            removeLoadingState(button);
        }, 3000);
    }
}

function removeLoadingState(button) {
    if (button) {
        button.classList.remove('btn-loading');
        button.disabled = false;
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
    }
}

// Função melhorada para exportar CSV com validação
function exportarCSVMelhorado(tableId, filename = 'relatorio.csv') {
    const table = document.getElementById(tableId);
    if (!table) {
        alert('Tabela não encontrada para exportação.');
        return;
    }

    let csv = [];
    
    try {
        // Cabeçalhos
        const headers = [];
        table.querySelectorAll('thead th').forEach(th => {
            headers.push(th.textContent.trim());
        });
        
        if (headers.length === 0) {
            alert('Nenhum cabeçalho encontrado na tabela.');
            return;
        }
        
        csv.push(headers.join(','));
        
        // Dados
        const rows = table.querySelectorAll('tbody tr');
        if (rows.length === 0) {
            alert('Nenhum dado encontrado na tabela para exportação.');
            return;
        }
        
        rows.forEach(tr => {
            const row = [];
            tr.querySelectorAll('td').forEach(td => {
                // Limpar o texto e escapar aspas
                let cellText = td.textContent.trim().replace(/\s+/g, ' ');
                row.push('"' + cellText.replace(/"/g, '""') + '"');
            });
            csv.push(row.join(','));
        });
        
        // Adicionar cabeçalho UTF-8 BOM para preservar caracteres especiais
        const csvContent = '\ufeff' + csv.join('\n');
        
        // Download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        
        // Adicionar ao DOM temporariamente para funcionar em todos os navegadores
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Feedback visual
        showExportFeedback('CSV exportado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao exportar CSV:', error);
        showExportFeedback('Erro ao exportar CSV. Tente novamente.', 'error');
    }
}

// Função para mostrar feedback de exportação
function showExportFeedback(message, type = 'success') {
    // Remover feedback anterior se existir
    const existingFeedback = document.querySelector('.export-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Criar elemento de feedback
    const feedback = document.createElement('div');
    feedback.className = `alert alert-${type === 'success' ? 'success' : 'danger'} export-feedback`;
    feedback.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInFromRight 0.3s ease;
    `;
    
    feedback.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
        ${message}
        <button type="button" class="btn-close" style="margin-left: 10px;" onclick="this.parentElement.remove()"></button>
    `;
    
    // Adicionar ao DOM
    document.body.appendChild(feedback);
    
    // Remover automaticamente após 5 segundos
    setTimeout(() => {
        if (feedback.parentElement) {
            feedback.remove();
        }
    }, 5000);
}

// Interceptar cliques em links de exportação PDF para adicionar loading
document.addEventListener('DOMContentLoaded', function() {
    const pdfLinks = document.querySelectorAll('a[href*="pdf"]');
    
    pdfLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            addLoadingState(this);
            showExportFeedback('Gerando PDF... Aguarde!', 'info');
        });
    });
});

// Função para validar filtros antes da exportação
function validarFiltrosExportacao() {
    const dataInicio = document.querySelector('input[name="data_inicio"]');
    const dataFim = document.querySelector('input[name="data_fim"]');
    
    if (dataInicio && dataFim) {
        const inicio = new Date(dataInicio.value);
        const fim = new Date(dataFim.value);
        
        if (dataInicio.value && dataFim.value && inicio > fim) {
            alert('A data de início deve ser anterior à data de fim.');
            return false;
        }
        
        // Verificar se o período não é muito longo (mais de 1 ano)
        if (dataInicio.value && dataFim.value) {
            const diffTime = Math.abs(fim - inicio);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays > 365) {
                const confirmar = confirm('O período selecionado é superior a 1 ano. Isso pode resultar em um arquivo muito grande. Deseja continuar?');
                if (!confirmar) {
                    return false;
                }
            }
        }
    }
    
    return true;
}

// Adicionar evento de validação aos botões de exportação
document.addEventListener('DOMContentLoaded', function() {
    const exportButtons = document.querySelectorAll('.export-buttons button, .export-buttons a');
    
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!validarFiltrosExportacao()) {
                e.preventDefault();
                return false;
            }
        });
    });
});