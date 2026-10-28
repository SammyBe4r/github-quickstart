# Palworld Base Planner

Um projeto de estudo em Python, inspirado no planejamento de uma base em Palworld. O programa calcula os materiais necessários para fabricar itens e recomenda Pals para uma tarefa de acordo com seus níveis de aptidão.

> Os Pals e as receitas incluídos são exemplos fictícios para demonstrar os algoritmos. Edite os dados em `palworld_planner.py` para montar seu próprio cenário.

## Funcionalidades

- Calcula quantos lotes de uma receita são necessários para produzir a quantidade desejada.
- Compara os materiais necessários com o inventário e mostra o que ainda falta.
- Ordena os Pals por aptidão para uma tarefa, usando o nome como critério de desempate.
- Valida quantidades e argumentos inválidos com mensagens de erro claras.
- Executa sem instalar bibliotecas de terceiros.

## Requisitos

- Python 3.10 ou superior.

## Como executar

No terminal, na pasta do projeto:

```bash
python palworld_planner.py
```

O exemplo padrão calcula os materiais para fabricar três unidades e recomenda trabalhadores para artesanato. Informe os materiais disponíveis usando `--inventory`:

```bash
python palworld_planner.py --quantity 5 --inventory madeira=6 --inventory pedra=2
```

Cada `--inventory` recebe um recurso no formato `nome=quantidade`. Para ver as opções:

```bash
python palworld_planner.py --help
```

## Exemplo de saída

```text
=== Planejador de base Palworld ===
Receita: kit de construção
Unidades desejadas: 3

Materiais:
- madeira: precisa de 6, tem 0, faltam 6
- pedra: precisa de 4, tem 0, faltam 4

Pals recomendados para artesanato:
- Pal Artesão (aptidão 3)
- Pal de Transporte (aptidão 1)
```

## Algoritmos e decisões técnicas

1. **Cálculo de lotes:** usa divisão com arredondamento para cima (`ceil`). Se uma receita produz duas unidades por lote e o jogador pede três, o programa calcula dois lotes e multiplica os materiais por dois.
2. **Cálculo de faltas:** para cada material da receita, subtrai o inventário da quantidade necessária e limita o resultado mínimo a zero.
3. **Recomendação de trabalhadores:** filtra quem tem aptidão positiva para a tarefa e ordena por nível decrescente. Em caso de empate, usa o nome em ordem alfabética para manter o resultado previsível.
4. **Separação em funções:** os cálculos ficam em funções reutilizáveis, independentes da interface de terminal, o que facilita testar e evoluir o projeto.

O GitHub Copilot pode apoiar a exploração de alternativas, a escrita de testes e a identificação de casos-limite. As sugestões devem ser revisadas e executadas antes de serem aceitas; neste projeto, os testes registram o comportamento esperado dos algoritmos.

## Testes

Execute os testes automatizados com:

```bash
python -m unittest -v
```

## Estrutura

```text
.
├── palworld_planner.py
├── test_palworld_planner.py
└── README.md
```
