# Fotos dos Produtos

Esta pasta contém as fotos dos produtos cadastrados no sistema.

## Configuração Automática

As fotos são automaticamente gerenciadas pelo sistema:

- **Upload**: Quando você adiciona ou edita um produto, pode selecionar uma foto
- **Formatos aceitos**: PNG, JPG, JPEG, GIF
- **Tamanho máximo**: 5MB por foto
- **Nomenclatura**: O sistema gera automaticamente nomes únicos para evitar conflitos

## Estrutura de Armazenamento

```
static/images/produtos/
├── abc123_foto1.jpg
├── def456_foto2.png
└── ghi789_foto3.jpeg
```

## Como Funciona

1. **Novo Produto**: 
   - Vá na aba "Foto da Peça" no modal de novo produto
   - Selecione uma imagem do seu computador
   - A pré-visualização será exibida
   - A foto será salva quando o produto for criado

2. **Editar Produto**:
   - Na aba "Foto da Peça" do modal de edição
   - Veja a foto atual (se existir)
   - Selecione nova foto para substituir
   - Ou marque "Remover foto atual" para excluir

3. **Exclusão Automática**:
   - Fotos são removidas automaticamente quando você:
     - Substitui por uma nova foto
     - Marca para remover a foto
     - Exclui o produto (implementação futura)

## Dicas para Melhores Fotos

- Use boa iluminação
- Mantenha o fundo limpo e neutro
- Fotografe a peça de ângulos que mostrem detalhes importantes
- Certifique-se de que códigos e números estejam legíveis
- Evite reflexos e sombras excessivas