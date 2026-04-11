# Guia de Correcao de Erros 500

## Problema Identificado

O aplicativo está apresentando erro 500 nas sessões de Clientes, Contas a Pagar e Contas a Receber devido a dependen cias faltantes.

## Solução

### Passo 1: Instalar dependências (No terminal PowerShell na pasta do projeto)

```powershell
# Navegar para a pasta do projeto
cd "c:\Users\ilton\OneDrive\Documentos\GitHub\FG-Auto-pe-as"

# Ativar o ambiente virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install Flask werkzeug psycopg2-binary python-dotenv pytz
```

### Passo 2: Configurar variáveis de ambiente

Editar o arquivo `.env` com as credenciais corretas do banco de dados:

```
DATABASE_URL=postgresql://usuario:senha@host:porta/database
```

### Passo 3: Iniciar o banco de dados (opcional)

Caso seja a primeira vez que roda a aplicação:

```powershell
python init_database.py
```

### Passo 4: Atualizar colunas do banco (se já existia banco)

```powershell
python migrate_db.py
```

### Passo 5: Testar conexão

```powershell
python test_diagnostic.py
```

## Correções Implementadas

1. **Função `listar_clientes()`** - Agora usa COALESCE para lidar com colunas que podem ser NULL
2. **Funções `adicionar_cliente()` e `editar_cliente()`** - Agora têm fallback para colunas básicas se as novas colunas não existirem
3. **Header do modal de Clientes** - Atualizado de #1a237e para #2962ff (padrão)
4. **Todas as cores dos headers** - Padronizadas em #2962ff

## Status das Implementações

- [x] Campos de NF-e adicionados ao formulário de clientes
- [x] Banco de dados estruturado para suportar dados de NF-e
- [x] Rotas atualizadas para processar novos campos
- [x] Cores padronizadas nos headers
- [ ] Dependências instaladas (PENDENTE - executar comandos acima)
