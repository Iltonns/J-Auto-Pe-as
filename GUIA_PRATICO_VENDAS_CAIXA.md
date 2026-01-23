# 💼 GUIA PRÁTICO - Integração Vendas ↔ Caixa

## 📖 Índice
1. [Para Vendedores](#para-vendedores)
2. [Para Administradores](#para-administradores)
3. [Cenários de Uso](#cenários-de-uso)
4. [Troubleshooting](#troubleshooting)

---

## 👤 Para Vendedores

### Como Fazer uma Venda Normalmente

#### Passo 1: Abrir o Caixa
```
1. Acesse o menu principal
2. Clique em "Caixa"
3. Clique no botão "Abrir Caixa"
4. Defina o saldo inicial (dinheiro que você tem agora)
5. Clique em "Confirmar"
```

**Resultado**: Status muda para "CAIXA ABERTO ✓"

#### Passo 2: Acessar Vendas
```
1. Clique em "Vendas" no menu
2. A página carrega a seção "Nova Venda"
3. Se o caixa está aberto, não há avisos
```

#### Passo 3: Criar Venda à Vista

**SITUAÇÃO A**: Caixa está aberto
```
1. Selecione Cliente (ou deixe "Cliente Avulso")
2. Selecione Forma de Pagamento:
   - 💰 Dinheiro
   - 📱 PIX
   - 💳 Cartão Débito
   - 💳 Cartão Crédito

3. Busque e adicione produtos
4. Revise quantidades e preços
5. Clique em "Finalizar Venda"

✓ Venda é processada
✓ Recibo é impresso (se marcado)
✓ Movimentação registrada no caixa automaticamente
```

**SITUAÇÃO B**: Caixa está fechado
```
1. Tente selecionar Forma de Pagamento = "Dinheiro"

⚠️ ALERTA AMARELO APARECE:
   "⚠️ CAIXA FECHADO! Abra o caixa para registrar vendas à vista."

2. Botão "Finalizar Venda" fica ACINZENTADO/DESABILITADO

3. Você NÃO consegue clicar no botão

SOLUÇÃO:
   A. Abra o caixa (seção Caixa)
   B. Volte para Vendas
   C. O alerta some e o botão fica habilitado novamente
   D. Clique em "Finalizar Venda"
```

#### Passo 4: Criar Venda a Prazo (Independente do Caixa)

```
1. Selecione Cliente (OBRIGATÓRIO para prazo)
2. Selecione Forma de Pagamento = "📅 A Prazo"

✓ NÃO precisa de caixa aberto!
✓ Alerta desaparece
✓ Botão "Finalizar Venda" fica HABILITADO

3. Busque e adicione produtos
4. Revise quantidades
5. Clique em "Finalizar Venda"

✓ Venda é processada
✓ Cria automaticamente "Conta a Receber"
✓ Cliente pode pagar depois
```

### Exemplo Real de Dia de Trabalho

```
08:00 AM - Abrir Caixa
├─ Tenho R$ 500 em caixa
└─ Registro como saldo inicial

08:15 AM - Cliente chega para comprar pneu
├─ Nome: João Silva
├─ Forma de Pagamento: Dinheiro
├─ Produtos: PNEU ARRO 185/65R15 (2x R$ 180 = R$ 360)
├─ Desconto: R$ 20
├─ Total: R$ 340
└─ ✓ VENDA APROVADA (caixa aberto)

09:30 AM - Cliente chega para compra a prazo
├─ Nome: Oficina Cruz
├─ Forma de Pagamento: A Prazo
├─ Produtos: ÓLEO 5L (3x R$ 45 = R$ 135)
├─ Total: R$ 135
└─ ✓ VENDA APROVADA (a prazo não precisa de caixa)

11:00 AM - Tenta fazer venda
├─ Caixa foi fechado por engano
├─ Cliente quer pagar em dinheiro
├─ ALERTA AMARELO: "CAIXA FECHADO!"
├─ Botão desabilitado
└─ SOLUÇÃO: Abrir caixa novamente
    ├─ Vai para seção Caixa
    ├─ Clica "Abrir Caixa"
    ├─ Volta para Vendas
    └─ ✓ Venda é aprovada

18:00 PM - Fechar Caixa
├─ Sistema calcula tudo automaticamente
├─ Total de Vendas: R$ 340
├─ Saldo Inicial: R$ 500
├─ Saldo Final: R$ 840 (+ vendas)
└─ ✓ Relório completo do dia
```

---

## 👨‍💼 Para Administradores

### Monitoramento da Integração

#### Verificar Status do Caixa
```
1. Acesse "Caixa" no menu
2. Veja se está "ABERTO" ou "FECHADO"
3. Se aberto, veja:
   - Hora de abertura
   - Quem abriu
   - Saldo atual
   - Movimentações do dia
```

#### Análise de Vendas Rejeitadas
```
Se um vendedor reportar erro "CAIXA FECHADO":

1. Verifique o timestamp do erro
2. Acesse "Vendas" > "Relatórios"
3. Filtre por data/hora
4. Procure por "Erro ao registrar venda"

Investigação:
├─ Caixa estava realmente fechado?
├─ Erro foi legítimo?
├─ Vendedor tentou novamente?
└─ Venda foi processada depois?
```

#### Sincronização Vendas ↔ Caixa
```
Idealmente:
├─ Total de Entradas no Caixa = 
│  Σ(Vendas à Vista com Caixa Aberto)
└─ NÃO inclui Vendas a Prazo

Para verificar:
1. Acesse "Caixa" > "Movimentações"
2. Acesse "Vendas" > "Relatórios"
3. Compare os totais do dia

Se não correspondem:
├─ Pode haver venda a prazo no cálculo
├─ Pode haver devoluções
├─ Pode haver movimentações manuais de caixa
└─ Investigar individualmente
```

### Configurações Recomendadas

#### Permissões
```
Admin/Gerente:
├─ ✓ Abrir Caixa
├─ ✓ Fechar Caixa
├─ ✓ Fazer Vendas
├─ ✓ Visualizar Relatórios
└─ ✓ Forçar Abertura de Caixa

Vendedor:
├─ ✓ Fazer Vendas (se caixa aberto)
├─ ✗ Abrir Caixa
├─ ✗ Fechar Caixa
└─ ✓ Ver Vendas (próprias)
```

#### Horários
```
Sugestão para bom funcionamento:
├─ 08:00 AM: Abrir caixa
├─ 13:00 PM: Pausa (fechar temporariamente?)
├─ 18:00 PM: Fechar caixa (expediente)
└─ Relatório diário automático

Nota: Com a nova integração,
vendas não podem ser feitas sem caixa,
então horários são claros e controláveis
```

### Reports e Auditorias

#### Relatório Diário Recomendado
```
1. Vendas do Dia:
   ├─ Total de Vendas à Vista: R$ XXXX
   ├─ Total de Vendas a Prazo: R$ XXXX
   └─ Total Geral: R$ XXXX

2. Status do Caixa:
   ├─ Saldo Inicial: R$ XXXX
   ├─ Entradas: R$ XXXX
   ├─ Saídas: R$ XXXX
   └─ Saldo Final: R$ XXXX

3. Validação:
   ├─ Vendas à Vista = Entradas de Caixa? ✓/✗
   ├─ Estoque conferido? ✓/✗
   └─ Sem erros de processamento? ✓/✗
```

---

## 📚 Cenários de Uso

### Cenário 1: Fluxo Normal (Melhor Caso)

```
INÍCIO DO DIA
├─ 08:00 AM: Abrir caixa com R$ 500
└─ Status: ✓ ABERTO

VENDAS DO DIA
├─ 08:15 AM: Cliente A (Dinheiro) R$ 340
│  └─ ✓ Processada, caixa atualizado
├─ 09:00 AM: Cliente B (A Prazo) R$ 200
│  └─ ✓ Processada, conta a receber criada
├─ 10:30 AM: Cliente C (PIX) R$ 450
│  └─ ✓ Processada, caixa atualizado
└─ 14:00 PM: Cliente D (Cartão) R$ 320
   └─ ✓ Processada, caixa atualizado

TOTAL VENDAS: R$ 1.310
├─ À Vista: R$ 1.110
├─ A Prazo: R$ 200
└─ Caixa:
   ├─ Saldo Inicial: R$ 500
   ├─ Entradas: R$ 1.110
   ├─ Saldo Final: R$ 1.610
   └─ Tudo sincronizado ✓

FIM DO DIA
└─ 18:00 PM: Fechar caixa (tudo conferido)
```

### Cenário 2: Problema - Caixa Fechado Acidentalmente

```
10:30 AM - PROBLEMA
├─ Vendedor não percebeu que caixa estava fechado
├─ Tenta fazer venda de R$ 500 em dinheiro
└─ Sistema rejeita:
   ├─ Alerta: "⚠️ CAIXA FECHADO!"
   ├─ Botão desabilitado
   └─ Mensagem: "Abra o caixa para continuar"

SOLUÇÃO
├─ 1. Vendedor acessa "Caixa"
├─ 2. Clica "Abrir Caixa" (novamente)
├─ 3. Volta para "Vendas"
└─ 4. Tenta venda novamente
   └─ ✓ Agora é processada

OBSERVAÇÃO
└─ Sistema protegeu contra erro operacional
   └─ Nenhuma venda inconsistente foi criada
```

### Cenário 3: Venda a Prazo (Sem Dependência de Caixa)

```
14:00 PM - VENDA A PRAZO
├─ Caixa está FECHADO (por qualquer motivo)
├─ Cliente quer compra à prazo
└─ Vendedor seleciona "A Prazo"

RESULTADO
├─ Alerta desaparece
├─ Botão fica HABILITADO
├─ Venda é processada normalmente
└─ "Conta a Receber" é criada
   └─ Cliente pode pagar em 30 dias

BENEFÍCIO
├─ Negócio não para por caixa fechado
├─ Apenas vendas à vista precisam de caixa
└─ Vendas a prazo são independentes
```

### Cenário 4: Multi-Abertura de Caixa (Não Recomendado)

```
08:00 AM - Vendedor A abre caixa
├─ Saldo Inicial: R$ 1.000
└─ Status: ABERTO (Vendedor A)

11:00 AM - Vendedor B tenta abrir caixa
├─ Sistema detecta: "Já existe caixa aberto"
└─ ✗ BLOQUEADO
   └─ Solução: Fechar caixa de Vendedor A primeiro

RECOMENDAÇÃO
└─ Um caixa por turno (ou por dia)
   ├─ Todos os vendedores usam o mesmo caixa
   ├─ Mais fácil de auditoria
   └─ Evita confusão
```

---

## 🔧 Troubleshooting

### Problema 1: Alerta Não Aparece

**Sintoma**: Caixa está fechado, mas alerta não aparece

**Causas Possíveis**:
1. JavaScript desabilitado no navegador
2. Página não recarregou
3. Cache do navegador
4. Erro de conexão com `/api/caixa/status`

**Soluções**:
```
A. Recarregar Página:
   └─ Pressione F5 ou CTRL+R

B. Limpar Cache:
   ├─ CTRL+SHIFT+Delete
   └─ Marque "Cookies e dados do site"
   └─ Clique em "Limpar dados"

C. Verificar Console:
   ├─ Pressione F12
   ├─ Vá para "Console"
   ├─ Procure por erros em vermelho
   └─ Relate ao administrador se houver erros

D. Verificar API:
   ├─ Na barra de endereço, digite:
   └─ localhost:5000/api/caixa/status
   └─ Se retorna JSON, API está Ok
   └─ Se erro 500, servidor pode estar offline
```

### Problema 2: Botão Fica Desabilitado Mesmo com Caixa Aberto

**Sintoma**: Caixa está aberto, mas botão não habilita

**Causas Possíveis**:
1. Nenhum item adicionado à venda
2. JavaScript não atualizou status
3. Forma de pagamento não foi selecionada corretamente

**Soluções**:
```
A. Adicionar Itens:
   ├─ O botão só habilita quando há itens
   └─ Busque e adicione produtos

B. Mudar Forma de Pagamento:
   ├─ Selecione qualquer forma
   ├─ Depois mude para outra
   └─ Força atualização do status

C. Recarregar Página:
   ├─ F5 ou CTRL+R
   ├─ Depois tente novamente
   └─ Se persistir, contate suporte

D. Verificar Console:
   └─ F12 > Console
   └─ Procure por erros
```

### Problema 3: Venda Foi Rejeitada com "CAIXA FECHADO"

**Sintoma**: Tentou fazer venda, recebeu erro "CAIXA FECHADO"

**O que Aconteceu**:
```
1. Você tentou venda à vista (dinheiro, PIX, etc)
2. Caixa estava realmente fechado
3. Sistema bloqueou por segurança
4. Nenhuma venda foi criada ✓
```

**Solução**:
```
1. Abra o caixa:
   ├─ Acesse "Caixa"
   ├─ Clique "Abrir Caixa"
   ├─ Defina saldo inicial
   └─ Confirme

2. Volte para Vendas:
   ├─ Clique em "Vendas"
   ├─ Alerta deve desaparecer
   └─ Botão deve habilitar

3. Tente a venda novamente:
   ├─ Adicione produtos
   └─ Clique "Finalizar Venda"
   └─ ✓ Deve funcionar agora

4. Se não funcionar:
   └─ Contate administrador
   └─ Pode haver erro no servidor
```

### Problema 4: Vendedor Fecha Caixa Durante o Dia

**Sintoma**: Caixa foi fechado enquanto havia vendas a fazer

**O que Aconteceu**:
```
1. Vendedor fechou caixa acidentalmente
2. Próxima venda à vista foi rejeitada
3. Alerta aparece
```

**Solução Rápida**:
```
1. Vendedor clica em "Caixa"
2. Clica "Abrir Caixa"
3. Define saldo inicial (o saldo final anterior)
4. Volta para "Vendas"
5. Tenta venda novamente
```

**Solução Melhor** (Administrador):
```
1. Verifique porquê o caixa foi fechado
2. Se foi engano:
   ├─ Reabra o caixa normalmente
   └─ Documente o incidente

3. Se foi proposital:
   ├─ Respeite a decisão
   ├─ Planeje melhor os horários
   └─ Evite fechar no meio do expediente
```

### Problema 5: API Retorna Erro 500

**Sintoma**: Ao recarregar vendas, vê erro 500 ou 502

**Causas Prováveis**:
1. Servidor Flask offline
2. Banco de dados não conectando
3. Erro no código Python

**Soluções**:
```
A. Verificar Servidor:
   └─ Administrador verifica se Flask está rodando
      ├─ Windows: Services > Flask app
      └─ Linux: systemctl status flask_app

B. Verificar Banco de Dados:
   └─ Administrador verifica conexão PostgreSQL
      ├─ URL de conexão está correta?
      ├─ Credenciais estão certas?
      └─ Servidor está online?

C. Reiniciar Serviços:
   └─ Reinicie servidor Flask
   └─ Aguarde 1-2 minutos
   └─ Tente novamente

D. Se Persistir:
   └─ Contate suporte técnico
   └─ Forneça:
      ├─ Horário do erro
      ├─ O que estava fazendo
      └─ Logs do servidor
```

### Problema 6: Teste de Sincronização Vendas ↔ Caixa

**Verificar se está tudo sincronizado**:

```
1. Acesse "Caixa" > "Movimentações"
   └─ Anote: TOTAL ENTRADAS (ex: R$ 5.000)

2. Acesse "Vendas" > "Relatórios"
   └─ Anote: TOTAL VENDAS À VISTA (ex: R$ 5.000)

3. Compare:
   ├─ Se forem iguais: ✓ Tudo Ok!
   ├─ Se forem diferentes:
   │  ├─ Verifique se há vendas a prazo
   │  ├─ Verifique se há devoluções
   │  └─ Verifique se há movimentações manuais
   └─ Se continuar diferente, contate suporte

4. Investigação:
   ├─ Venda 1: R$ 1.000 à vista ✓
   ├─ Venda 2: R$ 2.000 a prazo (NÃO entra em caixa)
   ├─ Venda 3: R$ 2.000 à vista ✓
   └─ TOTAL CAIXA: R$ 3.000 ✓ (apenas vistas)
      └─ TOTAL VENDAS: R$ 5.000 (vistas + prazo)
      └─ Diferença de R$ 2.000 = Vendas a Prazo ✓ Ok!
```

---

## 📞 Contato e Suporte

### Quando Contatar Suporte

**Contate suporte quando**:
- [ ] Alerta não aparece mesmo após várias tentativas
- [ ] Botão não habilita sem motivo aparente
- [ ] Erro 500 ou 502 persistente
- [ ] Venda foi rejeitada mas deveria ter passado
- [ ] Caixa não abre/fecha
- [ ] Sincronização descaiar
- [ ] Outro problema não listado acima

### Informações para Fornecer

```
Ao relatar problema, inclua:

1. Descrição do Problema:
   └─ O que você estava tentando fazer?

2. Quando Aconteceu:
   └─ Horário e data exata

3. Evidência:
   ├─ Screenshot da tela
   ├─ Mensagem de erro completa
   └─ Console (F12) com erro em vermelho

4. Contexto:
   ├─ Caixa estava aberto?
   ├─ Qual forma de pagamento?
   ├─ Quantos itens na venda?
   └─ Qual tipo de venda (à vista ou prazo)?

5. Tentativas:
   ├─ Já recarregou a página?
   ├─ Já limpou o cache?
   ├─ Já tentou outro navegador?
   └─ Já reportou antes?
```

---

## ✅ Checklist - Tudo Funcionando?

Use este checklist para garantir que a integração está ok:

```
☐ Caixa abre sem erros
☐ Caixa fecha sem erros
☐ Venda à vista com caixa aberto: ✓ Funciona
☐ Venda à vista com caixa fechado: ✗ Bloqueada (esperado)
☐ Venda a prazo com caixa fechado: ✓ Funciona
☐ Alerta amarelo aparece quando apropriado
☐ Botão desabilita quando apropriado
☐ Botão habilita quando apropriado
☐ Movimentações de caixa sincronizam com vendas
☐ Estoque atualiza após venda
☐ Contas a receber criadas para vendas a prazo
☐ Console (F12) não mostra erros em vermelho
☐ API /api/caixa/status retorna JSON válido

Se todos os itens estão marcados: ✅ SISTEMA ESTÁ OK!
Se algum item não está marcado: ⚠️ CONTATE SUPORTE
```

---

**Última atualização**: 23 de Janeiro de 2026  
**Versão**: 1.0  
**Status**: ✅ Completo
