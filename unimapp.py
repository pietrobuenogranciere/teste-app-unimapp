
"""UNIMAPP - protótipo acadêmico da UNIMAR.
auxílio de IA para o descobrimento dos comandos (pack, json, path)
Tela de login + área de estudos com navegação
"""
import json
import os
import tkinter as tk

try:
    from PIL import Image, ImageTk
    PIL_DISPONIVEL = True
except ImportError:
    PIL_DISPONIVEL = False

AZUL = "#0072BC"
AZUL_ESCURO = "#005A96"
AZUL_MUITO_ESCURO = "#083B66"
AZUL_CLARO = "#EAF5FC"
BRANCO = "#FFFFFF"
FUNDO = "#F5F8FB"
TEXTO = "#183247"
TEXTO_SEC = "#6B7C8D"
BORDA = "#DCE7EF"
VERDE = "#16803C"
VERMELHO = "#B00020"

ARQUIVO_USUARIOS = "usuarios.json"
PASTA_ASSETS = "assets"
ARQUIVO_CAMPUS = os.path.join(PASTA_ASSETS, "campus_unimar.jpg")
ARQUIVO_LOGO = os.path.join(PASTA_ASSETS, "unimar_logo.png")


def carregar_usuarios():
    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "aluno": {
                "senha": "1234",
                "tipo": "Aluno",
                "curso": "Projeto Jovem Programador",
            }
        }


def salvar_usuarios():
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=4)


def limpar_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def criar_botao(parent, texto, comando, largura=18, destaque=False):
    return tk.Button(
        parent,
        text=texto,
        command=comando,
        width=largura,
        bg=AZUL if destaque else BRANCO,
        fg=BRANCO if destaque else AZUL_ESCURO,
        activebackground=AZUL_ESCURO if destaque else AZUL_CLARO,
        activeforeground=BRANCO if destaque else AZUL_ESCURO,
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Arial", 10, "bold"),
        padx=12,
        pady=9,
    )


usuarios = carregar_usuarios()
usuario_atual = None
conteudo = None


def criar_tela_login():
    limpar_frame(janela)
    janela.configure(bg=FUNDO)

    esquerda = tk.Frame(janela, bg=AZUL_MUITO_ESCURO, width=650)
    esquerda.pack(side="left", fill="both", expand=True)

    canvas = tk.Canvas(esquerda, bg=AZUL_MUITO_ESCURO, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def desenhar_fallback(event=None):
        canvas.delete("all")
        w = max(1, canvas.winfo_width())
        h = max(1, canvas.winfo_height())

        faixas = ["#083B66", "#07538A", "#086AA7", "#0877B7"]
        largura = max(1, w // len(faixas))

        for i, cor in enumerate(faixas):
            canvas.create_rectangle(
                i * largura,
                0,
                (i + 1) * largura + 2,
                h,
                fill=cor,
                outline=cor,
            )

        base = h * 0.68
        canvas.create_polygon(
            w * 0.08,
            base,
            w * 0.50,
            base - 80,
            w * 0.92,
            base,
            fill="#EAF5FC",
            outline="",
        )
        canvas.create_rectangle(
            w * 0.12,
            base,
            w * 0.88,
            h * 0.88,
            fill="#F7FBFF",
            outline="",
        )

        for x in [w * 0.20, w * 0.31, w * 0.42, w * 0.53, w * 0.64, w * 0.75]:
            canvas.create_rectangle(
                x,
                base + 25,
                x + 34,
                h * 0.88,
                fill="#D8E6EF",
                outline="",
            )

        canvas.create_text(
            w * 0.10,
            h * 0.12,
            anchor="nw",
            text="UNIMAPP",
            fill=BRANCO,
            font=("Arial", 34, "bold"),
        )
        canvas.create_text(
            w * 0.10,
            h * 0.20,
            anchor="nw",
            text="Seu espaço acadêmico em um só lugar.",
            fill="#D6EEFC",
            font=("Arial", 13),
        )
        canvas.create_text(
            w * 0.10,
            h * 0.92,
            anchor="sw",
            text="UNIVERSIDADE DE MARÍLIA • PROJETO ACADÊMICO",
            fill="#C7E4F5",
            font=("Arial", 9, "bold"),
        )

    canvas.bind("<Configure>", desenhar_fallback)

    if PIL_DISPONIVEL and os.path.exists(ARQUIVO_CAMPUS):
        try:
            imagem = Image.open(ARQUIVO_CAMPUS).convert("RGB")

            def atualizar_foto(event=None):
                w = max(1, canvas.winfo_width())
                h = max(1, canvas.winfo_height())

                proporcao = max(w / imagem.width, h / imagem.height)
                tamanho = (
                    int(imagem.width * proporcao),
                    int(imagem.height * proporcao),
                )

                foto = imagem.resize(tamanho, Image.Resampling.LANCZOS)

                esquerda_corte = max(0, (foto.width - w) // 2)
                topo_corte = max(0, (foto.height - h) // 2)

                foto = foto.crop(
                    (
                        esquerda_corte,
                        topo_corte,
                        esquerda_corte + w,
                        topo_corte + h,
                    )
                )

                janela.foto_campus = ImageTk.PhotoImage(foto)

                canvas.delete("all")
                canvas.create_image(
                    0,
                    0,
                    image=janela.foto_campus,
                    anchor="nw",
                )
                canvas.create_rectangle(
                    0,
                    0,
                    w,
                    h,
                    fill=AZUL_MUITO_ESCURO,
                    stipple="gray50",
                    outline="",
                )
                canvas.create_text(
                    55,
                    55,
                    anchor="nw",
                    text="UNIMAPP",
                    fill=BRANCO,
                    font=("Arial", 34, "bold"),
                )
                canvas.create_text(
                    55,
                    105,
                    anchor="nw",
                    text="Seu espaço acadêmico em um só lugar.",
                    fill="#E0F2FF",
                    font=("Arial", 13),
                )
                canvas.create_text(
                    55,
                    h - 35,
                    anchor="sw",
                    text="UNIVERSIDADE DE MARÍLIA • PROJETO ACADÊMICO",
                    fill="#E0F2FF",
                    font=("Arial", 9, "bold"),
                )

            canvas.bind("<Configure>", atualizar_foto)
            atualizar_foto()
        except Exception:
            pass

    direita = tk.Frame(janela, bg=BRANCO, width=530)
    direita.pack(side="right", fill="both", expand=True)

    painel = tk.Frame(direita, bg=BRANCO)
    painel.pack(expand=True, padx=60, pady=35)

    logo_ok = False

    if os.path.exists(ARQUIVO_LOGO):
        try:
            if PIL_DISPONIVEL:
                logo = Image.open(ARQUIVO_LOGO).convert("RGBA")
                logo.thumbnail((250, 90), Image.Resampling.LANCZOS)
                janela.logo_login = ImageTk.PhotoImage(logo)
            else:
                janela.logo_login = tk.PhotoImage(file=ARQUIVO_LOGO)

            tk.Label(
                painel,
                image=janela.logo_login,
                bg=BRANCO,
            ).pack(anchor="w", pady=(0, 22))

            logo_ok = True
        except Exception:
            pass

    if not logo_ok:
        tk.Label(
            painel,
            text="UNIMAR",
            bg=BRANCO,
            fg=AZUL,
            font=("Arial", 30, "bold"),
        ).pack(anchor="w")

        tk.Label(
            painel,
            text="UNIVERSIDADE DE MARÍLIA",
            bg=BRANCO,
            fg=AZUL_ESCURO,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(0, 22))

    tk.Label(
        painel,
        text="Bem-vindo ao UNIMAPP",
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 25, "bold"),
    ).pack(anchor="w")

    tk.Label(
        painel,
        text=(
            "Estude, organize sua rotina e encontre seus "
            "recursos acadêmicos em um só lugar."
        ),
        bg=BRANCO,
        fg=TEXTO_SEC,
        wraplength=400,
        justify="left",
        font=("Arial", 11),
    ).pack(anchor="w", pady=(8, 28))

    tk.Label(
        painel,
        text="Usuário",
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 10, "bold"),
    ).pack(anchor="w")

    entrada_usuario = tk.Entry(
        painel,
        width=35,
        font=("Arial", 12),
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightcolor=AZUL,
        highlightbackground=BORDA,
    )
    entrada_usuario.pack(fill="x", ipady=8, pady=(6, 16))

    tk.Label(
        painel,
        text="Senha",
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 10, "bold"),
    ).pack(anchor="w")

    entrada_senha = tk.Entry(
        painel,
        width=35,
        font=("Arial", 12),
        show="*",
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightcolor=AZUL,
        highlightbackground=BORDA,
    )
    entrada_senha.pack(fill="x", ipady=8, pady=(6, 16))

    tk.Label(
        painel,
        text="Tipo da conta",
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 10, "bold"),
    ).pack(anchor="w")

    tipo_conta = tk.StringVar(value="Aluno")
    linha_tipo = tk.Frame(painel, bg=BRANCO)
    linha_tipo.pack(anchor="w", pady=(6, 18))

    for texto in ("Aluno", "Professor"):
        tk.Radiobutton(
            linha_tipo,
            text=texto,
            variable=tipo_conta,
            value=texto,
            bg=BRANCO,
            fg=TEXTO,
            activebackground=BRANCO,
            selectcolor=AZUL_CLARO,
            font=("Arial", 10),
        ).pack(side="left", padx=(0, 18))

    mensagem = tk.Label(
        painel,
        text="",
        bg=BRANCO,
        fg=VERMELHO,
        font=("Arial", 9),
        wraplength=380,
    )
    mensagem.pack(pady=(10, 8))

    def entrar():
        global usuario_atual

        usuario = entrada_usuario.get().strip()
        senha = entrada_senha.get().strip()

        if not usuario or not senha:
            mensagem.config(
                text="Preencha usuário e senha.",
                fg=VERMELHO,
            )
            return

        if usuario not in usuarios:
            mensagem.config(
                text="Usuário não encontrado. Crie uma conta primeiro.",
                fg=VERMELHO,
            )
            return

        if usuarios[usuario].get("senha") != senha:
            mensagem.config(
                text="Senha incorreta.",
                fg=VERMELHO,
            )
            return

        if usuarios[usuario].get("tipo") != tipo_conta.get():
            mensagem.config(
                text="O tipo de conta selecionado não corresponde ao cadastro.",
                fg=VERMELHO,
            )
            return

        usuario_atual = usuario
        criar_dashboard()

    def criar_conta():
        usuario = entrada_usuario.get().strip()
        senha = entrada_senha.get().strip()

        if not usuario or not senha:
            mensagem.config(
                text="Digite um usuário e uma senha para criar a conta.",
                fg=VERMELHO,
            )
            return

        if usuario in usuarios:
            mensagem.config(
                text="Este usuário já existe.",
                fg=VERMELHO,
            )
            return

        usuarios[usuario] = {
            "senha": senha,
            "tipo": tipo_conta.get(),
            "curso": "Curso não informado",
        }

        salvar_usuarios()

        mensagem.config(
            text="Conta criada! Agora clique em Entrar.",
            fg=VERDE,
        )
        entrada_senha.delete(0, tk.END)

    criar_botao(
        painel,
        "Entrar no UNIMAPP",
        entrar,
        largura=28,
        destaque=True,
    ).pack(fill="x", pady=(2, 8))

    criar_botao(
        painel,
        "Criar minha conta",
        criar_conta,
        largura=28,
    ).pack(fill="x")

    tk.Label(
        painel,
        text="Protótipo acadêmico • UNIMAR",
        bg=BRANCO,
        fg="#8A99A6",
        font=("Arial", 8),
    ).pack(anchor="w", pady=(28, 0))

    entrada_usuario.focus()
    entrada_senha.bind("<Return>", lambda _event: entrar())


def criar_dashboard():
    limpar_frame(janela)
    janela.configure(bg=FUNDO)

    dados = usuarios[usuario_atual]
    tipo = dados.get("tipo", "Aluno")
    curso = dados.get("curso", "Curso não informado")

    lateral = tk.Frame(
        janela,
        bg=AZUL_MUITO_ESCURO,
        width=235,
    )
    lateral.pack(side="left", fill="y")
    lateral.pack_propagate(False)

    tk.Label(
        lateral,
        text="UNIMAPP",
        bg=AZUL_MUITO_ESCURO,
        fg=BRANCO,
        font=("Arial", 25, "bold"),
    ).pack(anchor="w", padx=25, pady=(28, 2))

    tk.Label(
        lateral,
        text="UNIMAR • Área acadêmica",
        bg=AZUL_MUITO_ESCURO,
        fg="#B9DDF2",
        font=("Arial", 9),
    ).pack(anchor="w", padx=25, pady=(0, 30))

    menu = [
        ("⌂  Início", mostrar_inicio),
        (
            "▣  Materiais digitais",
            lambda: mostrar_secao(
                "Materiais digitais",
                "Organize apostilas, PDFs, slides e conteúdos das disciplinas.",
            ),
        ),
        (
            "✓  Provas e avaliações",
            lambda: mostrar_secao(
                "Provas e avaliações",
                "Central para revisar provas, trabalhos e atividades.",
            ),
        ),
        (
            "◷  Agenda acadêmica",
            lambda: mostrar_secao(
                "Agenda acadêmica",
                "Visualize prazos, aulas, eventos e compromissos.",
            ),
        ),
        (
            "▤  Biblioteca",
            lambda: mostrar_secao(
                "Biblioteca",
                "Acesso rápido aos recursos e leituras da vida acadêmica.",
            ),
        ),
        (
            "▥  Notas e desempenho",
            lambda: mostrar_secao(
                "Notas e desempenho",
                "Acompanhe seu progresso acadêmico ao longo do semestre.",
            ),
        ),
    ]

    for texto, comando in menu:
        tk.Button(
            lateral,
            text=texto,
            command=comando,
            anchor="w",
            bg=AZUL_MUITO_ESCURO,
            fg="#DCEFFA",
            activebackground=AZUL,
            activeforeground=BRANCO,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=24,
            pady=13,
        ).pack(fill="x")

    tk.Frame(
        lateral,
        bg="#1E567C",
        height=1,
    ).pack(fill="x", padx=20, pady=20)

    tk.Label(
        lateral,
        text="CONTA",
        bg=AZUL_MUITO_ESCURO,
        fg="#86B7D5",
        font=("Arial", 8, "bold"),
    ).pack(anchor="w", padx=25, pady=(0, 8))

    tk.Label(
        lateral,
        text=usuario_atual,
        bg=AZUL_MUITO_ESCURO,
        fg=BRANCO,
        font=("Arial", 11, "bold"),
    ).pack(anchor="w", padx=25)

    tk.Label(
        lateral,
        text=tipo,
        bg=AZUL_MUITO_ESCURO,
        fg="#B9DDF2",
        font=("Arial", 9),
    ).pack(anchor="w", padx=25, pady=(2, 18))

    criar_botao(
        lateral,
        "Sair",
        criar_tela_login,
        largura=14,
    ).pack(side="bottom", pady=25)

    global conteudo
    conteudo = tk.Frame(janela, bg=FUNDO)
    conteudo.pack(side="right", fill="both", expand=True)

    mostrar_inicio()


def cabecalho(titulo, subtitulo):
    tk.Label(
        conteudo,
        text=titulo,
        bg=FUNDO,
        fg=TEXTO,
        font=("Arial", 27, "bold"),
    ).pack(anchor="w", padx=35, pady=(30, 2))

    tk.Label(
        conteudo,
        text=subtitulo,
        bg=FUNDO,
        fg=TEXTO_SEC,
        font=("Arial", 11),
    ).pack(anchor="w", padx=35, pady=(0, 24))


def criar_card(parent, titulo, subtitulo, icone, comando, coluna):
    caixa = tk.Frame(
        parent,
        bg=BRANCO,
        highlightbackground=BORDA,
        highlightthickness=1,
        width=230,
        height=205,
    )

    caixa.grid(
        row=0,
        column=coluna,
        sticky="nsew",
        padx=(
            0 if coluna == 0 else 8,
            8 if coluna < 2 else 0,
        ),
    )
    caixa.grid_propagate(False)

    tk.Label(
        caixa,
        text=icone,
        bg=AZUL_CLARO,
        fg=AZUL_ESCURO,
        font=("Arial", 20, "bold"),
        width=4,
        height=2,
    ).pack(anchor="w", padx=18, pady=(18, 12))

    tk.Label(
        caixa,
        text=titulo,
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 13, "bold"),
    ).pack(anchor="w", padx=18)

    tk.Label(
        caixa,
        text=subtitulo,
        bg=BRANCO,
        fg=TEXTO_SEC,
        font=("Arial", 9),
        justify="left",
        wraplength=200,
    ).pack(anchor="w", padx=18, pady=(5, 10))

    criar_botao(
        caixa,
        "Abrir",
        comando,
        largura=12,
        destaque=True,
    ).pack(anchor="w", padx=18)

    parent.columnconfigure(coluna, weight=1)


def mostrar_inicio():
    limpar_frame(conteudo)

    dados = usuarios[usuario_atual]
    curso = dados.get("curso", "Curso não informado")
    tipo = dados.get("tipo", "Aluno")

    cabecalho(
        f"Olá, {usuario_atual}!",
        "Que bom ter você de volta ao seu espaço de estudos.",
    )

    banner = tk.Frame(
        conteudo,
        bg=AZUL,
        height=130,
    )
    banner.pack(fill="x", padx=35)
    banner.pack_propagate(False)

    tk.Label(
        banner,
        text="Seu caminho acadêmico começa aqui.",
        bg=AZUL,
        fg=BRANCO,
        font=("Arial", 21, "bold"),
    ).pack(anchor="w", padx=25, pady=(22, 4))

    tk.Label(
        banner,
        text=f"{tipo}  •  {curso}",
        bg=AZUL,
        fg="#D8EEFC",
        font=("Arial", 10),
    ).pack(anchor="w", padx=25)

    stats = tk.Frame(conteudo, bg=FUNDO)
    stats.pack(fill="x", padx=35, pady=20)

    for titulo, valor, detalhe in [
        ("Materiais", "12", "disponíveis"),
        ("Avaliações", "03", "próximas"),
        ("Progresso", "72%", "do semestre"),
    ]:
        bloco = tk.Frame(
            stats,
            bg=BRANCO,
            highlightbackground=BORDA,
            highlightthickness=1,
            width=210,
            height=80,
        )
        bloco.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12),
        )
        bloco.pack_propagate(False)

        tk.Label(
            bloco,
            text=valor,
            bg=BRANCO,
            fg=AZUL,
            font=("Arial", 20, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 0))

        tk.Label(
            bloco,
            text=f"{titulo} • {detalhe}",
            bg=BRANCO,
            fg=TEXTO_SEC,
            font=("Arial", 9),
        ).pack(anchor="w", padx=15)

    tk.Label(
        conteudo,
        text="Acesso rápido",
        bg=FUNDO,
        fg=TEXTO,
        font=("Arial", 16, "bold"),
    ).pack(anchor="w", padx=35, pady=(0, 12))

    grade = tk.Frame(conteudo, bg=FUNDO)
    grade.pack(fill="x", padx=35)

    criar_card(
        grade,
        "Materiais digitais",
        "Apostilas, slides e arquivos das disciplinas.",
        "▤",
        lambda: mostrar_secao(
            "Materiais digitais",
            "Seus materiais de estudo ficarão organizados aqui.",
        ),
        0,
    )

    criar_card(
        grade,
        "Provas e avaliações",
        "Revise provas e acompanhe avaliações.",
        "✓",
        lambda: mostrar_secao(
            "Provas e avaliações",
            "Suas avaliações e atividades aparecerão aqui.",
        ),
        1,
    )

    criar_card(
        grade,
        "Agenda acadêmica",
        "Prazos, aulas e eventos importantes.",
        "◷",
        lambda: mostrar_secao(
            "Agenda acadêmica",
            "Sua agenda acadêmica ficará disponível aqui.",
        ),
        2,
    )


def mostrar_secao(titulo, descricao):
    limpar_frame(conteudo)
    cabecalho(titulo, descricao)

    painel = tk.Frame(
        conteudo,
        bg=BRANCO,
        highlightbackground=BORDA,
        highlightthickness=1,
    )
    painel.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=(0, 35),
    )

    tk.Label(
        painel,
        text="Em construção",
        bg=BRANCO,
        fg=AZUL,
        font=("Arial", 24, "bold"),
    ).pack(pady=(100, 8))

    tk.Label(
        painel,
        text=(
            "Esta área já está integrada à navegação do UNIMAPP.\n"
            "Agora você pode adicionar os dados reais da plataforma."
        ),
        bg=BRANCO,
        fg=TEXTO_SEC,
        justify="center",
        font=("Arial", 11),
    ).pack()

    criar_botao(
        painel,
        "Voltar para início",
        mostrar_inicio,
        largura=20,
        destaque=True,
    ).pack(pady=25)


janela = tk.Tk()
janela.title("UNIMAPP • Universidade de Marília")
janela.geometry("1180x720")
janela.minsize(980, 650)
janela.configure(bg=FUNDO)

criar_tela_login()
janela.mainloop()
