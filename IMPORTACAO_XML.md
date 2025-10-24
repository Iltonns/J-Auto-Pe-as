# Funcionalidade de Importação XML - NFe

## Descrição
O sistema agora possui a capacidade de importar produtos automaticamente a partir de arquivos XML de Nota Fiscal Eletrônica (NFe).

## Como usar

### 1. Acessar a área de produtos
- Faça login no sistema
- Acesse o menu "Produtos"

### 2. Importar XML
- Clique no botão "Importar XML" 
- Selecione um arquivo XML de NFe
- Clique em "Importar Produtos"

## Dados importados

O sistema extrai automaticamente as seguintes informações do XML:

- **Nome do produto** (`xProd`)
- **Preço unitário** (`vUnCom`)
- **Quantidade** (`qCom`) - adicionada ao estoque
- **Código de barras** (`cEAN`)
- **NCM** (`NCM`) - Nomenclatura Comum do Mercosul
- **Unidade de medida** (`uCom`)

## Comportamento da importação

### Produtos novos
- Se o produto não existir no sistema, será criado automaticamente
- Todos os dados são preenchidos com base no XML

### Produtos existentes
- Se um produto já existir (mesmo código de barras), o sistema:
  - Atualiza o preço
  - Adiciona a quantidade ao estoque existente
  - Atualiza NCM e unidade

### Detecção de duplicatas
O sistema verifica duplicatas por:
1. Código de barras (EAN)
2. Código do produto
3. Nome similar

## Exemplo de XML suportado

```xml
<det nItem="1">
    <prod>
        <cProd>HT6000</cProd>
        <cEAN>7896690300277</cEAN>
        <xProd>OLEO FREIO DOT3 500ML CX/24</xProd>
        <NCM>38190000</NCM>
        <uCom>PC</uCom>
        <qCom>12.0000</qCom>
        <vUnCom>14.5650000000</vUnCom>
    </prod>
</det>
```

## Funcionalidades técnicas

### Validação
- Verifica se o arquivo é um XML válido
- Valida estrutura de NFe
- Detecta namespace correto (`http://www.portalfiscal.inf.br/nfe`)

### Tratamento de erros
- Produtos sem nome são ignorados
- Erros de produtos individuais não interrompem a importação
- Relatório detalhado de sucessos e erros

### Banco de dados
- Novas colunas adicionadas: `ncm` e `unidade`
- Compatibilidade com banco existente
- Transações seguras

## Resultados da importação

Após a importação, o sistema exibe:
- Número de produtos importados
- Número de produtos atualizados
- Lista de avisos/erros encontrados

## Arquivo de teste

Use o arquivo `teste_nfe.xml` para testar a funcionalidade com 3 produtos de exemplo.

## Melhorias futuras

- Importação de categorias automática
- Suporte a outros formatos (XML de catálogos)
- Importação de fornecedores
- Histórico de importações
- Validação de preços automática