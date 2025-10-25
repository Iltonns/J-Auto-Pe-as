# 🔧 GUIA DE TESTES - Sistema de Autopeças

## ✅ Preparação Concluída:
- ✅ Todos os produtos antigos foram removidos do banco de dados
- ✅ 3 produtos de teste foram adicionados:
  1. Vela de Ignição NGK - Teste 1 (R$ 30,00)
  2. Filtro de Óleo Mann - Teste 2 (R$ 45,00) 
  3. Pastilha de Freio Bosch - Teste 3 (R$ 72,00)
- ✅ Servidor Flask rodando em http://127.0.0.1:5000
- ✅ Arquivo XML de teste criado: `teste_nfe.xml`

## 🧪 TESTES A REALIZAR:

### 1. 🔍 TESTE DE BUSCA DE PRODUTOS
**URL:** http://127.0.0.1:5000/produtos

**Como testar:**
1. Acesse a página de produtos
2. Digite no campo de busca: "vela", "ngk", "filtro", etc.
3. Verifique se a busca funciona em tempo real
4. Teste os atalhos: Ctrl+F, Esc para limpar

**✅ Resultado esperado:** Busca em tempo real funcionando

---

### 2. ✏️ TESTE DE EDITAR PRODUTO
**Como testar:**
1. Na página de produtos, clique no botão "Editar" (ícone lápis) de qualquer produto
2. Verifique se os campos são preenchidos corretamente
3. Altere a margem de lucro (ex: de 100% para 50%)
4. Verifique se o preço é recalculado automaticamente
5. Altere o nome do produto
6. Clique em "Atualizar Produto"

**✅ Resultado esperado:** 
- Campos preenchidos corretamente
- Cálculo automático do preço funcionando
- Produto atualizado com sucesso

---

### 3. 🗑️ TESTE DE DELETAR PRODUTO
**Como testar:**
1. Na página de produtos, clique no botão "Deletar" (ícone lixeira) de qualquer produto
2. Confirme a exclusão
3. Verifique se o produto desaparece da lista

**✅ Resultado esperado:** 
- Confirmação de exclusão aparece
- Produto é removido da lista
- Mensagem de sucesso

---

### 4. 📁 TESTE DE IMPORTAÇÃO XML
**Como testar:**
1. Na página de produtos, clique em "Importar XML"
2. Selecione o arquivo `teste_nfe.xml` criado
3. Clique em "Importar Produtos"
4. Verifique se os produtos do XML foram importados

**✅ Resultado esperado:**
- 5 novos produtos importados do XML
- Produtos aparecem na lista com informações corretas

---

### 5. 🛒 TESTE DA ÁREA DE VENDAS
**URL:** http://127.0.0.1:5000/vendas

**Como testar:**
1. Acesse a área de vendas
2. Tente adicionar produtos ao carrinho
3. Verifique se aparecem erros relacionados aos produtos

**⚠️ Objetivo:** Identificar onde está o erro que afeta a área de vendas

---

### 6. 🗑️ TESTE DE DELETAR TODOS OS PRODUTOS (Interface Web)
**Como testar:**
1. Na página de produtos, clique em "Deletar Todos" (botão vermelho)
2. Confirme as duas confirmações
3. Verifique se todos os produtos são removidos

**✅ Resultado esperado:** Todos os produtos removidos

---

## 🐛 ERROS ESPERADOS PARA INVESTIGAR:

### Na área de vendas, podem ocorrer:
- ❌ Produtos não carregam no seletor
- ❌ Erro ao calcular preços
- ❌ Problemas com estoque
- ❌ Campos não preenchidos corretamente

### Possíveis causas identificadas:
1. **Problema no preenchimento de campos de edição** ✅ CORRIGIDO
2. **Problema no cálculo automático de preços** ✅ CORRIGIDO  
3. **Problema na função de deletar** ✅ CORRIGIDO
4. **Possível incompatibilidade entre dados antigos e novos** ✅ RESOLVIDO (banco limpo)

---

## 📋 CHECKLIST DE TESTE:

- [ ] Busca de produtos funciona
- [ ] Edição de produtos funciona (campos preenchidos)
- [ ] Cálculo automático de margem funciona
- [ ] Deletar produto individual funciona
- [ ] Importação XML funciona
- [ ] Deletar todos os produtos funciona
- [ ] Área de vendas funciona sem erros
- [ ] Adicionar novos produtos funciona

---

## 📞 SUPORTE:

Se encontrar algum erro:
1. Abra o console do navegador (F12)
2. Verifique mensagens de erro no console
3. Teste cada funcionalidade individualmente
4. Relate qual teste específico falhou

**Status atual:** 🟢 Sistema pronto para testes com dados limpos