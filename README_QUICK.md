# ⚡ QUICK START - PostgreSQL Neon

## 🎯 PASSO A PASSO RÁPIDO

### 1️⃣ No Neon (https://neon.tech)
```
1. Criar novo projeto
2. Copiar connection string (postgresql://...)
```

### 2️⃣ No arquivo .env
```env
DATABASE_URL=postgresql://[COLE_AQUI]
SECRET_KEY=troque-por-algo-aleatorio
```

### 3️⃣ No PowerShell
```powershell
# Instalar dependências
pip install -r requirements.txt

# Iniciar sistema
python app.py
```

### 4️⃣ Acessar
```
http://localhost:5000
Login: admin / admin123
```

---

## 📝 O QUE FOI ALTERADO

### ✅ Arquivos Criados
- `.env` - Configurações sensíveis (NÃO COMMITAR)
- `.env.example` - Template de configuração
- `migrar_dados.py` - Script de migração opcional
- `GUIA_MIGRACAO_NEON.md` - Guia completo
- `Minha_autopecas_web/logica_banco_sqlite_backup.py` - Backup do código original

### ✏️ Arquivos Modificados
- `requirements.txt` - Adicionado psycopg2-binary e python-dotenv
- `Minha_autopecas_web/logica_banco.py` - Convertido para PostgreSQL

### 🔧 Principais Mudanças Técnicas
```python
# ANTES (SQLite)
import sqlite3
conn = sqlite3.connect('autopecas.db')
cursor.execute("INSERT ... VALUES (?, ?, ?)")
id = cursor.lastrowid

# AGORA (PostgreSQL)
import psycopg2
from dotenv import load_dotenv
conn = psycopg2.connect(DATABASE_URL)
cursor.execute("INSERT ... VALUES (%s, %s, %s) RETURNING id")
id = cursor.fetchone()[0]
```

### 🔀 Conversões SQL
- `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
- `?` (placeholders) → `%s`
- `BOOLEAN DEFAULT 1/0` → `BOOLEAN DEFAULT TRUE/FALSE`
- `REAL` → `DECIMAL(10,2)`
- `cursor.lastrowid` → `cursor.fetchone()[0]` + `RETURNING id`

---

## ⚠️ IMPORTANTE

### Antes de Iniciar
```powershell
# 1. Configurar .env com suas credenciais do Neon
# 2. Instalar dependências
pip install -r requirements.txt
```

### Erros Comuns

**"DATABASE_URL não encontrada"**
→ Configure o arquivo `.env` com a string do Neon

**"Não foi possível resolver a importação dotenv"**  
→ Execute: `pip install python-dotenv`

**"could not connect to server"**
→ Verifique conexão de internet e string do Neon

---

## 💾 Migração de Dados (Opcional)

Se você tem dados no SQLite antigo:
```powershell
python migrar_dados.py
```

Se está começando do zero: **PULE ESTE PASSO!**

---

## 📊 Benefícios

| Antes (SQLite) | Agora (PostgreSQL Neon) |
|---|---|
| ❌ Dados apenas no PC | ✅ Dados na nuvem |
| ❌ Travamentos frequentes | ✅ Acesso simultâneo real |
| ❌ Sem backup | ✅ Backup automático |
| ❌ Acesso local apenas | ✅ Acesso de qualquer lugar |
| ❌ Escalabilidade limitada | ✅ Escalável conforme necessário |

---

## 📂 Estrutura de Arquivos

```
Autope-as-4-Irm-os/
├── .env                    # ⚙️  Configurações (NÃO COMMITAR!)
├── .env.example            # 📝 Template de configuração
├── requirements.txt        # 📦 Dependências Python
├── migrar_dados.py         # 🔄 Migração SQLite→PostgreSQL
├── GUIA_MIGRACAO_NEON.md   # 📖 Guia completo
├── README_QUICK.md         # ⚡ Este arquivo
├── app.py                  # 🚀 Aplicação Flask
└── Minha_autopecas_web/
    ├── logica_banco.py                  # 🗄️  Lógica PostgreSQL
    └── logica_banco_sqlite_backup.py    # 💾 Backup SQLite original
```

---

## ✅ Checklist Final

- [ ] Projeto criado no Neon
- [ ] `.env` configurado com DATABASE_URL
- [ ] SECRET_KEY alterado
- [ ] `pip install -r requirements.txt` executado
- [ ] Sistema iniciado com `python app.py`
- [ ] Login testado (admin/admin123)
- [ ] Cadastro testado
- [ ] Venda testada

---

**🎉 Pronto! Sistema agora roda em PostgreSQL na nuvem!**

Qualquer dúvida, consulte o `GUIA_MIGRACAO_NEON.md` para detalhes completos.
