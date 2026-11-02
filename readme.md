# Farol — estudo com clareza

Um wireframe funcional de média fidelidade para um planejador de estudos mais gentil. Em vez de mostrar uma lista infinita de obrigações, o Farol organiza uma única página em torno de uma pergunta simples: **qual é o próximo passo possível?**

> **Desafio DIO — Psicologia aplicada e usabilidade**
> Produto fictício · Dashboard responsivo · Protótipo em HTML, CSS e JavaScript

## Visão do produto

**Problema:** planos de estudo extensos e rígidos podem transformar a aprendizagem em mais uma fonte de cobrança. A pessoa perde tempo decidindo por onde começar e pode interpretar um dia incompleto como fracasso.

**Público:** pessoas que estudam por conta própria e conciliam cursos com outras responsabilidades. O cenário apresentado é o de Marina, estudante de UX Design.

**Proposta:** oferecer uma sessão curta e pronta para começar, tornar o progresso visível sem comparação e deixar o plano flexível. A tela evita rankings, sequências punitivas e alertas de atraso.

**Objetivo principal da página:** iniciar uma sessão de estudo em poucos segundos.

**Objetivo complementar:** ajudar a pessoa a reconhecer o que já fez e escolher o que cabe no dia.

## Hierarquia e fluxo

1. **Orientação:** saudação, contexto da página e navegação familiar ajudam a pessoa a saber onde está.
2. **Próxima ação:** o cartão de foco destaca uma sessão de 25 minutos, seu tema e um botão de início.
3. **Progresso:** um resumo semanal mostra o avanço sem transformar o plano em uma cobrança.
4. **Planejamento:** tarefas podem ser marcadas ou adicionadas, deixando claro que a lista é flexível.
5. **Reforço gentil:** uma mensagem de descanso fecha a página sem adicionar outra tarefa.

O fluxo principal é **visão geral → começar sessão → pausar ou retomar → concluir**. Também é possível ajustar o plano diretamente na lista.

## Decisões de usabilidade

| Princípio | Decisão aplicada |
| --- | --- |
| Visibilidade do status do sistema — Nielsen | O cronômetro atualiza a cada segundo; pausa, conclusão e tarefas marcadas recebem feedback visual e anunciado por leitor de tela. |
| Correspondência com o mundo real — Nielsen | A interface usa palavras comuns — “próximo passo”, “feito” e “sem cobrança” — em vez de termos técnicos ou métricas abstratas. |
| Controle e liberdade — Nielsen | A sessão pode ser pausada, retomada ou encerrada; tarefas podem ser marcadas sem uma ordem obrigatória. |
| Consistência e padrões — Nielsen | Navegação lateral, estados de tarefa e botões seguem padrões reconhecíveis ao longo da tela. |
| Reconhecimento em vez de memorização — Nielsen | Tema, duração, tarefas e progresso ficam visíveis no mesmo contexto, sem exigir que a pessoa lembre de uma tela anterior. |
| Prevenção de erros — Nielsen | O cronômetro não começa sem uma ação explícita; o formulário de tarefa valida conteúdo vazio e limita o texto a 60 caracteres. |
| Carga de trabalho — Bastien & Scapin | Uma única ação principal, grupos curtos e hierarquia visual reduzem a quantidade de decisões simultâneas. |
| Controle explícito — Bastien & Scapin | Iniciar, pausar, retomar, encerrar e concluir tarefas dependem de ações deliberadas da pessoa. |
| Gestão de erros — Bastien & Scapin | O formulário identifica entradas vazias e explica como corrigi-las antes de aceitar a tarefa. |
| Significado dos códigos e denominações — Bastien & Scapin | Ícones acompanham rótulos textuais; cores reforçam estados, mas não são a única forma de comunicá-los. |

As referências são aplicadas como critérios de projeto, não como afirmação de que o protótipo já foi validado com pessoas. O próximo passo de pesquisa seria observar estudantes iniciando uma sessão e ajustando o plano, para verificar se os rótulos, a duração e o feedback são compreendidos sem ajuda.

## Interações do protótipo

- **Começar sessão:** abre o cronômetro de 25 minutos, com opções para pausar, retomar e encerrar. Ao concluir o tempo, a tarefa de foco é marcada como feita.
- **Plano de hoje:** atualizar uma caixa de seleção recalcula o total de tarefas concluídas.
- **Adicionar uma tarefa:** abre um campo com validação para texto vazio; a nova tarefa aparece na lista e pode ser marcada.
- **Notificações:** o botão anuncia que não há novidades no protótipo.
- **Navegação e acessibilidade:** links levam às seções da página; a interface inclui foco visível, atalho para pular ao conteúdo, rótulos acessíveis e suporte a preferência por movimento reduzido.

O estado é demonstrativo e não é persistido entre recargas. Notificações, perfil e seleção de semana são elementos visuais do cenário e não simulam telas ou serviços externos.

## Identidade visual

- **Paleta:** verde profundo para foco, verde-claro para progresso, fundo quente quase branco e pequenos acentos de âmbar.
- **Tipografia:** pilhas de fontes do sistema, sem download ou dependência externa.
- **Forma:** cartões com cantos suaves, espaçamento generoso e ilustração geométrica feita em CSS.
- **Responsividade:** navegação compacta em tablets e lista em coluna única em telas menores.

## Executar localmente

Não é necessário instalar dependências ou compilar o projeto. Abra `index.html` no navegador ou inicie um servidor estático na raiz do repositório:

```bash
python -m http.server 8000
```

Depois, acesse `http://localhost:8000`.

## Estrutura

| Arquivo | Conteúdo |
| --- | --- |
| `index.html` | Estrutura semântica da página e conteúdo de demonstração |
| `styles.css` | Identidade visual, estados interativos e layout responsivo |
| `script.js` | Cronômetro, atualização de tarefas e acessibilidade das interações |
| `aulas-github.md` | Conteúdo original do repositório com as aulas de Git e GitHub |

## Escopo e próximos aprendizados

Este trabalho apresenta uma página de produto, e não um sistema de estudos completo. Os dados e o perfil são ilustrativos; não há login, sincronização, armazenamento, notificações reais ou integração com cursos. Antes de evoluir o produto, seria importante testar a compreensão do cartão de foco e do resumo semanal com estudantes, incluindo navegação por teclado e leitor de tela.

---

Projeto de estudo desenvolvido para o desafio de wireframe de média fidelidade da DIO.
