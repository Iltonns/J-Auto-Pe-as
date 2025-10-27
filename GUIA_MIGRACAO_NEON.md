# 🚀 MIGRAÇÃO PARA POSTGRESQL NEON - GUIA COMPLETO

## ✅ O QUE JÁ FOI FEITO

1. ✅ Código convertido de SQLite para PostgreSQL
2. ✅ Dependências atualizadas (psycopg2-binary, python-dotenv)
3. ✅ Arquivos de configuração criados (.env, .env.example)
4. ✅ Script de migração de dados criado
5. ✅ Backup do código SQLite original feito

## 📋 PASSOS PARA CONFIGURAR O NEON

### 1. Criar Projeto no Neon

1. Acesse https://neon.tech
2. Faça login na sua conta
3. Clique em **"New Project"**
4. Configure:
   - **Project name**: `autopecas-sistema` (ou o nome que preferir)
   - **Region**: Escolha a mais próxima (ex: US East, São Paulo, etc.)
   - **Postgres version**: 16 (ou a mais recente)
5. Clique em **"Create Project"**

### 2. Obter String de Conexão

1. Após criar o projeto, você verá a dashboard
2. Procure por **"Connection String"** ou **"Connection Details"**
3. Copie a string que começa com `postgresql://`
4. Exemplo:
   ```
   postgresql://usuario:senha@ep-xyz-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### 3. Configurar o Arquivo .env

1. Abra o arquivo `.env` na raiz do projeto
2. Cole a string de conexão do Neon:
   ```env
   DATABASE_URL=postgresql://[COLE_AQUI_A_STRING_DO_NEON]
   SECRET_KEY=mude-esta-chave-para-algo-super-seguro-e-aleatorio
   FLASK_ENV=production
   ```
3. **IMPORTANTE**: Mude o `SECRET_KEY` para algo aleatório e seguro!
   - Exemplo: `SECRET_KEY=k8#mX9pL@2qR$7nW&5tY!vB4cZ`

### 4. Instalar Dependências

Abra o PowerShell na pasta do projeto e execute:

```powershell
pip install -r requirements.txt
```

Isso instalará:
- `psycopg2-binary` (driver PostgreSQL)
- `python-dotenv` (gerenciamento de variáveis de ambiente)

### 5. Inicializar o Banco de Dados

Execute o app uma vez para criar todas as tabelas:

```powershell
python app.py
```

O sistema irá:
- Conectar ao PostgreSQL Neon
- Criar todas as tabelas necessárias
- Criar usuário admin padrão

### 6. Migrar Dados Antigos (OPCIONAL)

**⚠️ APENAS se você tem dados no SQLite antigo:**

```powershell
python migrar_dados.py
```

O script irá:
- Ler todos os dados do `autopecas.db` (SQLite)
- Transferir para o PostgreSQL Neon
- Preservar todos os IDs e relacionamentos

**Se você está começando do zero, PULE este passo!**

### 7. Testar o Sistema

1. Inicie o aplicativo:
   ```powershell
   python app.py
   ```

2. Acesse no navegador:
   ```
   http://localhost:5000
   ```

3. Faça login com:
   - **Usuário**: `admin`
   - **Senha**: `admin123` (mude depois!)

4. Teste:
   - ✅ Cadastro de produto
   - ✅ Cadastro de cliente
   - ✅ Fazer uma venda
   - ✅ Consultar relatórios

## 🔐 SEGURANÇA

### Proteger Credenciais

O arquivo `.env` contém informações sensíveis e está protegido pelo `.gitignore`:

```gitignore
.env          # ✅ Já está no .gitignore
*.db          # ✅ SQLite também protegido
__pycache__/  # ✅ Cache Python ignorado
```

**NUNCA faça commit do arquivo .env no Git!**

### Trocar Senha Padrão

Após primeiro login:
1. Vá em **Usuários**
2. Edite o usuário `admin`
3. Altere a senha para algo seguro

## 📊 VANTAGENS DO POSTGRESQL NEON

### Antes (SQLite)
❌ Travamentos com múltiplos usuários  
❌ Dados apenas no PC local  
❌ Backup manual  
❌ Sem acesso remoto  

### Agora (PostgreSQL Neon)
✅ Acesso simultâneo sem travamentos  
✅ Dados seguros na nuvem  
✅ Backup automático  
✅ Acesso de qualquer lugar  
✅ Plano gratuito generoso (0.5 GB)  

## 🆘 SOLUÇÃO DE PROBLEMAS

### Erro: "DATABASE_URL não encontrada"
**Solução**: Verifique se o arquivo `.env` existe e contém DATABASE_URL

### Erro: "could not connect to server"
**Soluções**:
1. Verifique sua conexão com a internet
2. Confirme que a string de conexão está correta
3. Verifique se o projeto Neon está ativo

### Erro: "relation does not exist"
**Solução**: Execute `python app.py` novamente para criar as tabelas

### Erro ao migrar dados
**Solução**: 
1. Verifique se `autopecas.db` existe
2. Se não tem dados antigos, não precisa migrar
3. Comece do zero!

## 📁 ARQUIVOS MODIFICADOS

```
Autope-as-4-Irm-os/
├── .env                          # ✨ NOVO - Credenciais (não fazer commit)
├── .env.example                  # ✨ NOVO - Template de configuração
├── requirements.txt              # ✏️  MODIFICADO - Adicionado psycopg2
├── migrar_dados.py              # ✨ NOVO - Script de migração
├── Minha_autopecas_web/
│   ├── logica_banco.py          # ✏️  MODIFICADO - Agora usa PostgreSQL
│   └── logica_banco_sqlite_backup.py  # 💾 BACKUP - Código SQLite original
└── app.py                       # ✅ Sem alterações
```

## 🎯 CHECKLIST FINAL

Antes de colocar em produção:

- [ ] Projeto criado no Neon
- [ ] String de conexão configurada no `.env`
- [ ] SECRET_KEY alterada no `.env`
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Banco inicializado (primeiro `python app.py`)
- [ ] Dados migrados (se necessário)
- [ ] Login testado
- [ ] Cadastro de produto testado
- [ ] Venda realizada com sucesso
- [ ] Senha do admin alterada
- [ ] `.env` não commitado no Git

## 📞 SUPORTE

Se tiver problemas:
1. Verifique este guia novamente
2. Confira se todos os passos foram seguidos
3. Veja os logs de erro no console
4. Documente a mensagem de erro exata

---

**✅ Boa sorte com o novo sistema na nuvem! 🚀**
