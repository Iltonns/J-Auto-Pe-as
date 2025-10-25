# 📥 Importação de Produtos via XML de NFe

## 📋 Visão Geral

A funcionalidade de **Importação de Produtos via XML** permite cadastrar automaticamente produtos no sistema usando arquivos XML de Nota Fiscal Eletrônica (NFe). Esta ferramenta extrai informações dos produtos diretamente da NFe e os adiciona ao catálogo de produtos.

## 🚀 Como Usar

### 1. Acessando a Funcionalidade
1. Navegue até a página **Produtos** no sistema
2. Clique no botão **"Importar XML"** (ícone azul ao lado de "Adicionar Produto")
3. O modal de importação será aberto

### 2. Selecionando o Arquivo XML
- Clique em **"Selecionar arquivo XML de NFe"**
- Escolha um arquivo `.xml` de uma Nota Fiscal Eletrônica
- O sistema validará automaticamente se o arquivo é um XML válido

### 3. Configurando as Opções de Importação

#### **Margem de Lucro Padrão (%)**
- Define a margem de lucro aplicada sobre o preço da NFe
- **Padrão:** 100% (duplica o preço)
- **Exemplo:** Produto custa R$ 25,00 na NFe → Preço de venda será R$ 50,00

#### **Estoque Mínimo Padrão**
- Quantidade mínima de estoque para produtos novos
- **Padrão:** 5 unidades

#### **Usar preço da NFe como base**
- ✅ **Marcado:** Usa o preço unitário da NFe como preço de custo
- ❌ **Desmarcado:** Produtos serão criados sem preço de custo definido

#### **Ação para produtos existentes**
- **Somar ao estoque atual:** Adiciona a quantidade da NFe ao estoque existente
- **Sobrescrever dados:** Substitui completamente os dados do produto
- **Ignorar produto:** Não modifica produtos que já existem

### 4. Executando a Importação
1. Clique em **"Importar Produtos"**
2. O sistema processará o arquivo XML
3. Uma mensagem de sucesso mostrará o resultado

## 📊 Dados Extraídos do XML

O sistema extrai as seguintes informações de cada produto na NFe:

| Campo XML | Descrição | Campo no Sistema |
|-----------|-----------|------------------|
| `cProd` | Código do produto | Código Fornecedor |
| `xProd` | Nome/descrição | Nome do Produto |
| `cEAN` / `cEANTrib` | Código de barras | Código de Barras |
| `NCM` | Nomenclatura Comum do Mercosul | NCM |
| `uCom` | Unidade comercial | Unidade |
| `qCom` | Quantidade | Quantidade (estoque) |
| `vUnCom` | Valor unitário | Preço de Custo |

## 🎯 Exemplo de XML Suportado

```xml
<det nItem="1">
  <prod>
    <cProd>02178BRAGS</cProd>
    <cEAN>7891252050034</cEAN>
    <xProd>RETENTOR COMANDO</xProd>
    <NCM>40169300</NCM>
    <uCom>PC</uCom>
    <qCom>5.0000</qCom>
    <vUnCom>26.1840000000</vUnCom>
    <vProd>130.92</vProd>
  </prod>
</det>
```

## ✅ Resultados da Importação

Após o processamento, você verá um relatório com:

- **Produtos importados:** Novos produtos adicionados
- **Produtos atualizados:** Produtos existentes modificados
- **Produtos ignorados:** Produtos que já existiam (dependendo da configuração)
- **Erros:** Lista de problemas encontrados durante a importação

## 📝 Exemplos de Uso

### Cenário 1: Nova Compra
- **Situação:** Você recebeu produtos de um fornecedor
- **Configuração:** 
  - Margem: 80%
  - Ação: "Somar ao estoque atual"
- **Resultado:** Produtos novos são cadastrados e estoque dos existentes é atualizado

### Cenário 2: Cadastro Inicial
- **Situação:** Primeiro cadastro de produtos de um fornecedor
- **Configuração:**
  - Margem: 100%
  - Ação: "Ignorar produto"
- **Resultado:** Apenas produtos novos são cadastrados

### Cenário 3: Atualização Completa
- **Situação:** Quer atualizar dados e preços dos produtos
- **Configuração:**
  - Margem: 90%
  - Ação: "Sobrescrever dados"
- **Resultado:** Todos os dados dos produtos são atualizados

## ⚠️ Considerações Importantes

### Formatos Suportados
- ✅ Arquivos XML de NFe (padrão nacional)
- ❌ Outros formatos XML não são suportados

### Validações
- O arquivo deve ser um XML válido
- Deve conter a estrutura padrão de NFe
- Produtos sem código ou nome são ignorados

### Categorização Automática
- O sistema tenta categorizar produtos automaticamente baseado no NCM
- Produtos sem categoria definida ficam como "Geral"

### Performance
- Arquivos grandes podem levar alguns segundos para processar
- O sistema processa até centenas de produtos por arquivo

## 🔧 Troubleshooting

### Problemas Comuns

**"Nenhum produto encontrado no XML"**
- Verifique se o arquivo é realmente uma NFe
- Confirme se contém produtos (elementos `<det>`)

**"Erro de codificação"**
- Arquivo deve estar em UTF-8
- Alguns arquivos podem ter codificação diferente

**"Produtos ignorados"**
- Produtos já existem no sistema
- Altere a ação para "Somar ao estoque" ou "Sobrescrever"

**"Margem muito baixa"**
- Verifique se a margem está configurada corretamente
- Margem 0% = mesmo preço da NFe

## 🎉 Benefícios

- ⚡ **Rapidez:** Cadastra dezenas de produtos em segundos
- 🎯 **Precisão:** Dados vêm diretamente da NFe oficial
- 🔄 **Automação:** Reduz trabalho manual e erros de digitação
- 📊 **Rastreabilidade:** Mantém códigos e informações padronizadas
- 💰 **Gestão de Preços:** Calcula automaticamente preços de venda

---

## 📞 Suporte

Se encontrar problemas ou tiver dúvidas sobre a importação XML, verifique:

1. Se o arquivo XML é de uma NFe válida
2. Se as configurações estão adequadas para seu caso
3. Se há espaço suficiente no banco de dados

A funcionalidade foi testada com NFes padrão do sistema brasileiro e é compatível com a estrutura XML oficial.