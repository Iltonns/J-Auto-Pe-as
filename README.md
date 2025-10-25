# 🔧 AutoPeças Pro - Sistema Profissional de Gestão Automotiva

Sistema completo de gestão para lojas de autopeças com design moderno e profissional inspirado no setor automotivo. Desenvolvido em Flask com SQLite e interface responsiva.

## 🎨 Novo Design Automotivo 2025

### Características Visuais
- **Paleta de Cores Profissional**: Azul escuro, laranja energia, cinza metálico
- **Layout Responsivo**: Design adaptado para desktop, tablet e mobile
- **Animações Suaves**: Efeitos de transição e hover profissionais
- **Ícones Temáticos**: Ícones específicos do setor automotivo
- **Gradientes Modernos**: Efeitos visuais que transmitem inovação e tecnologia

### Componentes Visuais
- Cards com bordas arredondadas e sombras suaves
- Botões com gradientes e efeitos hover
- Sidebar temática com ícones automotivos
- Dashboard com métricas animadas
- Alertas e notificações personalizadas

## 🚀 Funcionalidades

### 📊 Dashboard Principal
- Visão geral das estatísticas do negócio
- Produtos em estoque baixo
- Vendas recentes
- Contas a pagar/receber do dia

### 👥 Gestão de Clientes
- Cadastro completo de clientes
- Edição e exclusão de clientes
- Histórico de compras

### 📦 Gestão de Produtos
- Cadastro manual de produtos com código de barras
- **🆕 Importação automática via XML de NFe** com configurações avançadas
- Controle de estoque com NCM e unidade de medida
- Categorização automática baseada em NCM
- Alertas de estoque baixo
- Detecção automática de produtos duplicados
- Calculadora de preços com margem de lucro

#### 📥 Importação de Produtos via XML de NFe
- **Upload de arquivos XML** de Nota Fiscal Eletrônica
- **Extração automática** de dados dos produtos (código, nome, código de barras, NCM, preços)
- **Configurações flexíveis**:
  - Margem de lucro personalizada
  - Estoque mínimo padrão
  - Ação para produtos existentes (atualizar, sobrescrever ou ignorar)
- **Categorização inteligente** baseada no código NCM
- **Relatórios detalhados** de importação com produtos processados
- **Validação de dados** e tratamento de erros

### 💰 Sistema de Vendas
- PDV (Ponto de Venda) integrado
- Múltiplas formas de pagamento
- Busca rápida por código de barras
- Vendas a prazo com contas a receber

### 💳 Controle Financeiro
- Contas a pagar com vencimento
- Contas a receber de vendas a prazo
- Alertas de vencimentos

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Banco de Dados**: SQLite
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Autenticação**: Flask-Login
- **Ícones**: Font Awesome, Bootstrap Icons

## 📋 Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/Iltonns/Autope-as-4-Irm-os.git
   cd Autope-as-4-Irm-os
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicialize o banco de dados**
   ```bash
   python Minha_autopecas_web/logica_banco.py
   ```

4. **Adicione dados de exemplo (opcional)**
   ```bash
   python popular_dados.py
   ```

5. **Execute a aplicação**
   ```bash
   python app.py
   ```

6. **Acesse o sistema**
   - Abra seu navegador e vá para: http://127.0.0.1:5000
   - **Usuário**: admin
   - **Senha**: admin123

## 🆕 Importação XML de NFe

### Como importar produtos via XML
1. Acesse a área de **Produtos**
2. Clique em **Importar XML**
3. Selecione um arquivo XML de Nota Fiscal Eletrônica
4. Clique em **Importar Produtos**

### Dados importados automaticamente
- Nome do produto
- Preço unitário
- Quantidade (adicionada ao estoque)
- Código de barras (EAN)
- NCM (Nomenclatura Comum do Mercosul)
- Unidade de medida

### Comportamento inteligente
- **Produtos novos**: Criados automaticamente
- **Produtos existentes**: Estoque atualizado
- **Detecção de duplicatas**: Por código de barras e nome
- **Relatório completo**: Sucessos e erros detalhados

📄 Ver documentação completa em [`GUIA_IMPORTACAO_XML.md`](GUIA_IMPORTACAO_XML.md)

## 📱 Como Usar

### Login
- Use as credenciais padrão: `admin` / `admin123`
- O sistema criará automaticamente o usuário administrador na primeira execução

### Dashboard
- Visualize estatísticas gerais do negócio
- Monitore produtos com estoque baixo
- Acompanhe vendas recentes

### Clientes
- Adicione novos clientes clicando em "Novo Cliente"
- Edite informações existentes
- Gerencie base de clientes

### Produtos
- Cadastre produtos com informações completas
- Use códigos de barras para busca rápida
- Defina estoque mínimo para alertas

### Vendas
- Use o sistema PDV para registrar vendas
- Busque produtos por código de barras, nome ou ID
- Escolha formas de pagamento (dinheiro, PIX, cartão, prazo)
- Vendas a prazo geram automaticamente contas a receber

### Financeiro
- Monitore contas a pagar do dia
- Acompanhe recebimentos pendentes
- Marque contas como pagas/recebidas

## 🗂️ Estrutura do Projeto

```
Autope-as-4-Irm-os/
├── app.py                      # Aplicação principal Flask
├── requirements.txt            # Dependências Python
├── popular_dados.py           # Script para dados de exemplo
├── autopecas.db              # Banco de dados SQLite (criado automaticamente)
├── Minha_autopecas_web/
│   ├── __init__.py
│   └── logica_banco.py       # Funções de banco de dados
└── templates/                # Templates HTML
    ├── base.html            # Template base
    ├── dashboard.html       # Dashboard principal
    ├── clientes.html        # Gestão de clientes
    ├── produtos.html        # Gestão de produtos
    ├── vendas.html          # Sistema de vendas
    ├── login.html           # Tela de login
    ├── contas_a_pagar_hoje.html
    ├── contas_a_receber_hoje.html
    ├── relatorios.html      # Relatórios (em desenvolvimento)
    └── erros/               # Páginas de erro
        ├── 404.html
        └── 500.html
```

## 🔒 Segurança

- Senhas são criptografadas usando Werkzeug
- Sistema de autenticação com Flask-Login
- Sessões seguras
- **⚠️ IMPORTANTE**: Altere a `secret_key` em produção

## 🐛 Solução de Problemas

### Erro de banco de dados
```bash
# Reinicialize o banco
python Minha_autopecas_web/logica_banco.py
```

### Problemas de dependências
```bash
# Reinstale as dependências
pip install -r requirements.txt --upgrade
```

### Erro de porta ocupada
- Altere a porta no arquivo `app.py` na linha final:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Mude para outra porta
```

## 🚀 Próximas Funcionalidades

- [ ] Relatórios avançados
- [ ] Importação de produtos via XML
- [ ] Sistema de backup automático
- [ ] Múltiplos usuários e permissões
- [ ] API REST
- [ ] App mobile

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Família Autopeças**
- GitHub: [@Iltonns](https://github.com/Iltonns)

## 📞 Suporte

Se você encontrar algum problema ou tiver dúvidas:
1. Verifique a seção de solução de problemas
2. Abra uma issue no GitHub
3. Entre em contato via email

---

⭐ Se este projeto te ajudou, deixe uma estrela no GitHub!

### 👥 Gestão de Clientes
- Cadastro completo de clientes
- Controle de CPF/CNPJ
- Histórico de compras
- Dados de contato e endereço

### 🔧 Gestão de Produtos
- Cadastro manual de produtos
- **Importação automática via XML** (NFe)
- Controle de código de barras
- Gestão de estoque em tempo real
- Alertas de estoque baixo
- Busca rápida por código ou nome

### 💰 Sistema Financeiro Completo
- **Contas a Pagar Hoje** - Controle de vencimentos diários
- **Contas a Receber Hoje** - Acompanhamento de recebimentos
- Relatórios financeiros detalhados

### 🛒 Sistema de Vendas e Caixa
- Interface moderna de PDV (Ponto de Venda)
- Leitor de código de barras
- Múltiplas formas de pagamento (Dinheiro, PIX, Cartão, A Prazo)
- Cálculo automático de troco
- Produtos favoritos para vendas rápidas
- Controle de caixa diário

### 📊 Relatórios e Dashboard
- Dashboard com métricas importantes
- Relatórios de vendas
- Controle de estoque
- Análises financeiras
- Gráficos e estatísticas

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.9+ com Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: SQLite (fácil setup) / PostgreSQL (produção)
- **Autenticação**: Flask-Login
- **PDF**: ReportLab
- **XML Processing**: ElementTree (nativo Python)

## 🚀 Como Executar

### 1. Pré-requisitos
```bash
# Python 3.9 ou superior
python --version

# Git
git --version
```

### 2. Clonagem e Setup
```bash
# Clonar o repositório
git clone https://github.com/Iltonns/Autope-as-4-Irm-os.git
cd Autope-as-4-Irm-os

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração do Banco
```bash
# O banco SQLite será criado automaticamente na primeira execução
# Arquivo: loja.db
```

### 4. Executar a Aplicação
```bash
python app.py
```

### 5. Acessar o Sistema
- URL: `http://localhost:5000`
- **Usuário padrão**: `admin`
- **Senha padrão**: `admin123`

## 📁 Estrutura do Projeto

```
Autope-as-4-Irm-os/
├── app.py                          # Aplicação principal Flask
├── Minha_autopecas_web/
│   ├── __init__.py
│   ├── logica_banco.py            # Lógica do banco de dados
│   └── criar_usuarios.py          # Script para criar usuários
├── templates/                      # Templates HTML
│   ├── base.html                  # Template base
│   ├── login.html                 # Página de login
│   ├── clientes.html              # Gestão de clientes
│   ├── produtos.html              # Gestão de produtos
│   ├── vendas.html                # Sistema de vendas/caixa
│   ├── contas_a_pagar_hoje.html   # Contas a pagar hoje
│   ├── contas_a_receber_hoje.html # Contas a receber hoje
│   └── erros/
│       └── 404.html               # Página de erro 404
├── requirements.txt               # Dependências Python
├── runtime.txt                   # Versão do Python
└── README.md                     # Este arquivo
```

## 💡 Funcionalidades Especiais

### 📦 Importação de XML (NFe)
O sistema permite importar produtos diretamente de arquivos XML de Nota Fiscal Eletrônica:
- Extrai automaticamente: nome, preço, quantidade e código de barras
- Processa múltiplos produtos por arquivo
- Validação de dados e relatório de importação

### 📅 Sistema de Calendário Financeiro
- Visualização de vencimentos por data
- Alertas de vencimentos próximos
- Controle de inadimplência
- Negociação de parcelamentos

### 🔍 Busca Inteligente
- Busca por código de barras
- Busca por nome (parcial)
- Busca por ID do produto
- Resultados instantâneos

### 📱 Interface Responsiva
- Funciona em desktop, tablet e smartphone
- Design moderno e intuitivo
- Cores e ícones específicos para autopeças

## 🔧 Configurações Avançadas

### Banco de Dados PostgreSQL (Produção)
Para usar PostgreSQL em produção, modifique a função `get_db_connection()` em `logica_banco.py`:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="autopecas",
        user="seu_usuario",
        password="sua_senha",
        cursor_factory=RealDictCursor
    )
    return conn
```

### Variáveis de Ambiente
```bash
# .env (criar arquivo)
SECRET_KEY=sua_chave_secreta_super_segura
DATABASE_URL=sqlite:///loja.db
DEBUG=False
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte e dúvidas:
- 📧 Email: [seu_email@exemplo.com]
- 📱 WhatsApp: [seu_numero]
- 🐛 Issues: [GitHub Issues](https://github.com/Iltonns/Autope-as-4-Irm-os/issues)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🏆 Feito com ❤️ para a Família

Desenvolvido especialmente para atender as necessidades de lojas de autopeças familiares, com foco em:
- Facilidade de uso
- Funcionalidades práticas
- Interface intuitiva
- Controle financeiro eficiente

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela no GitHub!**