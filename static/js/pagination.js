/**
 * Sistema de Paginação Reutilizável
 * Para uso em tabelas do Sistema de Autopeças
 */

class TablePagination {
    constructor(options = {}) {
        this.tableId = options.tableId || 'tabelaPrincipal';
        this.itemsPerPageId = options.itemsPerPageId || 'itensPorPagina';
        this.searchId = options.searchId || 'buscaPrincipal';
        this.visibleCountId = options.visibleCountId || 'itensVisiveis';
        this.totalCountId = options.totalCountId || 'totalItens';
        this.prevBtnId = options.prevBtnId || 'btnAnterior';
        this.nextBtnId = options.nextBtnId || 'btnProximo';
        this.paginationControlsId = options.paginationControlsId || 'controlesNavegacao';
        this.pageInfoId = options.pageInfoId || 'infoPaginacao';
        
        // Configurações
        this.currentPage = 1;
        this.itemsPerPage = parseInt(options.defaultItemsPerPage) || 20;
        this.allRows = [];
        this.filteredRows = [];
        
        // Campos de busca personalizáveis
        this.searchFields = options.searchFields || ['nome', 'codigo', 'categoria'];
        
        this.init();
    }
    
    init() {
        this.setupElements();
        this.bindEvents();
        this.loadAllRows();
        this.updatePagination();
    }
    
    setupElements() {
        this.$table = $(`#${this.tableId}`);
        this.$tbody = this.$table.find('tbody');
        this.$itemsPerPage = $(`#${this.itemsPerPageId}`);
        this.$search = $(`#${this.searchId}`);
        this.$visibleCount = $(`#${this.visibleCountId}`);
        this.$totalCount = $(`#${this.totalCountId}`);
        this.$prevBtn = $(`#${this.prevBtnId}`);
        this.$nextBtn = $(`#${this.nextBtnId}`);
        this.$paginationControls = $(`#${this.paginationControlsId}`);
        this.$pageInfo = $(`#${this.pageInfoId}`);
    }
    
    bindEvents() {
        // Mudança na quantidade de itens por página
        this.$itemsPerPage.on('change', () => {
            const value = this.$itemsPerPage.val();
            this.itemsPerPage = value === 'all' ? this.filteredRows.length : parseInt(value);
            this.currentPage = 1;
            this.updatePagination();
        });
        
        // Busca em tempo real
        this.$search.on('input', () => {
            this.performSearch();
        });
        
        // Navegação
        this.$prevBtn.on('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.updatePagination();
            }
        });
        
        this.$nextBtn.on('click', () => {
            const totalPages = Math.ceil(this.filteredRows.length / this.itemsPerPage);
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.updatePagination();
            }
        });
        
        // Teclas de navegação
        $(document).on('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            const totalPages = Math.ceil(this.filteredRows.length / this.itemsPerPage);
            
            if (e.key === 'ArrowLeft' && this.currentPage > 1) {
                this.currentPage--;
                this.updatePagination();
                e.preventDefault();
            } else if (e.key === 'ArrowRight' && this.currentPage < totalPages) {
                this.currentPage++;
                this.updatePagination();
                e.preventDefault();
            }
        });
    }
    
    loadAllRows() {
        this.allRows = this.$tbody.find('tr').toArray();
        this.filteredRows = [...this.allRows];
    }
    
    performSearch() {
        const searchTerm = this.$search.val().toLowerCase().trim();
        
        if (!searchTerm) {
            this.filteredRows = [...this.allRows];
        } else {
            this.filteredRows = this.allRows.filter(row => {
                const $row = $(row);
                const text = $row.text().toLowerCase();
                return text.includes(searchTerm);
            });
        }
        
        this.currentPage = 1;
        this.updatePagination();
    }
    
    updatePagination() {
        const totalItems = this.filteredRows.length;
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        
        // Ocultar todas as linhas
        this.$tbody.find('tr').hide();
        
        // Calcular índices da página atual
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        
        // Mostrar apenas as linhas da página atual
        const rowsToShow = this.filteredRows.slice(startIndex, endIndex);
        $(rowsToShow).show();
        
        // Atualizar contadores
        const visibleItems = rowsToShow.length;
        this.$visibleCount.text(visibleItems);
        this.$totalCount.text(totalItems);
        
        // Atualizar botões de navegação
        this.$prevBtn.prop('disabled', this.currentPage <= 1);
        this.$nextBtn.prop('disabled', this.currentPage >= totalPages);
        
        // Mostrar/ocultar controles de navegação
        if (totalPages <= 1) {
            this.$paginationControls.hide();
        } else {
            this.$paginationControls.show();
        }
        
        // Atualizar texto dos botões
        this.$prevBtn.html(`<i class="fas fa-chevron-left"></i> Anterior${this.currentPage > 1 ? ` (${this.currentPage - 1})` : ''}`);
        this.$nextBtn.html(`Próximo${this.currentPage < totalPages ? ` (${this.currentPage + 1})` : ''} <i class="fas fa-chevron-right"></i>`);
        
        // Atualizar informações da página
        if (this.$pageInfo.length) {
            if (totalPages > 1) {
                this.$pageInfo.html(`
                    <small class="text-muted">
                        Página ${this.currentPage} de ${totalPages}
                        ${totalPages > 5 ? `<br><span class="badge bg-info">Use ← → para navegar</span>` : ''}
                    </small>
                `);
                this.$pageInfo.show();
            } else {
                this.$pageInfo.hide();
            }
        }
        
        // Mostrar mensagem se não houver resultados
        this.showNoResultsMessage(totalItems === 0);
    }
    
    showNoResultsMessage(show) {
        let $noResults = this.$tbody.find('.no-results-row');
        
        if (show) {
            if ($noResults.length === 0) {
                const colCount = this.$table.find('thead th').length;
                $noResults = $(`
                    <tr class="no-results-row">
                        <td colspan="${colCount}" class="text-center py-5">
                            <i class="fas fa-search fa-2x text-muted mb-3"></i>
                            <h5 class="text-muted">Nenhum resultado encontrado</h5>
                            <p class="text-muted">Tente ajustar os termos de busca.</p>
                        </td>
                    </tr>
                `);
                this.$tbody.append($noResults);
            }
            $noResults.show();
        } else {
            $noResults.hide();
        }
    }
    
    // Método público para recarregar dados
    reload() {
        this.loadAllRows();
        this.currentPage = 1;
        this.updatePagination();
    }
    
    // Método público para ir para uma página específica
    goToPage(page) {
        const totalPages = Math.ceil(this.filteredRows.length / this.itemsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.updatePagination();
        }
    }
    
    // Método público para definir itens por página
    setItemsPerPage(items) {
        this.itemsPerPage = items === 'all' ? this.filteredRows.length : parseInt(items);
        this.currentPage = 1;
        this.$itemsPerPage.val(items);
        this.updatePagination();
    }
}

// Função auxiliar para criar controles de paginação
function createPaginationControls(containerId, options = {}) {
    const defaultOptions = {
        showSearch: true,
        showItemsPerPage: true,
        searchPlaceholder: 'Buscar...',
        ...options
    };
    
    let html = `<div class="row mb-3 align-items-center">`;
    
    // Lado esquerdo - Controles de itens por página
    if (defaultOptions.showItemsPerPage) {
        html += `
            <div class="col-md-6">
                <div class="d-flex align-items-center">
                    <label for="${options.itemsPerPageId || 'itensPorPagina'}" class="form-label me-2 mb-0">Mostrar:</label>
                    <select class="form-select w-auto" id="${options.itemsPerPageId || 'itensPorPagina'}" style="min-width: 80px;">
                        <option value="10">10</option>
                        <option value="20" selected>20</option>
                        <option value="50">50</option>
                        <option value="100">100</option>
                        <option value="all">Todos</option>
                    </select>
                    <span class="ms-2 text-muted">itens por página</span>
                </div>
            </div>
        `;
    }
    
    // Lado direito - Contador e navegação
    html += `
        <div class="col-md-${defaultOptions.showItemsPerPage ? '6' : '12'} text-end">
            <div class="d-flex align-items-center justify-content-end">
                <span class="badge bg-primary me-2">
                    <i class="fas fa-list"></i> 
                    Mostrando <span id="${options.visibleCountId || 'itensVisiveis'}">0</span> de <span id="${options.totalCountId || 'totalItens'}">0</span> itens
                </span>
                <div class="btn-group" role="group" id="${options.paginationControlsId || 'controlesNavegacao'}">
                    <button type="button" class="btn btn-outline-secondary btn-sm" id="${options.prevBtnId || 'btnAnterior'}" disabled>
                        <i class="fas fa-chevron-left"></i> Anterior
                    </button>
                    <button type="button" class="btn btn-outline-secondary btn-sm" id="${options.nextBtnId || 'btnProximo'}">
                        Próximo <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            </div>
            <div id="${options.pageInfoId || 'infoPaginacao'}" class="mt-1"></div>
        </div>
    </div>`;
    
    // Busca (se habilitada)
    if (defaultOptions.showSearch) {
        html = `
            <div class="row mb-3">
                <div class="col-md-12">
                    <div class="input-group shadow-sm">
                        <span class="input-group-text bg-primary text-white border-0">
                            <i class="fas fa-search"></i>
                        </span>
                        <input type="text" class="form-control border-0" id="${options.searchId || 'buscaPrincipal'}" 
                               placeholder="${defaultOptions.searchPlaceholder}"
                               style="padding: 15px; font-size: 1rem;">
                    </div>
                </div>
            </div>
        ` + html;
    }
    
    $(`#${containerId}`).html(html);
}

// Exportar para uso global
window.TablePagination = TablePagination;
window.createPaginationControls = createPaginationControls;