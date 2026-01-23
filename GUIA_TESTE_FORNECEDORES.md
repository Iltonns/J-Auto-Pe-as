# 🧪 GUIA DE TESTE - Sistema de Validação de Fornecedores

## 📋 Índice
1. [Testes Manuais](#testes-manuais)
2. [Testes Automáticos](#testes-automáticos)
3. [Cenários de Importação XML](#cenários-de-importação-xml)
4. [Troubleshooting](#troubleshooting)

---

## 🧪 TESTES MANUAIS

### Teste 1: Cadastrar Fornecedor Novo

**Passos:**
1. Acesse `/fornecedores`
2. Clique em "Novo Fornecedor"
3. Preencha:
   - Nome: "Empresa Teste 001"
   - CNPJ: "00.000.000/0000-00"
   - Email: "teste@empresa.com"
   - Telefone: "(11) 99999-9999"
4. Observe o feedback em tempo real

**Resultado Esperado:**
- ✅ Campos com borda verde (disponível)
- ✅ Mensagem: "Disponível"
- ✅ Botão "Salvar" ativo
- ✅ Sem alertas

---

### Teste 2: Detectar Duplicação por CNPJ

**Passos:**
1. Com o formulário aberto
2. Preencha CNPJ de um fornecedor já existente
3. Digite em outro campo (ex: nome)
4. Aguarde 500ms

**Resultado Esperado:**
- ❌ Campo CNPJ com borda vermelha (is-invalid)
- ⚠️ Alerta amarelo mostrando:
  ```
  ⚠️ DUPLICAÇÃO DETECTADA!
  Fornecedor 'Nome Existente' já cadastrado com CNPJ XX.XXX.XXX/XXXX-XX
  Critério: CNPJ
  ```
- ❌ Botão "Salvar" continua ativo (deixa usuário tentar)
- ❌ Ao clicar "Salvar", exibe: "Existe uma duplicação detectada"

---

### Teste 3: Detectar Duplicação por Email

**Passos:**
1. Abra o formulário
2. Preencha email de um fornecedor já existente
3. Digite em outro campo
4. Aguarde validação

**Resultado Esperado:**
- ❌ Campo Email com borda vermelha
- ⚠️ Alerta: "Email já cadastrado em 'Nome Fornecedor'"
- 📋 Mostra dados do fornecedor existente

---

### Teste 4: Detectar Duplicação por Nome (Fuzzy)

**Passos:**
1. Abra o formulário
2. Preencha nome similar a existente:
   - Existente: "Empresa XYZ SA"
   - Novo: "EMPRESA XYZ S.A." (89%+ similar)
3. Aguarde validação

**Resultado Esperado:**
- ❌ Alerta detecta como similar
- 📋 Mensagem: "Possível duplicação: já existe 'Empresa XYZ SA' similar (89% de similaridade)"
- 🟡 Aviso de possível duplicação

---

### Teste 5: Validação CNPJ com Diferentes Formatações

**Passos:**
1. Cadastre fornecedor com CNPJ formatado: "00.000.000/0000-00"
2. Tente cadastrar outro com mesmo CNPJ sem formatação: "00000000000000"
3. Observe validação

**Resultado Esperado:**
- ✅ Sistema detecta como duplicação (mesmo CNPJ normalizado)
- ❌ Bloqueia cadastro
- 📋 Alerta mostra CNPJ formatado do existente

---

### Teste 6: Edição de Fornecedor

**Passos:**
1. Liste fornecedores
2. Clique em editar um fornecedor existente
3. Tente alterar email para um email de outro fornecedor
4. Aguarde validação

**Resultado Esperado:**
- ❌ Detecta como duplicação
- ⚠️ Alerta amarelo
- 📋 Mostra qual fornecedor tem esse email
- ❌ Impede salvamento

---

### Teste 7: Máscaras Automáticas

**Passos:**
1. Digite CNPJ sem formatação: "00000000000000"
2. Digite Telefone: "11999999999"
3. Digite CEP: "01310100"

**Resultado Esperado:**
- ✅ CNPJ → "00.000.000/0000-00"
- ✅ Telefone → "(11) 99999-9999"
- ✅ CEP → "01310-100"

---

## 🔌 TESTES AUTOMÁTICOS (API)

### Teste A: Validar Duplicação via API

```bash
curl -X POST http://localhost:5000/fornecedores/validar-duplicacao \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "nome=Empresa Teste&cnpj=00.000.000/0000-00&email=teste@empresa.com"
```

**Resposta Esperada:**
```json
{
    "duplicado": false,
    "critério": null,
    "mensagem": "Fornecedor não encontrado no sistema",
    "fornecedor_existente": null
}
```

---

### Teste B: Buscar Fornecedor

```bash
curl -X GET "http://localhost:5000/fornecedores/buscar?q=00.000.000/0000-00"
```

**Resposta Esperada:**
```json
{
    "encontrado": true,
    "fornecedor": {
        "id": 1,
        "nome": "Empresa Teste",
        "cnpj": "00.000.000/0000-00",
        "email": "teste@empresa.com",
        "telefone": "(11) 99999-9999",
        ...
    }
}
```

---

### Teste C: Teste Unitário em Python

```python
from Minha_autopecas_web.logica_banco import validar_fornecedor_duplicado

# Teste 1: CNPJ com formatação
resultado = validar_fornecedor_duplicado(
    cnpj="00.000.000/0000-00"
)
assert resultado['duplicado'] == False, "Teste CNPJ falhou"
print("✅ Teste CNPJ: OK")

# Teste 2: Email
resultado = validar_fornecedor_duplicado(
    email="teste@empresa.com"
)
assert resultado['duplicado'] == False, "Teste Email falhou"
print("✅ Teste Email: OK")

# Teste 3: Nome fuzzy
resultado = validar_fornecedor_duplicado(
    nome="Empresa Nova LTDA"
)
print(f"✅ Teste Nome: {resultado['mensagem']}")
```

---

## 📦 CENÁRIOS DE IMPORTAÇÃO XML

### Cenário 1: Fornecedor Novo

**Arquivo XML:** 
- Emitente: "EMPRESA ABC LTDA"
- CNPJ: "00.111.222/0000-33"

**Passos:**
1. Importe o XML
2. Verifique fornecedores

**Resultado Esperado:**
- ✅ Novo fornecedor criado
- 📋 ID atribuído
- 📝 Log: "Novo fornecedor criado: EMPRESA ABC LTDA (ID: X)"
- ✅ Produtos associados ao fornecedor

---

### Cenário 2: Fornecedor Já Existe

**Situação:**
- Fornecedor "Empresa ABC" já cadastrado com CNPJ "00.111.222/0000-33"

**Passos:**
1. Importe NFe da mesma empresa
2. Verifique se duplicou

**Resultado Esperado:**
- ✅ Fornecedor NÃO duplicado
- 📋 Reutiliza fornecedor existente
- 📝 Log: "Fornecedor já existia: Empresa ABC (ID: X)"
- ✅ Produtos associados ao mesmo fornecedor

---

### Cenário 3: Fornecedor com Nome Diferente

**Situação:**
- Cadastrado: "EMPRESA ABC SA"
- NFe chega de: "Empresa ABC S.A."
- Mesmo CNPJ: "00.111.222/0000-33"

**Passos:**
1. Importe a NFe
2. Verifique resultado

**Resultado Esperado:**
- ✅ Sistema detecta como mesmo fornecedor (validação por CNPJ)
- ✅ Reutiliza fornecedor existente
- ✅ NÃO atualiza nome automaticamente (mantém consistência)
- 📝 Log: "Fornecedor já existia"

---

### Cenário 4: Email Detecta Duplicação

**Situação:**
- NFe de "Empresa XYZ" (novo nome)
- Email: "contato@empresa.com" (email já existe)

**Passos:**
1. Importe a NFe
2. Verifique validação

**Resultado Esperado:**
- ✅ Sistema detecta duplicação por email (fuzzy matching não ativa, mas email sim)
- ✅ Reutiliza fornecedor com esse email
- 📝 Log indica qual critério detectou

---

## 🐛 TROUBLESHOOTING

### Problema 1: Validação não funciona em tempo real

**Sintoma:**
- Digita CNPJ, mas não mostra feedback

**Solução:**
1. Verifique console do navegador (F12)
2. Procure por erros JavaScript
3. Verifique se endpoint `/fornecedores/validar-duplicacao` existe
4. Teste manualmente:
   ```bash
   curl -X POST http://localhost:5000/fornecedores/validar-duplicacao \
     -d "nome=Teste&cnpj=00.000.000/0000-00"
   ```

---

### Problema 2: Sempre detecta como duplicado

**Sintoma:**
- Mesmo novo fornecedor é detectado como duplicado

**Solução:**
1. Limpe banco de dados de testes:
   ```bash
   python -c "from Minha_autopecas_web.logica_banco import init_db; init_db()"
   ```
2. Verifique se há fornecedores de teste antigos
3. Inspecione a query:
   ```sql
   SELECT * FROM fornecedores WHERE nome LIKE '%Teste%';
   ```

---

### Problema 3: Fuzzy matching muito sensível

**Sintoma:**
- Detecta como similar nomes muito diferentes

**Solução:**
1. Ajuste threshold (padrão: 0.89 = 89%)
2. Edite em `validar_fornecedor_duplicado()`:
   ```python
   if similaridade >= 0.92:  # Aumentar de 0.89 para 0.92
   ```
3. Teste novamente

---

### Problema 4: Importação XML não valida fornecedor

**Sintoma:**
- Fornecedores duplicados após importar XML

**Solução:**
1. Verifique se `importar_xml_para_movimentacoes()` foi atualizado
2. Procure por:
   ```python
   resultado_fornecedor = adicionar_ou_atualizar_fornecedor_automatico(
   ```
3. Se não encontrar, significa que não foi atualizado
4. Atualizar manualmente (ver MELHORIA_FORNECEDORES.md)

---

### Problema 5: JavaScript não valida ao abrir modal

**Sintoma:**
- Abre modal de edição, mas validação não funciona

**Solução:**
1. Verifique se `setupValidacaoFornecedor()` é chamado
2. Adicione log:
   ```javascript
   console.log('Setup validação');
   ```
3. Verifique console (F12)
4. Se não aparece log, significa função não foi chamada

---

## 📊 CASOS DE TESTE RESUMIDOS

| ID | Teste | Entrada | Resultado | ✓ |
|----|-------|---------|-----------|---|
| T1 | Novo fornecedor | Nome, CNPJ, Email | Cadastrado | - |
| T2 | CNPJ duplicado | CNPJ existente | Bloqueado | - |
| T3 | Email duplicado | Email existente | Bloqueado | - |
| T4 | Nome similar | Nome 89%+ similar | Alerta | - |
| T5 | CNPJ variações | "00.000.000/0000-00" vs "00000000000000" | Detecta | - |
| T6 | Editar validado | Alterar para email duplicado | Bloqueado | - |
| T7 | Máscaras | Dados brutos | Formatados | - |
| A1 | API validação | POST com dados | JSON resposta | - |
| A2 | API busca | GET com query | JSON + dados | - |
| A3 | Teste unitário | Python direto | OK/ERRO | - |
| X1 | XML novo | NFe novo fornecedor | Criado | - |
| X2 | XML existente | NFe fornecedor ativo | Reutilizado | - |
| X3 | XML variação | NFe nome diferente | Detectado | - |
| X4 | XML email | NFe email duplicado | Reutilizado | - |

---

## ✅ CHECKLIST FINAL

Antes de considerar completo, teste:

- [ ] Cadastro manual funciona sem erros
- [ ] Validação em tempo real mostra feedback
- [ ] Duplicação por CNPJ é detectada
- [ ] Duplicação por Email é detectada
- [ ] Nomes similares geram alerta
- [ ] Edição valida corretamente
- [ ] Máscaras funcionam (CNPJ, Telefone, CEP)
- [ ] Importação XML não duplica
- [ ] Endpoints REST respondem
- [ ] Sem erros no console JavaScript
- [ ] Sem erros no log Python
- [ ] Fuzzy matching funciona
- [ ] Performance < 1s

---

## 📞 SUPORTE

Se encontrar problema:

1. Verifique os logs:
   ```bash
   # Terminal
   python app.py 2>&1 | grep -i "erro\|debug\|fornecedor"
   ```

2. Verifique console navegador (F12)

3. Execute testes unitários:
   ```python
   python -c "from Minha_autopecas_web.logica_banco import validar_fornecedor_duplicado; print(validar_fornecedor_duplicado())"
   ```

4. Consulte `MELHORIA_FORNECEDORES.md` para detalhes técnicos

---

**FIM DO GUIA DE TESTE** ✅

*Última atualização: 23 de Janeiro de 2026*
