"""Interface visual em português para configurar um servidor dedicado Palworld."""

from __future__ import annotations

import ipaddress
import os
import shutil
import signal
import socket
import subprocess
import tempfile
import tkinter as tk
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from eventos_palworld import (
    FREQUENCIAS,
    TIPOS_EVENTO,
    carregar_eventos,
    criar_evento,
    formatar_proxima_execucao,
    processar_agenda,
    salvar_eventos,
)


NOME_CONFIGURACAO = "PalWorldSettings.ini"
NOME_MODELO = "DefaultPalWorldSettings.ini"
CAMINHO_CONFIGURACAO = Path(
    "Pal", "Saved", "Config", "WindowsServer", NOME_CONFIGURACAO
)
PORTA_PADRAO = 8211
JOGADORES_PADRAO = 10
JOGADORES_MAXIMO = 32
PLATAFORMAS = ("Steam", "Xbox", "PS5", "Mac")
CAMINHO_EVENTOS = Path(
    os.environ.get(
        "LOCALAPPDATA",
        str(Path.home() / "AppData" / "Local"),
    ),
    "ConfiguradorPalworld",
    "eventos.json",
)
PASTAS_SERVIDOR_COMUNS = (
    Path(r"C:\SteamLibrary\steamapps\common\PalServer"),
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\PalServer"),
    Path(r"C:\Program Files\Steam\steamapps\common\PalServer"),
)


def encontrar_servidor() -> Path | None:
    """Localiza o PalServer em alguns diretórios comuns da Steam."""
    for pasta in PASTAS_SERVIDOR_COMUNS:
        if (pasta / "PalServer.exe").is_file():
            return pasta
    return None


def validar_configuracao(
    nome: str,
    quantidade_jogadores: int,
    porta: int,
    plataformas: list[str] | tuple[str, ...],
) -> None:
    if not nome.strip():
        raise ValueError("Informe um nome para o servidor.")
    if "\n" in nome or "\r" in nome or '"' in nome:
        raise ValueError("O nome não pode conter aspas nem quebras de linha.")
    if (
        isinstance(quantidade_jogadores, bool)
        or not isinstance(quantidade_jogadores, int)
        or not 1 <= quantidade_jogadores <= JOGADORES_MAXIMO
    ):
        raise ValueError(
            f"O limite de jogadores precisa estar entre 1 e {JOGADORES_MAXIMO}."
        )
    if isinstance(porta, bool) or not isinstance(porta, int) or not 1 <= porta <= 65535:
        raise ValueError("A porta UDP precisa estar entre 1 e 65535.")
    if any(plataforma not in PLATAFORMAS for plataforma in plataformas):
        raise ValueError("A lista contém uma plataforma não suportada.")


def interpretar_opcoes(linha: str) -> dict[str, str]:
    """Lê pares Opção=Valor, respeitando vírgulas entre aspas ou parênteses."""
    conteudo = linha.strip()
    prefixo = "OptionSettings=("
    if not conteudo.startswith(prefixo) or not conteudo.endswith(")"):
        raise ValueError("O modelo não contém uma linha OptionSettings válida.")

    conteudo = conteudo[len(prefixo) : -1]
    opcoes: dict[str, str] = {}
    inicio = 0
    profundidade = 0
    entre_aspas = False
    escape = False
    partes: list[str] = []

    for indice, caractere in enumerate(conteudo):
        if escape:
            escape = False
            continue
        if entre_aspas and caractere == "\\":
            escape = True
            continue
        if caractere == '"':
            entre_aspas = not entre_aspas
        elif not entre_aspas:
            if caractere == "(":
                profundidade += 1
            elif caractere == ")":
                profundidade -= 1
            elif caractere == "," and profundidade == 0:
                partes.append(conteudo[inicio:indice])
                inicio = indice + 1
    partes.append(conteudo[inicio:])

    for parte in partes:
        chave, separador, valor = parte.partition("=")
        if not separador or not chave.strip():
            raise ValueError("O modelo contém uma opção inválida.")
        opcoes[chave.strip()] = valor.strip()
    return opcoes


def carregar_opcoes_modelo(texto: str) -> tuple[str, dict[str, str]]:
    linhas = texto.splitlines()
    for indice, linha in enumerate(linhas):
        if linha.strip().startswith("OptionSettings=("):
            return "\n".join(linhas[:indice]), interpretar_opcoes(linha)
    raise ValueError("O arquivo não contém OptionSettings.")


def _formatar_texto_ini(valor: str) -> str:
    if "\n" in valor or "\r" in valor:
        raise ValueError("Os textos do servidor não podem conter quebras de linha.")
    return '"' + valor.replace("\\", "\\\\").replace('"', '\\"') + '"'


def gerar_pal_world_settings(
    modelo: str,
    *,
    nome: str,
    descricao: str,
    quantidade_jogadores: int,
    porta: int,
    senha_servidor: str,
    senha_administrador: str,
    plataformas: list[str] | tuple[str, ...],
) -> str:
    validar_configuracao(nome, quantidade_jogadores, porta, plataformas)
    if "\n" in descricao or "\r" in descricao:
        raise ValueError("A descrição não pode conter quebras de linha.")
    if any("\n" in senha or "\r" in senha for senha in (senha_servidor, senha_administrador)):
        raise ValueError("As senhas não podem conter quebras de linha.")

    cabecalho, opcoes = carregar_opcoes_modelo(modelo)
    opcoes.update(
        {
            "ServerName": _formatar_texto_ini(nome.strip()),
            "ServerDescription": _formatar_texto_ini(descricao.strip()),
            "ServerPlayerMaxNum": str(quantidade_jogadores),
            "PublicPort": str(porta),
            "ServerPassword": _formatar_texto_ini(senha_servidor),
            "AdminPassword": _formatar_texto_ini(senha_administrador),
            "bIsMultiplay": "True",
            "CrossplayPlatforms": f"({','.join(plataformas)})",
        }
    )
    linha_opcoes = "OptionSettings=(" + ",".join(
        f"{chave}={valor}" for chave, valor in opcoes.items()
    ) + ")"
    return f"{cabecalho.rstrip()}\n{linha_opcoes}\n"


def gravar_configuracao_segura(
    destino: Path, conteudo: str, *, criar_backup: bool = True
) -> Path | None:
    """Preserva uma cópia da configuração anterior e substitui o arquivo atomicamente."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    if criar_backup and destino.exists() and destino.stat().st_size:
        carimbo = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = destino.with_name(f"{destino.name}.{carimbo}.bak")
        sufixo = 1
        while backup.exists():
            backup = destino.with_name(f"{destino.name}.{carimbo}-{sufixo}.bak")
            sufixo += 1
        shutil.copy2(destino, backup)

    arquivo_temporario: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=destino.parent,
            prefix=f".{destino.name}.",
            suffix=".tmp",
            delete=False,
        ) as arquivo:
            arquivo.write(conteudo)
            arquivo_temporario = Path(arquivo.name)
        os.replace(arquivo_temporario, destino)
    except OSError:
        if arquivo_temporario is not None:
            arquivo_temporario.unlink(missing_ok=True)
        raise
    return backup


def listar_enderecos_locais() -> list[str]:
    """Retorna endereços IPv4 privados encontrados no computador."""
    enderecos: set[str] = set()
    try:
        resultados = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
    except OSError:
        return []
    for resultado in resultados:
        endereco = resultado[4][0]
        ip = ipaddress.ip_address(endereco)
        if ip.is_private and not ip.is_loopback and not ip.is_link_local:
            enderecos.add(endereco)
    return sorted(enderecos)


class ConfiguradorPalworld:
    def __init__(
        self, janela: tk.Tk, *, caminho_eventos: Path = CAMINHO_EVENTOS
    ) -> None:
        self.janela = janela
        self.janela.title("Servidor dedicado de Palworld")
        self.janela.minsize(800, 760)
        self.pasta_servidor = tk.StringVar(
            value=str(encontrar_servidor() or Path.home())
        )
        self.nome_servidor = tk.StringVar(value="Servidor dos Amigos")
        self.descricao_servidor = tk.StringVar(value="Servidor privado")
        self.quantidade_jogadores = tk.StringVar(value=str(JOGADORES_PADRAO))
        self.porta = tk.StringVar(value=str(PORTA_PADRAO))
        self.senha_servidor = tk.StringVar()
        self.senha_administrador = tk.StringVar()
        self.plataformas_ativas = {
            plataforma: tk.BooleanVar(value=True) for plataforma in PLATAFORMAS
        }
        self.status = tk.StringVar(value="Servidor parado")
        self._processo: subprocess.Popen[bytes] | None = None
        self._arquivo_log = None
        self.caminho_eventos = caminho_eventos
        try:
            self.eventos = carregar_eventos(self.caminho_eventos)
            self._agenda_disponivel = True
        except (OSError, ValueError) as erro:
            self.eventos = []
            self._agenda_disponivel = False
            messagebox.showerror("Agenda indisponível", str(erro))
        self._montar_interface()
        self.janela.protocol("WM_DELETE_WINDOW", self._ao_fechar)
        self._atualizar_enderecos()
        self._atualizar_lista_eventos()
        if self._agenda_disponivel:
            self.janela.after(10_000, self._verificar_agenda)

    def _montar_interface(self) -> None:
        raiz = ttk.Frame(self.janela, padding=16)
        raiz.pack(fill="both", expand=True)
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(2, weight=1)

        ttk.Label(
            raiz,
            text="Servidor dedicado de Palworld",
            font=("", 17, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            raiz,
            text="Configure seu servidor para até 10 amigos ou exporte os dados para outra hospedagem.",
            wraplength=700,
        ).grid(row=1, column=0, sticky="w", pady=(5, 12))

        abas = ttk.Notebook(raiz)
        abas.grid(row=2, column=0, sticky="nsew")
        aba_local = ttk.Frame(abas, padding=14)
        aba_externa = ttk.Frame(abas, padding=14)
        aba_eventos = ttk.Frame(abas, padding=14)
        abas.add(aba_local, text="Meu PC")
        abas.add(aba_externa, text="Outra hospedagem")
        abas.add(aba_eventos, text="Eventos")
        self._montar_aba_local(aba_local)
        self._montar_aba_externa(aba_externa)
        self._montar_aba_eventos(aba_eventos)

        ttk.Label(raiz, textvariable=self.status).grid(
            row=3, column=0, sticky="w", pady=(10, 0)
        )

    def _montar_aba_local(self, aba: ttk.Frame) -> None:
        aba.columnconfigure(1, weight=1)
        ttk.Label(aba, text="Pasta do servidor dedicado:").grid(
            row=0, column=0, sticky="w", pady=4
        )
        ttk.Entry(aba, textvariable=self.pasta_servidor).grid(
            row=0, column=1, sticky="ew", padx=8, pady=4
        )
        ttk.Button(aba, text="Procurar...", command=self._escolher_pasta_servidor).grid(
            row=0, column=2, pady=4
        )

        self._adicionar_campo(aba, 1, "Nome do servidor:", self.nome_servidor)
        self._adicionar_campo(aba, 2, "Descrição:", self.descricao_servidor)
        self._adicionar_campo(
            aba, 3, "Limite de jogadores (1 a 32):", self.quantidade_jogadores
        )
        self._adicionar_campo(aba, 4, "Porta do jogo (UDP):", self.porta)
        self._adicionar_campo(
            aba, 5, "Senha para entrar (opcional):", self.senha_servidor, ocultar=True
        )
        self._adicionar_campo(
            aba,
            6,
            "Senha de administrador:",
            self.senha_administrador,
            ocultar=True,
        )

        plataformas = ttk.LabelFrame(aba, text="Plataformas permitidas", padding=8)
        plataformas.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(9, 3))
        for indice, plataforma in enumerate(PLATAFORMAS):
            ttk.Checkbutton(
                plataformas,
                text=plataforma,
                variable=self.plataformas_ativas[plataforma],
            ).grid(row=0, column=indice, padx=(0, 16), sticky="w")
        ttk.Label(
            aba,
            text=(
                "A lista é gravada na configuração do jogo; o acesso entre plataformas "
                "também depende das versões e do suporte oficial do Palworld."
            ),
            wraplength=680,
        ).grid(row=8, column=0, columnspan=3, sticky="w", pady=(4, 8))

        botoes = ttk.Frame(aba)
        botoes.grid(row=9, column=0, columnspan=3, sticky="ew", pady=8)
        ttk.Button(
            botoes, text="Salvar configuração", command=self._salvar_local
        ).pack(side="left")
        ttk.Button(
            botoes, text="Iniciar servidor", command=self._iniciar_servidor
        ).pack(side="left", padx=8)
        self.botao_parar = ttk.Button(
            botoes, text="Parar servidor", command=self._parar_servidor, state="disabled"
        )
        self.botao_parar.pack(side="left")
        ttk.Button(
            botoes, text="Abrir pasta", command=self._abrir_pasta_servidor
        ).pack(side="right")

        rede = ttk.LabelFrame(aba, text="Conexão e acesso", padding=8)
        rede.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        self.texto_enderecos = tk.Text(rede, height=6, wrap="word")
        self.texto_enderecos.pack(fill="both", expand=True)
        self.texto_enderecos.configure(state="disabled")
        ttk.Button(
            rede, text="Atualizar dados de conexão", command=self._atualizar_enderecos
        ).pack(anchor="e", pady=(6, 0))

    def _montar_aba_externa(self, aba: ttk.Frame) -> None:
        aba.columnconfigure(0, weight=1)
        instrucoes = (
            "Para usar outra hospedagem, gere o arquivo PalWorldSettings.ini e envie-o "
            "pelo painel ou pelo método indicado pelo provedor.\n\n"
            "O arquivo contém o nome, o limite de jogadores, a porta, as plataformas e "
            "as senhas definidas na aba Meu PC. Trate-o como confidencial.\n\n"
            "Dados para cadastrar no provedor:\n"
            f"• Porta do jogo: {PORTA_PADRAO}/UDP (ou a porta escolhida)\n"
            "• Jogadores: limite escolhido na aba Meu PC\n"
            "• Arquivo de configuração: PalWorldSettings.ini\n\n"
            "A instalação de servidor oferecida pelo provedor pode exigir outros campos. "
            "Confirme com o suporte da hospedagem o caminho esperado para o arquivo e "
            "se ela aceita servidores dedicados de Palworld."
        )
        ttk.Label(aba, text=instrucoes, wraplength=700, justify="left").grid(
            row=0, column=0, sticky="nw", pady=(0, 16)
        )
        ttk.Button(
            aba,
            text="Exportar PalWorldSettings.ini...",
            command=self._exportar_configuracao,
        ).grid(row=1, column=0, sticky="w")

    def _montar_aba_eventos(self, aba: ttk.Frame) -> None:
        aba.columnconfigure(0, weight=1)
        aba.rowconfigure(1, weight=1)
        ttk.Label(
            aba,
            text=(
                "Cadastre invasões, chefes e outros eventos, escolha a recorrência "
                "e defina o prêmio para os participantes."
            ),
            wraplength=700,
            justify="left",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        tabela = ttk.Treeview(
            aba,
            columns=("tipo", "frequencia", "inicio", "premio", "estado"),
            show="headings",
            selectmode="browse",
            height=12,
        )
        self.tabela_eventos = tabela
        for coluna, titulo, largura in (
            ("tipo", "Tipo", 130),
            ("frequencia", "Recorrência", 105),
            ("inicio", "Próximo início", 145),
            ("premio", "Prêmio por participante", 230),
            ("estado", "Estado", 95),
        ):
            tabela.heading(coluna, text=titulo)
            tabela.column(coluna, width=largura, anchor="w")
        tabela.grid(row=1, column=0, sticky="nsew")
        barra = ttk.Scrollbar(aba, orient="vertical", command=tabela.yview)
        barra.grid(row=1, column=1, sticky="ns")
        tabela.configure(yscrollcommand=barra.set)

        botoes = ttk.Frame(aba)
        botoes.grid(row=2, column=0, sticky="ew", pady=(10, 8))
        self.botoes_eventos: list[ttk.Button] = []
        for texto, comando in (
            ("Adicionar evento", self._adicionar_evento),
            ("Editar", self._editar_evento),
            ("Ativar/Pausar", self._alternar_evento),
            ("Remover", self._remover_evento),
        ):
            botao = ttk.Button(botoes, text=texto, command=comando)
            botao.pack(side="left", padx=(0, 6))
            self.botoes_eventos.append(botao)
        if not self._agenda_disponivel:
            for botao in self.botoes_eventos:
                botao.configure(state="disabled")

        ttk.Label(
            aba,
            text=(
                "O configurador precisa permanecer aberto para mostrar os avisos. "
                "A invocação do Pal/boss e a entrega do prêmio a cada participante "
                "são manuais pelo Creative Menu (F1); o mod precisa estar instalado "
                "no servidor e no cliente, com permissão de administrador."
            ),
            wraplength=700,
            justify="left",
        ).grid(row=3, column=0, sticky="w", pady=(4, 0))

    def _salvar_eventos(self, eventos: list[dict[str, object]]) -> bool:
        try:
            salvar_eventos(self.caminho_eventos, eventos)
        except (OSError, ValueError) as erro:
            messagebox.showerror("Não foi possível salvar a agenda", str(erro))
            return False
        self.eventos = eventos
        self._atualizar_lista_eventos()
        return True

    def _atualizar_lista_eventos(self) -> None:
        if not hasattr(self, "tabela_eventos"):
            return
        for identificador in self.tabela_eventos.get_children():
            self.tabela_eventos.delete(identificador)
        for evento in self.eventos:
            estado = "Ativo" if evento["ativo"] else "Pausado/concluído"
            self.tabela_eventos.insert(
                "",
                "end",
                iid=evento["id"],
                values=(
                    evento["tipo"],
                    evento["frequencia"],
                    formatar_proxima_execucao(evento),
                    evento["premio"],
                    estado,
                ),
            )

    def _evento_selecionado(self) -> dict[str, object] | None:
        selecionados = self.tabela_eventos.selection()
        if not selecionados:
            messagebox.showinfo("Selecione um evento", "Selecione um evento na lista.")
            return None
        identificador = selecionados[0]
        return next(
            (evento for evento in self.eventos if evento["id"] == identificador),
            None,
        )

    def _adicionar_evento(self) -> None:
        self._abrir_editor_evento()

    def _editar_evento(self) -> None:
        evento = self._evento_selecionado()
        if evento is not None:
            self._abrir_editor_evento(evento)

    def _abrir_editor_evento(self, evento: dict[str, object] | None = None) -> None:
        agora = (datetime.now() + timedelta(minutes=5)).replace(second=0, microsecond=0)
        valores = evento or {
            "nome": "",
            "tipo": TIPOS_EVENTO[0],
            "inicio": agora.strftime("%Y-%m-%d %H:%M"),
            "frequencia": FREQUENCIAS[0],
            "premio": "",
            "ativo": True,
        }
        janela = tk.Toplevel(self.janela)
        janela.title("Editar evento" if evento else "Novo evento")
        janela.transient(self.janela)
        janela.grab_set()
        janela.columnconfigure(1, weight=1)

        nome = tk.StringVar(value=str(valores["nome"]))
        tipo = tk.StringVar(value=str(valores["tipo"]))
        inicio = tk.StringVar(value=str(valores["inicio"]))
        frequencia = tk.StringVar(value=str(valores["frequencia"]))
        premio = tk.StringVar(value=str(valores["premio"]))
        ativo = tk.BooleanVar(value=bool(valores["ativo"]))

        ttk.Label(janela, text="Nome do evento:").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 4)
        )
        ttk.Entry(janela, textvariable=nome, width=42).grid(
            row=0, column=1, sticky="ew", padx=(8, 12), pady=(12, 4)
        )
        ttk.Label(janela, text="Tipo:").grid(
            row=1, column=0, sticky="w", padx=12, pady=4
        )
        ttk.Combobox(
            janela, textvariable=tipo, values=TIPOS_EVENTO, state="readonly"
        ).grid(row=1, column=1, sticky="ew", padx=(8, 12), pady=4)
        ttk.Label(janela, text="Início (AAAA-MM-DD HH:MM):").grid(
            row=2, column=0, sticky="w", padx=12, pady=4
        )
        ttk.Entry(janela, textvariable=inicio).grid(
            row=2, column=1, sticky="ew", padx=(8, 12), pady=4
        )
        ttk.Label(janela, text="Recorrência:").grid(
            row=3, column=0, sticky="w", padx=12, pady=4
        )
        ttk.Combobox(
            janela, textvariable=frequencia, values=FREQUENCIAS, state="readonly"
        ).grid(row=3, column=1, sticky="ew", padx=(8, 12), pady=4)
        ttk.Label(janela, text="Prêmio por participante:").grid(
            row=4, column=0, sticky="w", padx=12, pady=4
        )
        ttk.Entry(janela, textvariable=premio).grid(
            row=4, column=1, sticky="ew", padx=(8, 12), pady=4
        )
        ttk.Checkbutton(janela, text="Evento ativo", variable=ativo).grid(
            row=5, column=1, sticky="w", padx=(8, 12), pady=4
        )

        def salvar() -> None:
            try:
                atualizado = criar_evento(
                    nome=nome.get(),
                    tipo=tipo.get(),
                    inicio=inicio.get(),
                    frequencia=frequencia.get(),
                    premio=premio.get(),
                    ativo=ativo.get(),
                    identificador=str(evento["id"]) if evento else None,
                )
            except ValueError as erro:
                messagebox.showerror("Dados inválidos", str(erro), parent=janela)
                return
            eventos = [
                atualizado if existente["id"] == atualizado["id"] else existente
                for existente in self.eventos
            ]
            if evento is None:
                eventos.append(atualizado)
            if self._salvar_eventos(eventos):
                janela.destroy()

        botoes = ttk.Frame(janela)
        botoes.grid(row=6, column=0, columnspan=2, sticky="e", padx=12, pady=12)
        ttk.Button(botoes, text="Cancelar", command=janela.destroy).pack(
            side="right", padx=(6, 0)
        )
        ttk.Button(botoes, text="Salvar", command=salvar).pack(side="right")

    def _alternar_evento(self) -> None:
        evento = self._evento_selecionado()
        if evento is None:
            return
        eventos = [
            {**existente, "ativo": not bool(existente["ativo"])}
            if existente["id"] == evento["id"]
            else existente
            for existente in self.eventos
        ]
        self._salvar_eventos(eventos)

    def _remover_evento(self) -> None:
        evento = self._evento_selecionado()
        if evento is None or not messagebox.askyesno(
            "Remover evento",
            f"Deseja remover o evento “{evento['nome']}”?",
        ):
            return
        self._salvar_eventos(
            [existente for existente in self.eventos if existente["id"] != evento["id"]]
        )

    def _verificar_agenda(self) -> None:
        eventos_atualizados, iniciados = processar_agenda(
            self.eventos, datetime.now()
        )
        if eventos_atualizados != self.eventos:
            if not self._salvar_eventos(eventos_atualizados):
                self.janela.after(10_000, self._verificar_agenda)
                return
        for evento in iniciados:
            messagebox.showinfo(
                f"Evento Palworld: {evento['nome']}",
                f"O evento “{evento['nome']}” começou.\n\n"
                f"Tipo: {evento['tipo']}\n"
                f"Prêmio planejado para cada participante: {evento['premio']}\n\n"
                "No jogo, use o Creative Menu (F1) para iniciar o evento e, "
                "ao final, entregar manualmente o prêmio a cada participante.",
            )
        self.janela.after(10_000, self._verificar_agenda)

    def _adicionar_campo(
        self,
        aba: ttk.Frame,
        linha: int,
        rotulo: str,
        variavel: tk.StringVar,
        *,
        ocultar: bool = False,
    ) -> None:
        ttk.Label(aba, text=rotulo).grid(row=linha, column=0, sticky="w", pady=4)
        ttk.Entry(
            aba,
            textvariable=variavel,
            show="*" if ocultar else "",
        ).grid(row=linha, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)

    def _escolher_pasta_servidor(self) -> None:
        pasta = filedialog.askdirectory(title="Selecione a pasta do servidor Palworld")
        if pasta:
            self.pasta_servidor.set(pasta)

    def _obter_valores(self) -> tuple[str, str, int, int, str, str, list[str]]:
        try:
            jogadores = int(self.quantidade_jogadores.get())
            porta = int(self.porta.get())
        except ValueError as erro:
            raise ValueError("O limite de jogadores e a porta precisam ser números inteiros.") from erro
        plataformas = [
            plataforma
            for plataforma in PLATAFORMAS
            if self.plataformas_ativas[plataforma].get()
        ]
        nome = self.nome_servidor.get().strip()
        validar_configuracao(nome, jogadores, porta, plataformas)
        return (
            nome,
            self.descricao_servidor.get(),
            jogadores,
            porta,
            self.senha_servidor.get(),
            self.senha_administrador.get(),
            plataformas,
        )

    def _modelo_e_base(self, pasta: Path) -> tuple[str, Path]:
        modelo_path = pasta / NOME_MODELO
        config_path = pasta / CAMINHO_CONFIGURACAO
        origem = config_path if config_path.is_file() and config_path.stat().st_size else modelo_path
        if not origem.is_file():
            raise FileNotFoundError(
                f"Não encontrei {NOME_MODELO} nem uma configuração existente em {pasta}."
            )
        return origem.read_text(encoding="utf-8-sig"), config_path

    def _criar_configuracao(self, pasta: Path) -> tuple[str, Path, int]:
        nome, descricao, jogadores, porta, senha, admin, plataformas = self._obter_valores()
        modelo, destino = self._modelo_e_base(pasta)
        conteudo = gerar_pal_world_settings(
            modelo,
            nome=nome,
            descricao=descricao,
            quantidade_jogadores=jogadores,
            porta=porta,
            senha_servidor=senha,
            senha_administrador=admin,
            plataformas=plataformas,
        )
        return conteudo, destino, porta

    def _salvar_local(self) -> bool:
        pasta = Path(self.pasta_servidor.get()).expanduser()
        if not (pasta / "PalServer.exe").is_file():
            messagebox.showerror(
                "Servidor não encontrado",
                "Selecione a pasta que contém o arquivo PalServer.exe.",
            )
            return False
        try:
            conteudo, destino, _ = self._criar_configuracao(pasta)
            backup = gravar_configuracao_segura(destino, conteudo)
        except (OSError, ValueError) as erro:
            messagebox.showerror("Não foi possível salvar", str(erro))
            return False
        self.status.set(f"Configuração salva em {destino}")
        if backup:
            self.status.set(f"Configuração salva. Cópia anterior: {backup.name}")
        return True

    def _iniciar_servidor(self) -> None:
        if self._processo is not None and self._processo.poll() is None:
            messagebox.showinfo("Servidor em execução", "O servidor já está rodando.")
            return
        pasta = Path(self.pasta_servidor.get()).expanduser()
        executavel = pasta / "PalServer.exe"
        if not executavel.is_file():
            messagebox.showerror(
                "Servidor não encontrado",
                "Selecione a pasta de instalação que contém PalServer.exe.",
            )
            return
        if not self._salvar_local():
            return
        try:
            jogadores = int(self.quantidade_jogadores.get())
            porta = int(self.porta.get())
            log_path = pasta / "ServidorPalworld.log"
            self._arquivo_log = log_path.open("ab")
            opcoes = {
                "cwd": pasta,
                "stdout": self._arquivo_log,
                "stderr": subprocess.STDOUT,
                "stdin": subprocess.DEVNULL,
            }
            if os.name == "nt":
                opcoes["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            self._processo = subprocess.Popen(
                [str(executavel), f"-port={porta}", f"-players={jogadores}"],
                **opcoes,
            )
        except (OSError, ValueError) as erro:
            if self._arquivo_log:
                self._arquivo_log.close()
                self._arquivo_log = None
            messagebox.showerror("Falha ao iniciar", str(erro))
            return
        self.status.set(
            f"Servidor iniciando na porta UDP {porta}. Registro: {log_path}"
        )
        self.botao_parar.configure(state="normal")
        self.janela.after(2000, self._verificar_processo)
        self._atualizar_enderecos()

    def _parar_servidor(self) -> None:
        processo = self._processo
        if processo is None or processo.poll() is not None:
            self._processo = None
            self.botao_parar.configure(state="disabled")
            self.status.set("Servidor parado")
            return
        if not messagebox.askyesno(
            "Parar servidor",
            "Deseja enviar o sinal de encerramento ao servidor? "
            "Aguarde a gravação do mundo antes de fechar esta janela.",
        ):
            return
        try:
            if os.name == "nt":
                processo.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                processo.send_signal(signal.SIGINT)
        except OSError as erro:
            messagebox.showerror(
                "Não foi possível parar",
                f"O sinal de encerramento não foi enviado: {erro}",
            )
            return
        self.status.set("Solicitando encerramento seguro; aguardando o servidor...")
        self.janela.after(1000, self._aguardar_encerramento, processo)

    def _aguardar_encerramento(self, processo: subprocess.Popen[bytes]) -> None:
        if processo.poll() is None:
            self.janela.after(1000, self._aguardar_encerramento, processo)
            return
        self._processo = None
        self.botao_parar.configure(state="disabled")
        self.status.set("Servidor parado")
        if self._arquivo_log:
            self._arquivo_log.close()
            self._arquivo_log = None

    def _verificar_processo(self) -> None:
        if self._processo is None:
            return
        codigo_saida = self._processo.poll()
        if codigo_saida is None:
            self.status.set("Servidor em execução")
            self.janela.after(5000, self._verificar_processo)
        else:
            self.status.set(
                f"O servidor encerrou com código {codigo_saida}. Consulte o registro."
            )
            self._processo = None
            self.botao_parar.configure(state="disabled")
            if self._arquivo_log:
                self._arquivo_log.close()
                self._arquivo_log = None

    def _atualizar_enderecos(self) -> None:
        porta = self.porta.get().strip()
        linhas = [
            "Endereço local (mesma rede Wi-Fi/roteador):",
            *(
                f"  {endereco}:{porta}"
                for endereco in listar_enderecos_locais()
            ),
        ]
        if len(linhas) == 1:
            linhas.append("  Não foi possível detectar um endereço local.")
        linhas.extend(
            [
                "",
                "Acesso pela Internet:",
                f"  IP público ou domínio: (consulte no roteador) :{porta}",
                f"  Porta do jogo: UDP {porta}",
                "",
                "Para amigos fora da rede: permita esta porta UDP no Firewall "
                "do Windows e encaminhe a mesma porta no roteador para o IP local "
                "deste PC. Nenhuma regra de rede foi alterada por este programa.",
                "Confirme a compatibilidade de crossplay com as versões do jogo "
                "dos seus amigos.",
            ]
        )
        self.texto_enderecos.configure(state="normal")
        self.texto_enderecos.delete("1.0", tk.END)
        self.texto_enderecos.insert("1.0", "\n".join(linhas))
        self.texto_enderecos.configure(state="disabled")

    def _exportar_configuracao(self) -> None:
        try:
            modelo, _ = self._modelo_e_base(
                Path(self.pasta_servidor.get()).expanduser()
            )
            valores = self._obter_valores()
            conteudo = gerar_pal_world_settings(
                modelo,
                nome=valores[0],
                descricao=valores[1],
                quantidade_jogadores=valores[2],
                porta=valores[3],
                senha_servidor=valores[4],
                senha_administrador=valores[5],
                plataformas=valores[6],
            )
        except (OSError, ValueError) as erro:
            messagebox.showerror("Configuração inválida", str(erro))
            return
        destino = filedialog.asksaveasfilename(
            title="Exportar configuração do servidor",
            initialfile=NOME_CONFIGURACAO,
            defaultextension=".ini",
            filetypes=[("Configuração INI", "*.ini")],
        )
        if not destino:
            return
        destino_path = Path(destino)
        if destino_path.exists() and not messagebox.askyesno(
            "Substituir arquivo",
            f"{destino_path.name} já existe. Deseja substituí-lo?",
        ):
            return
        try:
            backup = gravar_configuracao_segura(destino_path, conteudo)
        except OSError as erro:
            messagebox.showerror("Falha na exportação", str(erro))
            return
        mensagem = f"Configuração exportada para:\n{destino_path}"
        if backup:
            mensagem += f"\n\nCópia anterior: {backup}"
        mensagem += "\n\nO arquivo pode conter senhas; envie-o somente pelo canal seguro do provedor."
        messagebox.showinfo("Exportação concluída", mensagem)

    def _abrir_pasta_servidor(self) -> None:
        pasta = Path(self.pasta_servidor.get()).expanduser()
        if not pasta.is_dir():
            messagebox.showerror("Pasta não encontrada", f"Não existe:\n{pasta}")
            return
        os.startfile(pasta)

    def _ao_fechar(self) -> None:
        if self._processo is not None and self._processo.poll() is None:
            fechar = messagebox.askyesno(
                "Servidor em execução",
                "O servidor continuará rodando se você fechar a janela. "
                "Deseja fechar o configurador mesmo assim?",
            )
            if not fechar:
                return
        if self._arquivo_log:
            self._arquivo_log.close()
            self._arquivo_log = None
        self.janela.destroy()


def main() -> None:
    janela = tk.Tk()
    ConfiguradorPalworld(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
