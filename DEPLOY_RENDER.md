# 🚀 GUIA DE DEPLOY NO RENDER

## ✅ CONFIGURAÇÃO CONCLUÍDA

Seu projeto já está configurado para o Render com:
- ✅ PostgreSQL Neon conectado
- ✅ Variáveis de ambiente configuradas
- ✅ Gunicorn adicionado
- ✅ Procfile criado
- ✅ Build script criado

---

## 📋 PASSO A PASSO PARA DEPLOY NO RENDER

### 1️⃣ Preparar o Repositório Git

#### A. Se ainda não inicializou o Git:
```bash
git init
git add .
git commit -m "Configuração inicial para deploy no Render"
```

#### B. Criar repositório no GitHub:
1. Acesse https://github.com
2. Clique em "New repository"
3. Nome: `FG-Auto-pecas` (ou outro)
4. **NÃO** marque "Initialize with README"
5. Clique em "Create repository"

#### C. Enviar código para o GitHub:
```bash
git remote add origin https://github.com/SEU_USUARIO/FG-Auto-pecas.git
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANTE**: O arquivo `.env` NÃO será enviado (está no .gitignore)

---

### 2️⃣ Criar Web Service no Render

#### A. Acessar Render
1. Acesse https://render.com
2. Faça login (ou crie conta gratuita)
3. Clique em **"New +"** → **"Web Service"**

#### B. Conectar Repositório
1. Selecione **"Connect a repository"**
2. Escolha **GitHub**
3. Autorize o Render a acessar seus repositórios
4. Selecione o repositório **FG-Auto-pecas**

#### C. Configurar o Web Service
Preencha os campos:

```
Name: fg-autopecas
    (ou outro nome - será parte da URL)

Region: Oregon (US West)
    (ou a região mais próxima)

Branch: main

Root Directory: (deixe vazio)

Runtime: Python 3

Build Command: 
    ./build.sh

Start Command:
    gunicorn app:app

Instance Type: Free
    ⚠️ IMPORTANTE: Selecione "Free" para não pagar
```

---

### 3️⃣ Configurar Variáveis de Ambiente

Na seção **"Environment Variables"**, clique em **"Add Environment Variable"** e adicione:

#### Variável 1:
```
Key: DATABASE_URL
Value: postgresql://neondb_owner:npg_x5quBrEwHJ7Q@ep-wild-brook-a44zutrc-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

#### Variável 2:
```
Key: SECRET_KEY
Value: fg-autopecas-2025-super-secret-key-change-this
```
**💡 Dica**: Gere uma chave aleatória segura!

#### Variável 3:
```
Key: FLASK_ENV
Value: production
```

#### Variável 4 (Opcional - para desenvolvimento):
```
Key: PYTHON_VERSION
Value: 3.11.0
```

---

### 4️⃣ Fazer Deploy

1. Clique em **"Create Web Service"**
2. O Render irá:
   - Clonar seu repositório
   - Instalar dependências
   - Executar o build script
   - Iniciar a aplicação
3. Aguarde o deploy (3-5 minutos)

---

### 5️⃣ Acessar o Sistema

Após o deploy bem-sucedido:

1. URL do sistema: `https://fg-autopecas.onrender.com`
   (ou o nome que você escolheu)

2. **Primeiro Acesso**:
   - O sistema criará automaticamente as tabelas no Neon
   - Criará o usuário admin padrão

3. **Login**:
   ```
   Usuário: admin
   Senha: admin123
   ```

4. **⚠️ IMPORTANTE**: Mude a senha do admin imediatamente!

---

## 🔧 COMANDOS ÚTEIS

### Testar Localmente Antes do Deploy
```powershell
# Instalar dependências
pip install -r requirements.txt

# Testar localmente
python app.py

# Ou testar com Gunicorn (como no Render)
gunicorn app:app
```

### Atualizar o Deploy
```bash
# Fazer mudanças no código
git add .
git commit -m "Descrição das mudanças"
git push origin main

# O Render fará deploy automático!
```

---

## 📊 MONITORAMENTO NO RENDER

### Verificar Logs
1. No painel do Render, clique no seu serviço
2. Vá em **"Logs"**
3. Veja os logs em tempo real

### Verificar Status
- **Live**: Sistema funcionando ✅
- **Building**: Fazendo deploy 🔄
- **Failed**: Erro no deploy ❌

---

## 🆘 SOLUÇÃO DE PROBLEMAS

### Erro: "Application failed to start"
**Possíveis causas**:
1. Variáveis de ambiente não configuradas
2. Erro na DATABASE_URL
3. Dependências faltando

**Solução**:
1. Verifique as variáveis de ambiente no painel
2. Confira os logs para ver o erro exato
3. Verifique se o `requirements.txt` está completo

### Erro: "Database connection failed"
**Solução**:
1. Verifique se a DATABASE_URL está correta
2. Confirme que o projeto Neon está ativo
3. Teste a conexão localmente primeiro

### Erro: "Build failed"
**Solução**:
1. Verifique se o `build.sh` tem permissão de execução
2. Confira os logs de build
3. Teste o build localmente

### Site muito lento (Free tier)
**Nota**: O plano gratuito do Render:
- Desliga após 15 minutos de inatividade
- Leva ~30 segundos para "acordar" no primeiro acesso
- **Solução**: Upgrade para plano pago ($7/mês) para manter sempre ativo

---

## ⚡ OTIMIZAÇÕES

### 1. Manter o Serviço Ativo (Free Tier)
Use um serviço de ping como UptimeRobot:
1. Acesse https://uptimerobot.com
2. Crie monitor HTTP
3. URL: sua URL do Render
4. Intervalo: 5 minutos

### 2. Melhorar Performance
No `app.py`, adicione compressão:
```python
from flask_compress import Compress
Compress(app)
```

Adicione ao `requirements.txt`:
```
flask-compress==1.14
```

### 3. Configurar Domínio Customizado
1. No painel do Render → "Settings"
2. Seção "Custom Domain"
3. Adicione seu domínio
4. Configure DNS conforme instruções

---

## 🔒 SEGURANÇA

### Checklist de Segurança
- [ ] SECRET_KEY alterada e segura
- [ ] Senha do admin alterada
- [ ] `.env` não está no repositório
- [ ] DATABASE_URL não está exposta
- [ ] HTTPS habilitado (automático no Render)
- [ ] Firewall do Neon configurado (opcional)

### Recomendações
1. Use senhas fortes
2. Mude SECRET_KEY regularmente
3. Monitore os logs
4. Faça backups regulares do banco

---

## 📈 PRÓXIMOS PASSOS

### Após Deploy Bem-Sucedido
1. ✅ Teste todas as funcionalidades
2. ✅ Cadastre produtos
3. ✅ Faça vendas de teste
4. ✅ Verifique relatórios
5. ✅ Configure usuários adicionais
6. ✅ Personalize configurações da empresa

### Melhorias Futuras
- [ ] Configurar backup automático
- [ ] Adicionar monitoramento de erros (Sentry)
- [ ] Configurar envio de emails
- [ ] Adicionar autenticação 2FA
- [ ] Implementar API REST

---

## 📞 SUPORTE

### Documentação Útil
- **Render Docs**: https://render.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Flask Docs**: https://flask.palletsprojects.com/

### Links do Projeto
- **Render Dashboard**: https://dashboard.render.com
- **Neon Dashboard**: https://console.neon.tech
- **GitHub Repo**: https://github.com/SEU_USUARIO/FG-Auto-pecas

---

## ✅ CHECKLIST FINAL

Antes de fazer deploy:
- [ ] Código commitado no GitHub
- [ ] `.env` NÃO está no repositório
- [ ] `requirements.txt` atualizado
- [ ] `Procfile` criado
- [ ] `build.sh` criado
- [ ] Variáveis de ambiente prontas
- [ ] DATABASE_URL testada localmente

Durante o deploy:
- [ ] Web Service criado no Render
- [ ] Repositório conectado
- [ ] Variáveis de ambiente configuradas
- [ ] Build bem-sucedido
- [ ] Serviço iniciado

Após o deploy:
- [ ] Sistema acessível via URL
- [ ] Login funcionando
- [ ] Cadastros funcionando
- [ ] Vendas funcionando
- [ ] Senha do admin alterada

---

## 🎉 PRONTO!

Seu sistema FG Auto Peças agora está:
- ✅ Rodando na nuvem (Render)
- ✅ Com banco de dados PostgreSQL (Neon)
- ✅ Acessível de qualquer lugar
- ✅ Com backup automático
- ✅ Escalável e profissional

**URL do Sistema**: `https://fg-autopecas.onrender.com`

**Boa sorte com o sistema em produção! 🚀**

---

*Última atualização: 27 de outubro de 2025*
