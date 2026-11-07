# Nona — pizza feita com tempo

Protótipo de alta fidelidade para um aplicativo de pedidos de uma pizzaria artesanal fictícia em São Paulo. O projeto exercita briefing, arquitetura da informação, linguagem visual, usabilidade, prototipagem e estimativa de custos em uma interface real e navegável.

**[Abrir o protótipo](./index.html)** · Projeto demonstrativo, sem backend, cadastro real ou pagamento.

## 1. Briefing

| Item | Definição |
|---|---|
| Cliente | Nona, pizzaria artesanal fictícia da Vila Madalena, São Paulo |
| Problema | A experiência de pedir pelo celular costuma ser confusa: cardápios extensos, custos pouco claros e etapas demais antes de confirmar |
| Objetivo | Ajudar a pessoa a encontrar um sabor, entender o preço final e concluir um pedido de demonstração com segurança |
| Público principal | Pessoas de 20 a 40 anos que pedem jantar em casa, usam o celular e valorizam comida artesanal e praticidade |
| Proposta de valor | Pizza de fermentação longa com a clareza e a conveniência de um pedido simples |
| Plataforma | Web responsiva, com prioridade para celular |
| Escopo do protótipo | Cardápio, categorias, busca, sacola, quantidades, endereço, cupom, resumo de valores e confirmação fictícia |
| Fora do escopo | Autenticação, integração com restaurante, pagamento, mapa, rastreamento e persistência de pedidos |

### Hipótese de design

Se mostrarmos os produtos e o preço final com clareza, permitirmos ajustar o pedido sem perder o contexto e mantivermos a finalização curta, mais pessoas conseguirão chegar à confirmação sem dúvidas.

### Personas

- **Marina, 28 — “quero decidir sem abrir dez telas”**: pede pelo celular depois do trabalho; precisa comparar sabores e conferir taxa e total antes de seguir.
- **Rafael, 36 — “pedido para dividir”**: escolhe comida para duas ou mais pessoas; precisa alterar quantidades e encontrar uma combinação rapidamente.

### Critérios de sucesso a validar

- Encontrar um item usando categoria ou busca em até 30 segundos.
- Adicionar, remover e alterar quantidades diretamente na experiência de cardápio/sacola.
- Identificar subtotal, entrega, desconto e total antes de abrir o formulário.
- Concluir a tarefa de demonstração sem ajuda em um teste moderado com 5 participantes.

Os números são metas para um teste futuro, não resultados medidos.

## 2. Arquitetura e fluxo

**Fluxo principal:** abrir cardápio → explorar categoria ou buscar → adicionar item → revisar sacola e valores → informar endereço → preencher nome e forma de pagamento → ver confirmação.

**Fluxos alternativos:** ajustar quantidade; aplicar/remover o cupom `NONA10` (10% de desconto, até R$ 15, em pedidos a partir de R$ 50); editar endereço; fechar a sacola e continuar explorando.

### Wireframe estrutural

```text
┌──────────────────── Marca · endereço · perfil ────────────────────┐
│ Banner: proposta de valor · CTA · prazo · avaliação                │
├─────────────────────────────────┬─────────────────────────────────┤
│ Título · busca                  │ Sacola · endereço                │
│ Categorias                      │ Itens · quantidades              │
│ Produtos em cards               │ Cupom · subtotal · entrega        │
│                                 │ Total · continuar                │
└─────────────────────────────────┴─────────────────────────────────┘
```

Em telas estreitas, a sacola vira uma folha inferior acionada pelo botão fixo “Ver sacola”, mantendo o catálogo visível durante a escolha.

## 3. Guideline / Design System

### Direção visual

Uma trattoria contemporânea: tons de papel, verde-oliva e terracota, fotografia quente e títulos serifados. O tom de voz é próximo e apetitoso, mas a interface de preços e ações é direta.

### Tokens principais

| Token | Valor | Uso |
|---|---|---|
| Papel | `#F8F6F1` | Fundo |
| Superfície | `#FFFEFA` | Cards e sacola |
| Tinta | `#252921` | Texto principal |
| Oliva | `#475B39` | Ação primária e seleção |
| Terracota | `#CF684D` | Destaques pontuais |
| Linha | `#E9E7DF` | Divisórias e bordas |
| Títulos | Playfair Display | Identidade e hierarquia |
| Interface | DM Sans | Corpo, controles e números |

### Componentes e comportamento

- Botão primário oliva; estados indisponíveis com contraste reduzido e ação desabilitada.
- Chips de categoria com estado selecionado persistente e exposto por `aria-pressed`.
- Cards com foto, nome, descrição, preço, avaliação e ação explícita de adicionar.
- Sacola recalcula quantidade, subtotal, entrega grátis acima de R$ 80, cupom e total.
- Busca também pode ser focada pelo atalho `/`; diálogos podem ser fechados com `Esc`.
- Layout responsivo, rótulos acessíveis, mensagens em regiões `aria-live` e preferência por movimento reduzido.

## 4. Protótipo e validação

O protótipo executável está em `index.html`; não exige instalação nem ferramentas de build. Abra o arquivo no navegador. As imagens e fontes são carregadas de serviços externos, então a conexão com a internet melhora a apresentação; os fluxos funcionam localmente sem servidor.

### Roteiro rápido de teste

1. Filtre por “Pizzas” e localize a Margherita; depois teste uma busca por “limonada”.
2. Adicione uma pizza e uma bebida; confira subtotal, taxa e total.
3. Use o cupom `NONA10` com subtotal acima de R$ 50; confira o desconto e experimente um código inválido.
4. Aumente e diminua a quantidade de um item; verifique os valores.
5. Edite o endereço e finalize o pedido de demonstração; confira a tela de confirmação.
6. Repita os passos principais em largura móvel e com navegação por teclado.

O protótipo não envia dados, salva pedidos nem processa pagamentos.

### Próxima etapa em Figma

Este repositório entrega a interface como protótipo web funcional. Para apresentar também um arquivo nativo do Figma, recrie os tokens e componentes documentados e ligue os frames na ordem do fluxo principal acima. Não há arquivo `.fig` incluído nesta entrega.

## 5. Orçamento estimado

Estimativa ilustrativa para um projeto de design com escopo semelhante, em reais (BRL):

| Etapa | Horas | Valor/hora | Total |
|---|---:|---:|---:|
| Briefing e alinhamento | 6 h | R$ 120 | R$ 720 |
| Arquitetura e wireframes | 8 h | R$ 120 | R$ 960 |
| Direção visual e design system | 12 h | R$ 135 | R$ 1.620 |
| Telas de alta fidelidade e responsividade | 14 h | R$ 135 | R$ 1.890 |
| Protótipo interativo | 10 h | R$ 135 | R$ 1.350 |
| Teste moderado e entrega | 6 h | R$ 120 | R$ 720 |
| **Subtotal** | **56 h** |  | **R$ 7.260** |
| Reserva para ajustes (10%) |  |  | R$ 726 |
| **Investimento estimado** |  |  | **R$ 7.986** |

**Prazo estimado:** 3 semanas, contando com retorno do cliente em até 2 dias úteis por rodada. O orçamento é uma simulação acadêmica, válido por 30 dias a partir de uma proposta comercial hipotética. Não inclui desenvolvimento de backend, integrações, taxas, impostos, licenças de ferramentas, produção fotográfica ou rodadas extras além do escopo.

## 6. Como executar

1. Clone ou baixe o repositório.
2. Abra `prototipo/index.html` em um navegador moderno.
3. Não é necessário instalar dependências.

## Créditos e ressalvas

Marca, restaurante, preços, endereço, clientes e avaliações são fictícios. Fotografias e fontes são referenciadas por URLs de terceiros para fins demonstrativos; substitua-as por ativos licenciados antes de uso comercial. Não confundir as avaliações ilustrativas da interface com dados reais.
