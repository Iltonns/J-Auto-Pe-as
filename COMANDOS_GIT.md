# COMANDOS GIT PARA DEPLOY - COPIE E COLE

## 🚀 PASSO 1: INICIALIZAR REPOSITÓRIO
# Execute um comando por vez

# Inicializar Git
git init

# Adicionar todos os arquivos
git add .

# Fazer primeiro commit
git commit -m "Configuração inicial - Deploy para Render com PostgreSQL Neon"

# IMPORTANTE: Verificar se .env NÃO será enviado
git status
# Se aparecer .env na lista, NÃO CONTINUE! Verifique o .gitignore

## 🚀 PASSO 2: CRIAR REPOSITÓRIO NO GITHUB

1. Acesse: https://github.com/new
2. Nome do repositório: FG-Auto-pecas
3. NÃO marque "Initialize with README"
4. Clique em "Create repository"
5. Copie a URL que aparece (https://github.com/SEU_USUARIO/FG-Auto-pecas.git)

## 🚀 PASSO 3: CONECTAR E ENVIAR

# Adicionar repositório remoto (SUBSTITUA SEU_USUARIO)
git remote add origin https://github.com/SEU_USUARIO/FG-Auto-pecas.git

# Renomear branch para main
git branch -M main

# Enviar código para GitHub
git push -u origin main

# ✅ PRONTO! Código está no GitHub!

## 🚀 PASSO 4: RENDER (FAZER NO NAVEGADOR)

1. Acesse: https://render.com
2. Faça login ou crie conta
3. Clique em "New +" → "Web Service"
4. Clique em "Connect a repository"
5. Autorize o Render no GitHub
6. Selecione o repositório "FG-Auto-pecas"

Configure:
  Name: fg-autopecas
  Region: Oregon (US West)
  Branch: main
  Root Directory: (vazio)
  Runtime: Python 3
  Build Command: ./build.sh
  Start Command: gunicorn app:app
  Instance Type: Free ⭐

Adicione Environment Variables:

DATABASE_URL
postgresql://neondb_owner:npg_x5quBrEwHJ7Q@ep-wild-brook-a44zutrc-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require

SECRET_KEY
fg-autopecas-2025-super-secret-key-change-this

FLASK_ENV
production

7. Clique em "Create Web Service"
8. Aguarde 3-5 minutos (acompanhe os logs)

## ✅ SISTEMA NO AR!

URL: https://fg-autopecas.onrender.com

Login:
  Usuário: admin
  Senha: admin123

⚠️ MUDE A SENHA IMEDIATAMENTE!

## 🔄 PARA ATUALIZAR NO FUTURO

# Fazer mudanças no código
# Depois:

git add .
git commit -m "Descrição das mudanças"
git push origin main

# Deploy automático no Render! 🚀
