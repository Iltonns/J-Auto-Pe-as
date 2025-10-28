/**
 * Autocomplete para Marcas e Categorias
 * Carrega marcas e categorias do banco de dados para autocomplete nos modais
 */

// Carregar marcas e categorias do banco de dados
function carregarMarcasECategorias() {
    // Carregar marcas
    fetch('/api/marcas')
        .then(response => response.json())
        .then(marcas => {
            // Para movimentações
            const datalistMovimentacoes = document.getElementById('marcas-list');
            if (datalistMovimentacoes) {
                datalistMovimentacoes.innerHTML = '';
                marcas.forEach(marca => {
                    const option = document.createElement('option');
                    option.value = marca;
                    datalistMovimentacoes.appendChild(option);
                });
                console.log(`✅ ${marcas.length} marcas carregadas (movimentações)`);
            }
            
            // Para produtos
            const datalistProdutos = document.getElementById('marcas-list-produtos');
            if (datalistProdutos) {
                datalistProdutos.innerHTML = '';
                marcas.forEach(marca => {
                    const option = document.createElement('option');
                    option.value = marca;
                    datalistProdutos.appendChild(option);
                });
                console.log(`✅ ${marcas.length} marcas carregadas (produtos)`);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar marcas:', error);
        });
    
    // Carregar categorias
    fetch('/api/categorias')
        .then(response => response.json())
        .then(categorias => {
            // Para movimentações
            const datalistMovimentacoes = document.getElementById('categorias-list');
            if (datalistMovimentacoes) {
                datalistMovimentacoes.innerHTML = '';
                categorias.forEach(categoria => {
                    const option = document.createElement('option');
                    option.value = categoria;
                    datalistMovimentacoes.appendChild(option);
                });
                console.log(`✅ ${categorias.length} categorias carregadas (movimentações)`);
            }
            
            // Para produtos
            const datalistProdutos = document.getElementById('categorias-list-produtos');
            if (datalistProdutos) {
                datalistProdutos.innerHTML = '';
                categorias.forEach(categoria => {
                    const option = document.createElement('option');
                    option.value = categoria;
                    datalistProdutos.appendChild(option);
                });
                console.log(`✅ ${categorias.length} categorias carregadas (produtos)`);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar categorias:', error);
        });
}

// Carregar ao abrir a página
document.addEventListener('DOMContentLoaded', function() {
    carregarMarcasECategorias();
});

// Recarregar quando abrir os modais (para pegar novos cadastros)
// Modais de movimentações
const modalAdicionarMovimentacao = document.getElementById('modalAdicionarMovimentacao');
if (modalAdicionarMovimentacao) {
    modalAdicionarMovimentacao.addEventListener('shown.bs.modal', carregarMarcasECategorias);
}

const modalEditarMovimentacao = document.getElementById('modalEditarMovimentacao');
if (modalEditarMovimentacao) {
    modalEditarMovimentacao.addEventListener('shown.bs.modal', carregarMarcasECategorias);
}

// Modais de produtos
const modalAdicionarProduto = document.getElementById('modalAdicionarProduto');
if (modalAdicionarProduto) {
    modalAdicionarProduto.addEventListener('shown.bs.modal', carregarMarcasECategorias);
}

const modalEditarProduto = document.getElementById('modalEditarProduto');
if (modalEditarProduto) {
    modalEditarProduto.addEventListener('shown.bs.modal', carregarMarcasECategorias);
}
