# Planejador de Base de Palworld

Projeto de estudo em Python inspirado no planejamento e na hospedagem de um servidor dedicado de Palworld. Inclui um planejador de materiais e um configurador visual em português para Windows.

> Os Pals e as receitas incluídos são exemplos fictícios para demonstrar os algoritmos. Edite os dados em `planejador_palworld.py` para montar seu próprio cenário.

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
python planejador_palworld.py
```

O exemplo padrão calcula os materiais para fabricar três unidades e recomenda trabalhadores para artesanato. Informe os materiais disponíveis usando `--inventario`:

```bash
python planejador_palworld.py --quantidade 5 --inventario madeira=6 --inventario pedra=2
```

Cada `--inventario` recebe um recurso no formato `nome=quantidade`. Para ver as opções:

```bash
python planejador_palworld.py --ajuda
```

## Exemplo de saída

```text
=== Planejador de base de Palworld ===
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

1. **Cálculo de lotes:** usa divisão com arredondamento para cima (`math.ceil`). Se uma receita produz duas unidades por lote e o jogador pede três, o programa calcula dois lotes e multiplica os materiais por dois.
2. **Cálculo de faltas:** para cada material da receita, subtrai o inventário da quantidade necessária e limita o resultado mínimo a zero.
3. **Recomendação de trabalhadores:** filtra quem tem aptidão positiva para a tarefa e ordena por nível decrescente. Em caso de empate, usa o nome em ordem alfabética para manter o resultado previsível.
4. **Separação em funções:** os cálculos ficam em funções reutilizáveis, independentes da interface de terminal, o que facilita testar e evoluir o projeto.

O GitHub Copilot pode apoiar a exploração de alternativas, a escrita de testes e a identificação de casos-limite. As sugestões devem ser revisadas e executadas antes de serem aceitas; neste projeto, os testes registram o comportamento esperado dos algoritmos.

## Configurador visual do servidor

O configurador abre uma janela com duas abas:

- **Meu PC:** selecione a pasta que contém `PalServer.exe`, configure nome, descrição, limite de jogadores, porta UDP, senhas e plataformas permitidas. Salve a configuração e inicie ou pare o servidor pela janela. Uma cópia de segurança é criada antes de substituir uma configuração existente.
- **Outra hospedagem:** exporte `PalWorldSettings.ini` e use as informações de porta, jogadores e caminho esperadas pelo seu provedor. O arquivo pode conter senhas; envie-o somente por um canal seguro.
- **Eventos:** organize uma agenda de invasões, chefes, recorrência e prêmios. O configurador avisa quando o horário chega; invocação e distribuição continuam manuais pelo mod.
- **Administração:** com a API REST ativada, consulte jogadores online, anuncie mensagens, expulse ou bane jogadores, remova banimentos, salve o mundo e agende o desligamento. Por segurança, a conexão direta do app aceita apenas localhost ou endereços IP privados.
- **Project Sphere:** abra as versões e o portal de desenvolvedor do Discord, gere um link de convite usando o Application ID criado por você, grave o token no `.env` da pasta local do bot e inicie/pare o bot pelo configurador. O token é guardado em texto nesse arquivo; não o compartilhe nem o publique. O app não cria a aplicação Discord, baixa/atualiza o código do bot nem instala suas dependências.
- **PalDefender:** a aba Administração abre a página oficial do mod e o guia de instalação. O plugin precisa ser instalado separadamente e, conforme a documentação do autor, destina-se a servidores dedicados Windows. O app ativa RCON opcionalmente para integrações compatíveis, mas não baixa nem instala o plugin.

Para abrir no Windows, dê dois cliques em `INICIAR_CONFIGURADOR.bat`. Também é possível executar no terminal:

```bash
python configurador_palworld.py
```

O programa usa o servidor dedicado Palworld instalado pela Steam. Ele não instala o jogo, não altera o Firewall do Windows nem configura o roteador. Para amigos fora da rede local, permita a porta UDP do jogo no firewall e encaminhe a mesma porta no roteador para o IP local do computador. A aba **Meu PC** mostra os endereços de rede que consegue detectar.

As plataformas selecionadas são gravadas em `CrossplayPlatforms`; o acesso entre plataformas também depende do suporte e da versão do jogo para cada plataforma. Confirme a compatibilidade antes de compartilhar o endereço do servidor.

#### Administração e hospedagem externa

A API REST e o RCON ficam desativados por padrão. Ative apenas os serviços necessários, defina uma senha administrativa forte e reinicie o servidor para aplicar as opções. A API REST oficial usa autenticação HTTP Basic sem criptografia adicional quando configurada em HTTP e a documentação recomenda não expô-la diretamente à Internet. Prefira localhost ou uma rede privada confiável e não encaminhe as portas REST/RCON no roteador. O painel integrado é destinado ao próprio computador ou à rede privada; para administração remota, prefira uma VPN ou a integração com bot, seguindo os requisitos e as permissões do provedor.

O [Project Sphere](https://github.com/projectsphere/sphere) é um bot de Discord self-hosted, não um bot público pronto para convidar. Para usá-lo, baixe uma versão publicada, crie seu próprio aplicativo/bot no Discord Developer Portal e instale as dependências do projeto (Python 3.11+), depois selecione a pasta no configurador para salvar o token e iniciar/parar o processo. O botão de convite abre a autorização do aplicativo informado, mas você deve revisar as permissões antes de adicionar o bot ao servidor Discord e configurar o servidor com os comandos do próprio Sphere. Recursos de acesso remoto por SFTP dependem da variante SFTP do Sphere e do suporte da hospedagem; o configurador não envia credenciais nem arquivos ao provedor.

O [PalDefender](https://www.nexusmods.com/palworld/mods/451) é um plugin comunitário de proteção server-side para servidor dedicado Windows. A instalação e as atualizações devem seguir as instruções oficiais e ser verificadas quanto à compatibilidade com a versão atual do Palworld. Em uma hospedagem externa, confirme primeiro se o provedor aceita plugins nativos e permite administrá-los.

### Agenda de eventos

A aba **Eventos** permite cadastrar invasões, chefes, chefes de Raid e eventos personalizados, com início, recorrência (uma vez, diária ou semanal) e prêmio planejado por participante. Os dados ficam em `%LOCALAPPDATA%\ConfiguradorPalworld\eventos.json`.

O configurador precisa permanecer aberto no computador que executa a agenda para exibir os avisos de início. A invocação do Pal/boss e a entrega do prêmio a cada participante são manuais dentro do jogo; o painel não controla o menu do mod nem distribui itens automaticamente.

Para organizar o evento dentro do jogo, use o [Creative Menu original da Oficina Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3625287786). A página do mod informa que o servidor e o jogador que utilizará o menu precisam do mod, e que o administrador deve conceder permissão para uso em multiplayer. Os demais jogadores podem entrar sem instalar o mod. Use o item original da Oficina e confira as instruções e a compatibilidade com a versão atual antes de instalar. O menu abre com **F1**; ele também pode invocar variantes Raid.

## Testes

Execute os testes automatizados com:

```bash
python -m unittest -v
```

## Estrutura

```text
.
├── planejador_palworld.py
├── test_planejador_palworld.py
├── eventos_palworld.py
├── test_eventos_palworld.py
├── palworld_admin.py
├── test_palworld_admin.py
├── test_configurador_palworld.py
├── configurador_palworld.py
├── INICIAR_CONFIGURADOR.bat
└── README.md
```
