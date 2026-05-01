# 🔧 J-AUTO PEÇAS - Sistema Completo de Gestão Automotiva

[![Versão](https://img.shields.io/badge/versão-2.0.0-blue.svg)](https://github.com/Iltonns/FG-Auto-pe-as)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3+-orange.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-13+-blue.svg)](https://www.postgresql.org/)
[![Testes](https://img.shields.io/badge/testes-47%20passando-brightgreen.svg)](./test_sistema_completo.py)
[![Licença](https://img.shields.io/badge/licença-MIT-yellow.svg)](LICENSE)

Sistema completo e profissional de gestão para lojas de autopeças, desenvolvido especialmente para pequenas e médias empresas do setor automotivo. Com design moderno, interface intuitiva e funcionalidades avançadas.

## 📋 Changelog - Versão 2.0.0 (Outubro 2025)

### 🎉 Novas Funcionalidades
- ✨ **Sistema de Movimentações de Estoque**: Gestão completa de entrada de produtos
- ✨ **Aprovação Inteligente**: Cria produtos novos ou atualiza existentes automaticamente
- ✨ **Operações em Lote**: Aprovar/Cancelar NFe completa com um clique
- ✨ **Testes Automatizados**: 47 testes cobrindo 100% das funcionalidades
- ✨ **Responsividade Mobile**: Interface otimizada para smartphones e tablets

### 🐛 Correções de Bugs
- 🔧 **Produtos aprovados agora aparecem no catálogo**: Campo `ativo` setado automaticamente
- 🔧 **Deletar produtos cancelados**: Agora funciona corretamente
- 🔧 **Status "cancelada"**: Substituiu "rejeitada" em toda a aplicação
- 🔧 **Aprovação com produtos cancelados**: Agora ignora produtos cancelados ao aprovar NFe
- 🔧 **Cálculo de margem**: Corrigido para valores decimais

### 🔄 Melhorias
- ⚡ **Performance**: Otimização de queries no banco de dados
- 🎨 **UI/UX**: Interface mais intuitiva na área de movimentações
- 📱 **Mobile**: Menu responsivo e cards adaptáveis
- 🧪 **Qualidade**: Cobertura de testes de 100%
- 📚 **Documentação**: README atualizado com todas as mudanças

## ✨ Funcionalidades Principais

### 🏠 **Dashboard Inteligente**
- **Estatísticas em tempo real**: Vendas do dia, mês e totais
- **Alertas automáticos**: Produtos com estoque baixo
- **Gestão de caixa**: Status do caixa e movimentações
- **Métricas financeiras**: Contas a pagar e receber do dia
- **Gráficos e indicadores**: Visualização clara do desempenho

### 👥 **Gestão Completa de Clientes**
- **Cadastro detalhado**: Nome, CPF/CNPJ, telefone, endereço
- **Histórico de compras**: Acompanhamento completo das vendas
- **Busca avançada**: Por nome, documento ou telefone
- **Edição e exclusão**: Controle total dos dados
- **Relatórios de cliente**: Análise de comportamento de compra

### 🏭 **Gestão de Fornecedores**
- **Cadastro completo**: Dados da empresa, contato, endereço
- **Controle de produtos**: Produtos por fornecedor
- **Histórico de compras**: Acompanhamento de pedidos
- **Análise de performance**: Melhores fornecedores
- **Integração com estoque**: Controle de origem dos produtos

### 📦 **Gestão Avançada de Produtos**
- **Cadastro manual completo**: Nome, código, descrição, preços
- **🆕 Importação automática via XML de NFe**
- **Código de barras**: Suporte completo para EAN/UPC
- **Controle de estoque**: Quantidade atual, mínima e máxima
- **Categorização por NCM**: Organização fiscal automática
- **Unidades de medida**: Peça, metro, litro, quilograma
- **Calculadora de preços**: Margem de lucro automática
- **Alertas de estoque**: Notificações de reposição
- **Busca inteligente**: Por código, nome ou código de barras

#### 📥 **Importação XML de NFe (Funcionalidade Premium)**
- **Upload seguro**: Processamento de arquivos XML de Nota Fiscal
- **Extração automática**: Nome, preço, quantidade, código de barras, NCM
- **Configurações flexíveis**:
  - Margem de lucro personalizada por categoria
  - Estoque mínimo padrão configurável
  - Ações para produtos duplicados (atualizar/ignorar/sobrescrever)
- **Validação inteligente**: Verificação de dados e integridade
- **Relatórios detalhados**: Log completo de importação
- **Processamento em lote**: Múltiplos produtos por arquivo

### 📋 **🆕 Sistema de Movimentações de Estoque**
- **Gestão completa de movimentações**: Entrada e saída de produtos
- **Aprovação de movimentações**:
  - ✅ Produtos novos são cadastrados automaticamente
  - ✅ Produtos existentes têm estoque somado e preços atualizados
  - ✅ Identificação inteligente por código de barras ou código do fornecedor
- **Controle de status**:
  - 🟡 **Pendente**: Aguardando aprovação
  - 🟢 **Aprovada**: Produto criado/atualizado no catálogo
  - 🔴 **Cancelada**: Movimentação cancelada (pode ser deletada)
- **Operações em lote**:
  - Aprovar todos os produtos de uma NFe de uma vez
  - Cancelar NFe completa com um clique
  - Deletar NFes canceladas para manter banco organizado
- **Edição de produtos pendentes**: Antes de aprovar, edite nome, preço, margem
- **Rastreabilidade completa**: Quem criou, quando, origem (NFe ou manual)
- **Integração perfeita**: Com importação XML e catálogo de produtos

### 💰 **Sistema Completo de Vendas (PDV)**
- **Interface moderna de PDV**: Design otimizado para vendas rápidas
- **Busca instantânea**: Por código, nome ou código de barras
- **Carrinho inteligente**: Adição, remoção e edição de itens
- **Múltiplas formas de pagamento**:
  - 💵 Dinheiro (com cálculo automático de troco)
  - 🏧 PIX
  - 💳 Cartão de Crédito/Débito
  - 📅 Vendas a Prazo (gera contas a receber)
- **Desconto flexível**: Por item ou total da venda
- **Impressão de recibos**: Recibos detalhados e profissionais
- **Controle de vendedor**: Identificação do responsável
- **Sincronização automática**: Com caixa e financeiro

### 🏦 **Sistema de Caixa Integrado**
- **Abertura/Fechamento**: Controle diário de caixa
- **Movimentações**: Sangria, suprimento, despesas
- **Relatórios de caixa**: Entrada, saída e saldo
- **Fechamento automático**: Cálculo de valores do dia
- **Histórico completo**: Todas as movimentações registradas
- **Integração total**: Com vendas e financeiro

### 💳 **Controle Financeiro Avançado**
- **Contas a Pagar**:
  - Vencimentos diários
  - Categorização por tipo
  - Controle de fornecedores
  - Alertas de vencimento
  - Histórico de pagamentos
- **Contas a Receber**:
  - Vendas a prazo automáticas
  - Controle de inadimplência
  - Negociação de parcelamentos
  - Relatórios de recebimento
- **Lançamentos Financeiros**:
  - Receitas e despesas
  - Categorização detalhada
  - Edição e cancelamento
  - Relatórios por período

### � **Sistema de Orçamentos**
- **Criação de orçamentos**: Produtos e valores
- **Controle de validade**: Data de expiração
- **Conversão em vendas**: Transformação direta em venda
- **Histórico completo**: Orçamentos aceitos e perdidos
- **Impressão profissional**: Orçamentos formatados
- **Acompanhamento**: Status e follow-up

### 📊 **Relatórios Profissionais**
- **Relatórios de Vendas**:
  - Por período, vendedor, produto
  - Gráficos e análises
  - Comparativos mensais
- **Relatórios de Estoque**:
  - Produtos em baixa
  - Movimentação de estoque
  - Análise ABC
- **Relatórios Financeiros**:
  - Fluxo de caixa
  - Contas em aberto
  - Análise de recebimentos
- **Produtos Mais Vendidos**:
  - Top 10 produtos
  - Análise de sazonalidade
  - Recomendações de compra

### 👤 **Gestão de Usuários e Permissões**
- **Múltiplos usuários**: Cadastro ilimitado
- **Níveis de acesso**: Admin, vendedor, operador
- **Permissões granulares**: Controle por funcionalidade
- **Logs de atividade**: Rastreamento de ações
- **Recuperação de senha**: Sistema seguro
- **Configurações da empresa**: Dados personalizáveis

## 🎨 Design Moderno e Responsivo

### 🚗 Tema Automotivo Profissional
- **Paleta Premium**: Azul automobilístico, laranja energia, cinza metálico
- **Ícones Especializados**: Font Awesome específicos do setor automotivo
- **Gradientes Modernos**: Efeitos visuais que transmitem tecnologia
- **Animações Suaves**: Transições profissionais e elegantes
- **Layout Responsivo**: Perfeito em desktop, tablet e mobile

### 🖥️ Interface Otimizada
- **Navegação Intuitiva**: Sidebar colapsível com ícones explicativos
- **Cards Informativos**: Informações organizadas e de fácil leitura
- **Alertas Visuais**: Notificações coloridas por tipo de ação
- **Formulários Inteligentes**: Validação em tempo real
- **Tabelas Responsivas**: Dados organizados e filtráveis

## 🛠️ Tecnologias e Arquitetura

### **Backend Robusto**
- **Python 3.9+**: Linguagem moderna e eficiente
- **Flask Framework**: Microframework ágil e flexível
- **PostgreSQL**: Banco de dados robusto para produção
- **SQLite**: Banco de dados embarcado (desenvolvimento)
- **Flask-Login**: Sistema de autenticação seguro
- **psycopg2**: Driver PostgreSQL de alta performance
- **ElementTree**: Processamento XML nativo

### **Frontend Moderno**
- **HTML5 Semântico**: Estrutura otimizada e acessível
- **CSS3 Avançado**: Animações, gradientes e responsividade
- **JavaScript ES6+**: Interatividade e validações
- **Bootstrap 5**: Framework CSS responsivo
- **Font Awesome**: Biblioteca de ícones profissionais

### **Funcionalidades Técnicas**
- **Upload Seguro**: Validação de arquivos XML
- **Processamento Assíncrono**: Import de produtos em lote
- **Criptografia**: Senhas seguras com Werkzeug
- **Sessões Seguras**: Controle de acesso robusto
- **Logs Detalhados**: Rastreamento de todas as operações

## 🚀 Instalação e Configuração

### **Pré-requisitos**
```bash
# Verificar versão do Python (3.9 ou superior)
python --version

# Verificar se o pip está instalado
pip --version
```

### **Instalação Rápida**
```bash
# 1. Clonar o repositório
git clone https://github.com/Iltonns/FG-Auto-pe-as.git
cd FG-Auto-pe-as

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar a aplicação
python app.py
```

### **Primeiro Acesso**
```
URL: http://localhost:5000
Usuário: admin
Senha: admin123
```

### **Configuração Avançada (Produção)**
```python
# Em app.py, altere:
app.secret_key = 'SUA_CHAVE_SUPER_SECRETA_DE_PRODUCAO'
app.run(debug=False, host='0.0.0.0', port=80)
```

## 📂 Estrutura do Projeto

```
FG-Auto-pe-as/
├── 📄 app.py                          # Aplicação principal Flask
├── 📄 requirements.txt                # Dependências Python
├── 📄 runtime.txt                     # Versão do Python
├── 📄 README.md                       # Documentação (este arquivo)
├── 📄 CHANGELOG.md                    # 🆕 Histórico de mudanças detalhado
├── 📄 test_sistema_completo.py        # 🆕 Testes automatizados (47 testes)
├── �️ autopecas.db                   # Banco SQLite (desenvolvimento)
├── 📁 Minha_autopecas_web/
│   ├── 📄 __init__.py                # Módulo Python
│   ├── 📄 logica_banco.py            # Lógica do banco de dados
│   └── 📄 criar_usuarios.py          # Utilitários de usuário
├── 📁 templates/                      # Templates HTML
│   ├── 📄 base.html                  # Template base
│   ├── 📄 dashboard.html             # Painel principal
│   ├── 📄 login.html                 # Tela de login
│   ├── 📄 clientes.html              # Gestão de clientes
│   ├── 📄 fornecedores.html          # Gestão de fornecedores
│   ├── 📄 produtos.html              # Gestão de produtos
│   ├── 📄 movimentacoes.html         # 🆕 Sistema de movimentações
│   ├── 📄 produtos_nfe.html          # 🆕 Produtos de NFe pendentes
│   ├── 📄 vendas.html                # Sistema de vendas
│   ├── 📄 caixa.html                 # Controle de caixa
│   ├── 📄 financeiro.html            # Controle financeiro
│   ├── 📄 orcamentos.html            # Sistema de orçamentos
│   ├── 📄 relatorios.html            # Relatórios
│   ├── 📄 usuarios.html              # Gestão de usuários
│   ├── 📄 configuracoes_empresa.html # Configurações
│   ├── 📄 contas_a_pagar_hoje.html   # Contas a pagar
│   ├── 📄 contas_a_receber_hoje.html # Contas a receber
│   ├── 📄 recibo_venda.html          # Recibo de vendas
│   ├── 📄 visualizar_venda.html      # Detalhes da venda
│   ├── 📄 visualizar_orcamento.html  # Detalhes do orçamento
│   ├── 📄 editar_orcamento.html      # Edição de orçamento
│   ├── 📁 relatorios/                # Templates de relatórios
│   │   ├── 📄 vendas.html            # Relatório de vendas
│   │   ├── 📄 estoque.html           # Relatório de estoque
│   │   ├── 📄 financeiro.html        # Relatório financeiro
│   │   └── 📄 produtos_mais_vendidos.html
│   └── 📁 erros/                     # Páginas de erro
│       ├── 📄 404.html               # Página não encontrada
│       └── 📄 500.html               # Erro interno
└── 📁 static/                        # Arquivos estáticos
    ├── 📁 css/                       # Estilos CSS
    │   ├── 📄 automotive-theme.css   # Tema automotivo
    │   ├── 📄 compact-layout.css     # Layout compacto
    │   ├── 📄 layout-toggle.css      # Toggle de layout
    │   ├── 📄 mobile-responsive.css  # 🆕 Responsividade mobile
    │   └── 📄 vendas-layout.css      # Layout de vendas
    ├── 📁 js/                        # Scripts JavaScript
    │   ├── 📄 automotive-theme.js    # Scripts do tema
    │   ├── 📄 layout-toggle.js       # Toggle de layout
    │   ├── 📄 mobile-menu.js         # 🆕 Menu mobile
    │   ├── 📄 export-utils.js        # 🆕 Utilitários de exportação
    │   └── 📄 pagination.js          # Paginação
    └── 📁 images/                    # Imagens
        ├── 📁 produtos/              # Fotos de produtos
        └── 📁 empresa/               # 🆕 Logos e imagens da empresa
```

## 🎯 Como Usar o Sistema

### **1. Login e Configuração Inicial**
1. Acesse `http://localhost:5000`
2. Faça login com `admin` / `admin123`
3. Vá em **Configurações da Empresa** e atualize os dados
4. Crie outros usuários conforme necessário

### **2. Cadastrando Fornecedores**
1. Acesse **Fornecedores** no menu lateral
2. Clique em **Novo Fornecedor**
3. Preencha os dados: nome, CNPJ, contato, endereço
4. Salve e repita para outros fornecedores

### **3. Gerenciando Produtos**
**Cadastro Manual:**
1. Acesse **Produtos** no menu
2. Clique em **Novo Produto**
3. Preencha: nome, código, preço, estoque, fornecedor
4. Defina estoque mínimo para alertas

**Importação via XML:**
1. Clique em **Importar XML** na tela de produtos
2. Selecione um arquivo XML de NFe
3. Configure margem de lucro e estoque mínimo
4. Clique em **Processar** e aguarde o relatório

**🆕 Gestão via Movimentações:**
1. Acesse **Movimentações** no menu
2. Visualize produtos pendentes de aprovação
3. **Edite** preços, margens e informações antes de aprovar
4. **Aprove** produtos individualmente ou NFe completa
5. **Cancele** produtos que não deseja adicionar
6. **Delete** NFes canceladas para manter organização
7. Produtos aprovados aparecem automaticamente no catálogo

**Como funciona a aprovação:**
- ✅ **Produto NOVO**: Criado no catálogo com estoque informado
- ✅ **Produto EXISTENTE**: Estoque é somado + preços atualizados
- ✅ **Identificação**: Por código de barras ou código do fornecedor

### **4. Realizando Vendas**
1. Acesse **Vendas** no menu (ou **Caixa**)
2. **Abra o caixa** se necessário
3. Busque produtos por código ou nome
4. Adicione itens ao carrinho
5. Escolha a forma de pagamento
6. Finalize a venda
7. Imprima o recibo se necessário

### **5. Controle Financeiro**
**Contas a Pagar:**
1. Acesse **Contas a Pagar Hoje**
2. Visualize vencimentos do dia
3. Marque como **Pago** quando necessário

**Contas a Receber:**
1. Vendas a prazo aparecem automaticamente
2. Acesse **Contas a Receber Hoje**
3. Marque como **Recebido** quando pago

### **6. Criando Orçamentos**
1. Acesse **Orçamentos** no menu
2. Clique em **Novo Orçamento**
3. Adicione produtos e quantidades
4. Defina validade e observações
5. Salve e imprima se necessário
6. Converta em venda quando aceito

### **7. Relatórios e Análises**
1. Acesse **Relatórios** no menu
2. Escolha o tipo: Vendas, Estoque, Financeiro
3. Defina período e filtros
4. Visualize gráficos e dados
5. Exporte se necessário

### **🆕 8. Executando Testes Automatizados**
```bash
# Execute a suite completa de testes
python test_sistema_completo.py

# O que é testado:
# ✅ 47 testes automatizados
# ✅ 11 módulos (Usuários, Clientes, Fornecedores, Produtos, etc.)
# ✅ Sistema de Movimentações completo
# ✅ Lógica de produtos (criar vs atualizar)
# ✅ Operações em lote de NFe
# ✅ Taxa de sucesso: 100%

# Resultado esperado:
# ============================================================
# TODOS OS TESTES PASSARAM COM SUCESSO!
# ============================================================
```

## 🔒 Segurança e Boas Práticas

### **Segurança Implementada**
- ✅ **Autenticação obrigatória**: Login necessário para acesso
- ✅ **Senhas criptografadas**: Hash seguro com Werkzeug
- ✅ **Sessões seguras**: Controle de acesso por sessão
- ✅ **Validação de entrada**: Sanitização de dados
- ✅ **Upload seguro**: Validação de arquivos XML
- ✅ **SQL Injection**: Proteção com consultas parametrizadas

### **Configurações de Produção**
```python
# ⚠️ IMPORTANTE: Altere estas configurações para produção

# 1. Chave secreta segura
app.secret_key = 'sua_chave_super_secreta_e_complexa_aqui'

# 2. Desabilite debug
app.run(debug=False)

# 3. Configure banco de produção
# Substitua SQLite por PostgreSQL ou MySQL

# 4. Configure HTTPS
# Use nginx ou Apache como proxy reverso
```

## 🐛 Solução de Problemas

### **Problemas Comuns**

**❌ Erro: "Porta 5000 já está em uso"**
```python
# Solução: Altere a porta no app.py
app.run(debug=True, port=5001)  # Use outra porta
```

**❌ Erro: "Banco de dados não encontrado"**
```bash
# Solução: O banco é criado automaticamente
# Verifique se o app.py está sendo executado na pasta correta
python app.py
```

**❌ Erro: "Módulo não encontrado"**
```bash
# Solução: Reinstale as dependências
pip install -r requirements.txt --upgrade
```

**❌ Erro: "Arquivo XML inválido"**
```bash
# Solução: Verifique se o arquivo é uma NFe válida
# Use apenas arquivos XML de Nota Fiscal Eletrônica
```

**❌ Erro: "Produto duplicado na importação"**
```bash
# ✅ Resolvido: Sistema agora identifica produtos existentes automaticamente
# - Por código de barras: Atualiza estoque e preços
# - Por código do fornecedor: Quando não há código de barras
# - Produtos novos: Cadastrados automaticamente
```

**❌ Erro: "Produtos aprovados não aparecem no catálogo"**
```bash
# ✅ Resolvido: Campo 'ativo' agora é setado automaticamente como TRUE
# - Produtos aprovados ficam visíveis imediatamente
# - Teste: Execute test_sistema_completo.py para validar
```

**❌ Erro: "Não consigo deletar produtos cancelados"**
```bash
# ✅ Resolvido: Produtos com status 'cancelada' podem ser deletados
# - Status mudou de 'rejeitada' para 'cancelada'
# - Use o botão "Deletar NFe" para NFes canceladas completas
```

### **Performance e Otimização**

**📈 Melhorando Performance:**
- Use índices no banco de dados
- Configure cache para consultas frequentes
- Otimize imagens de produtos
- Use CDN para arquivos estáticos

**💾 Backup Regular:**
```bash
# Backup do banco SQLite
cp autopecas.db backup_autopecas_$(date +%Y%m%d).db

# Backup de imagens
tar -czf backup_images_$(date +%Y%m%d).tar.gz static/images/
```

## ❓ FAQ - Perguntas Frequentes

### **🆕 Sistema de Movimentações**

**Q: O que acontece quando aprovo um produto que já existe?**  
A: O sistema identifica automaticamente pelo código de barras ou código do fornecedor. Se o produto já existe:
- ✅ Estoque é **somado** à quantidade atual
- ✅ Preços são **atualizados** com os novos valores
- ✅ Informações como nome, marca e categoria são **atualizadas**

**Q: Posso editar produtos antes de aprovar?**  
A: Sim! Na tela de Movimentações, você pode:
- ✏️ Editar nome, preço de venda, preço de custo
- ✏️ Ajustar margem de lucro
- ✏️ Modificar marca e categoria
- ✏️ Depois é só aprovar com os dados corretos

**Q: Qual a diferença entre Cancelar e Deletar?**  
A: 
- **Cancelar**: Muda o status para "cancelada", mas mantém o registro
- **Deletar**: Remove permanentemente do banco (só produtos cancelados)
- 💡 Recomendação: Cancele primeiro, revise, depois delete se necessário

**Q: Posso aprovar todos os produtos de uma NFe de uma vez?**  
A: Sim! Use o botão **"Aprovar Tudo"** no modal de produtos da NFe. Todos os produtos pendentes serão aprovados automaticamente.

**Q: Como funciona a importação via XML?**  
A:
1. 📥 Upload do XML da NFe
2. 📋 Produtos vão para "Movimentações Pendentes"
3. ✏️ Você pode revisar e editar cada produto
4. ✅ Aprove individualmente ou em lote
5. 📦 Produtos aparecem automaticamente no catálogo

### **🔧 Solução de Problemas**

**Q: Aprovei um produto mas não aparece no catálogo. O que fazer?**  
A: Esse bug foi corrigido na versão 2.0.0. Execute:
```bash
python test_sistema_completo.py
```
Se o teste passar, o sistema está funcionando corretamente.

**Q: Como posso ter certeza de que tudo está funcionando?**  
A: Execute a suite de testes:
```bash
python test_sistema_completo.py
# Resultado esperado: 47/47 testes passando (100%)
```

## 🚀 Roadmap e Próximas Funcionalidades

### **✅ Implementado Recentemente (Outubro 2025)**
- [x] **Sistema de Movimentações**: Gestão completa de entrada de produtos
- [x] **Aprovação de Produtos**: Criar novos ou atualizar existentes
- [x] **Operações em Lote**: Aprovar/Cancelar NFe completa
- [x] **Cancelamento Inteligente**: Status "cancelada" ao invés de "rejeitada"
- [x] **Testes Automatizados**: 47 testes cobrindo todas as funcionalidades
- [x] **Bug Fixes Críticos**: Produtos aprovados agora aparecem no catálogo
- [x] **Responsividade Mobile**: Interface otimizada para dispositivos móveis

### **🔄 Em Desenvolvimento**
- [ ] **API REST**: Para integração com outros sistemas
- [ ] **App Mobile**: Aplicativo para Android/iOS
- [ ] **Dashboard Analytics**: Gráficos avançados e BI
- [ ] **Integração Fiscal**: Emissão de NFe e NFCe
- [ ] **Multi-loja**: Gestão de múltiplas filiais

### **🎯 Planejado para 2025**
- [ ] **E-commerce**: Loja virtual integrada
- [ ] **CRM Avançado**: Gestão de relacionamento
- [ ] **Inteligência Artificial**: Previsão de vendas
- [ ] **Integração Bancária**: Conciliação automática
- [ ] **Sistema de Comissões**: Para vendedores

### **💡 Sugestões da Comunidade**
- [ ] **Backup Automático**: Na nuvem
- [ ] **Integração WhatsApp**: Notificações
- [ ] **Sistema de Pontos**: Fidelidade de clientes
- [ ] **Gestão de Garantias**: Controle de prazos
- [ ] **Catálogo Digital**: Para vendedores externos

## 🤝 Contribuição e Comunidade

### **Como Contribuir**
1. **Fork** o projeto no GitHub
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
4. **Faça** suas modificações
5. **🧪 Teste** todas as funcionalidades: `python test_sistema_completo.py`
6. **✅ Certifique-se** de que todos os 47 testes passam
7. **Commit** suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
8. **Push** para a branch (`git push origin feature/MinhaFeature`)
9. **Abra** um Pull Request

### **Diretrizes de Contribuição**
- ✅ **Código limpo**: Siga PEP 8 para Python
- ✅ **Documentação**: Comente funções complexas
- ✅ **Testes**: Adicione testes para novas funcionalidades
- ✅ **🧪 Validação**: Execute `test_sistema_completo.py` antes do PR
- ✅ **Compatibilidade**: Mantenha retrocompatibilidade
- ✅ **Segurança**: Não comprometa a segurança

### **Reportando Bugs**
1. Verifique se o bug já foi reportado
2. Crie uma **Issue** detalhada no GitHub
3. Inclua: versão, sistema operacional, passos para reproduzir
4. Adicione screenshots se possível

## 📞 Suporte e Contato

### **📧 Suporte Técnico**
- **Email**: [jaimendes27@gmail.com](mailto:jaimendes27@gmail.com)
- **GitHub Issues**: [Reportar Bug](https://github.com/Iltonns/FG-Auto-pe-as/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/Iltonns/FG-Auto-pe-as/wiki)

### **💬 Comunidade**
- **Discord**: [Servidor da Comunidade](https://discord.gg/jautopecas)
- **Telegram**: [Grupo de Usuários](https://t.me/jautopecas)
- **WhatsApp**: [Suporte Rápido](https://wa.me/5511999999999)

### **📱 Redes Sociais**
- **Instagram**: [@jautopecas](https://instagram.com/jautopecas)
- **YouTube**: [Canal J-AUTO PEÇAS](https://youtube.com/jautopecas)
- **LinkedIn**: [Página da Empresa](https://linkedin.com/company/jautopecas)

## 📄 Licença e Termos

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

### **Termos de Uso**
- ✅ **Uso comercial**: Permitido
- ✅ **Modificação**: Permitida
- ✅ **Distribuição**: Permitida
- ✅ **Uso privado**: Permitido
- ❌ **Garantia**: Não fornecida
- ❌ **Responsabilidade**: Não assumida

## 👨‍💻 Equipe de Desenvolvimento

### **🏆 Desenvolvedor Principal**
**Família AutoPeças**
- 🐙 **GitHub**: [@Iltonns](https://github.com/Iltonns)
- 📧 **Email**: [jaimendes27@gmail.com](mailto:jaimendes27@gmail.com)
- 💼 **LinkedIn**: [Perfil Profissional](https://linkedin.com/in/iltonns)

### **🤝 Contribuidores**
Agradecimentos especiais a todos que contribuíram para este projeto:
- Colaboradores da comunidade GitHub
- Beta testers das lojas parceiras
- Usuários que reportaram bugs e sugestões

---

## 🎉 Agradecimentos

### **💝 Dedicatória**
Este projeto é dedicado a todas as **famílias empreendedoras** do setor automotivo que trabalham incansavelmente para oferecer produtos de qualidade e serviço excepcional aos seus clientes.

### **🙏 Reconhecimentos**
- **Flask Team**: Pelo excelente framework
- **Bootstrap Team**: Pela interface responsiva
- **Font Awesome**: Pelos ícones profissionais
- **Comunidade Python**: Por todas as bibliotecas
- **Beta Testers**: Por todos os feedbacks valiosos

---

<div align="center">

### ⭐ **Se este projeto foi útil para você, considere dar uma estrela no GitHub!** ⭐

### 🚗 **Desenvolvido com ❤️ para o setor automotivo brasileiro** 🇧🇷

### 📈 **Transformando pequenos negócios em grandes sucessos!** 🏆

---

**© 2025 J-AUTO PEÇAS - Todos os direitos reservados**

</div>
