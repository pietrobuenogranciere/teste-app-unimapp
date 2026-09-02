import hashlib
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# UNIMAPP - versão funcional 3.0 com modificações na interface original e nos botões

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
AMARELO = "#A66A00"

DB_FILE = "unimapp.db"

janela = None
usuario_atual = None
conteudo = None

# BANCO DE DADOS

def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def inicializar_banco():
    conn = conectar()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'Aluno',
            curso TEXT NOT NULL DEFAULT 'Curso não informado'
        );

        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            disciplina TEXT NOT NULL DEFAULT '',
            tipo TEXT NOT NULL DEFAULT 'Apostila',
            caminho TEXT NOT NULL DEFAULT '',
            descricao TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            disciplina TEXT NOT NULL DEFAULT '',
            data TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Pendente',
            nota REAL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            data TEXT NOT NULL DEFAULT '',
            hora TEXT NOT NULL DEFAULT '',
            tipo TEXT NOT NULL DEFAULT 'Aula',
            descricao TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS biblioteca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL DEFAULT '',
            categoria TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Disponível',
            link TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            disciplina TEXT NOT NULL,
            atividade TEXT NOT NULL,
            nota REAL NOT NULL,
            valor_maximo REAL NOT NULL DEFAULT 10,
            semestre TEXT NOT NULL DEFAULT 'Atual',
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
    """)

    # Usuário inicial para testar a aplicação.
    existe = cur.execute(
        "SELECT id FROM usuarios WHERE usuario = ?",
        ("aluno",)
    ).fetchone()

    if not existe:
        cur.execute(
            """
            INSERT INTO usuarios (usuario, senha_hash, tipo, curso)
            VALUES (?, ?, ?, ?)
            """,
            (
                "aluno",
                hash_senha("1234"),
                "Aluno",
                "Projeto Jovem Programador"
            )
        )

    conn.commit()
    conn.close()


def obter_usuario(usuario):
    conn = conectar()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE usuario = ?",
        (usuario,)
    ).fetchone()
    conn.close()
    return row


def usuario_id_atual():
    row = obter_usuario(usuario_atual)
    return row["id"] if row else None

# UTILITÁRIOS DE INTERFACE

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
    ).pack(anchor="w", padx=35, pady=(0, 20))


def criar_tree(parent, colunas, larguras=None):
    frame = tk.Frame(parent, bg=BRANCO)

    tree = ttk.Treeview(
        frame,
        columns=colunas,
        show="headings",
        selectmode="browse"
    )

    for i, coluna in enumerate(colunas):
        tree.heading(coluna, text=coluna)
        tree.column(
            coluna,
            width=larguras[i] if larguras else 130,
            anchor="w"
        )

    scroll = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    return frame, tree


def abrir_caminho(caminho):
    if not caminho:
        messagebox.showinfo("Material", "Este item não possui arquivo ou link cadastrado.")
        return

    try:
        if caminho.startswith(("http://", "https://")):
            import webbrowser
            webbrowser.open(caminho)
        elif os.path.exists(caminho):
            os.startfile(os.path.abspath(caminho))
        else:
            messagebox.showwarning(
                "Arquivo não encontrado",
                f"O caminho cadastrado não existe mais:\n\n{caminho}"
            )
    except Exception as exc:
        messagebox.showerror("Erro", f"Não foi possível abrir o item.\n\n{exc}")


def campo_form(parent, texto, valor="", largura=45):
    tk.Label(
        parent,
        text=texto,
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(8, 3))

    entrada = tk.Entry(
        parent,
        width=largura,
        font=("Arial", 11),
        relief="solid",
        bd=1
    )
    entrada.pack(fill="x", ipady=6)

    if valor:
        entrada.insert(0, str(valor))

    return entrada


def combo_form(parent, texto, valores, valor_inicial=None):
    tk.Label(
        parent,
        text=texto,
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(8, 3))

    var = tk.StringVar(
        value=valor_inicial if valor_inicial is not None else valores[0]
    )

    combo = ttk.Combobox(
        parent,
        textvariable=var,
        values=valores,
        state="readonly",
        font=("Arial", 10)
    )
    combo.pack(fill="x", ipady=5)

    return var


def abrir_formulario(titulo, montar, salvar):
    janela_form = tk.Toplevel(janela)
    janela_form.title(titulo)
    janela_form.configure(bg=BRANCO)
    janela_form.geometry("520x620")
    janela_form.transient(janela)
    janela_form.grab_set()

    area = tk.Frame(janela_form, bg=BRANCO)
    area.pack(fill="both", expand=True, padx=25, pady=20)

    montar(area)

    botoes = tk.Frame(area, bg=BRANCO)
    botoes.pack(fill="x", pady=(20, 0))

    def confirmar():
        if salvar():
            janela_form.destroy()

    criar_botao(
        botoes, "Cancelar", janela_form.destroy, largura=14
    ).pack(side="right", padx=(8, 0))

    criar_botao(
        botoes, "Salvar", confirmar, largura=14, destaque=True
    ).pack(side="right")

# LOGIN E CONTA

def criar_tela_login():
    limpar_frame(janela)
    janela.configure(bg=FUNDO)

    esquerda = tk.Frame(
        janela,
        bg=AZUL_MUITO_ESCURO,
        width=620
    )
    esquerda.pack(side="left", fill="both", expand=True)

    canvas = tk.Canvas(
        esquerda,
        bg=AZUL_MUITO_ESCURO,
        highlightthickness=0
    )
    canvas.pack(fill="both", expand=True)

    def desenhar(event=None):
        canvas.delete("all")
        w = max(1, canvas.winfo_width())
        h = max(1, canvas.winfo_height())

        faixas = ["#083B66", "#07538A", "#086AA7", "#0877B7"]
        largura = max(1, w // len(faixas))

        for i, cor in enumerate(faixas):
            canvas.create_rectangle(
                i * largura, 0,
                (i + 1) * largura + 2, h,
                fill=cor,
                outline=cor
            )

        base = h * 0.68

        canvas.create_polygon(
            w * 0.08, base,
            w * 0.50, base - 80,
            w * 0.92, base,
            fill="#EAF5FC",
            outline=""
        )

        canvas.create_rectangle(
            w * 0.12, base,
            w * 0.88, h * 0.88,
            fill="#F7FBFF",
            outline=""
        )

        for x in [
            w * 0.20, w * 0.31, w * 0.42,
            w * 0.53, w * 0.64, w * 0.75
        ]:
            canvas.create_rectangle(
                x, base + 25,
                x + 34, h * 0.88,
                fill="#D8E6EF",
                outline=""
            )

        canvas.create_text(
            w * 0.10,
            h * 0.12,
            anchor="nw",
            text="UNIMAPP",
            fill=BRANCO,
            font=("Arial", 34, "bold")
        )

        canvas.create_text(
            w * 0.10,
            h * 0.20,
            anchor="nw",
            text="Seu espaço acadêmico em um só lugar.",
            fill="#D6EEFC",
            font=("Arial", 13)
        )

        canvas.create_text(
            w * 0.10,
            h * 0.92,
            anchor="sw",
            text="UNIVERSIDADE DE MARÍLIA • PROJETO ACADÊMICO",
            fill="#C7E4F5",
            font=("Arial", 9, "bold")
        )

    canvas.bind("<Configure>", desenhar)

    direita = tk.Frame(
        janela,
        bg=BRANCO,
        width=530
    )
    direita.pack(side="right", fill="both", expand=True)

    painel = tk.Frame(direita, bg=BRANCO)
    painel.pack(expand=True, padx=60, pady=35)

    tk.Label(
        painel,
        text="UNIMAR",
        bg=BRANCO,
        fg=AZUL,
        font=("Arial", 30, "bold")
    ).pack(anchor="w")

    tk.Label(
        painel,
        text="UNIVERSIDADE DE MARÍLIA",
        bg=BRANCO,
        fg=AZUL_ESCURO,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(0, 22))

    tk.Label(
        painel,
        text="Bem-vindo ao UNIMAPP",
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 25, "bold")
    ).pack(anchor="w")

    tk.Label(
        painel,
        text="Estude, organize sua rotina e encontre seus recursos acadêmicos em um só lugar.",
        bg=BRANCO,
        fg=TEXTO_SEC,
        wraplength=400,
        justify="left",
        font=("Arial", 11)
    ).pack(anchor="w", pady=(8, 28))

    entrada_usuario = campo_form(painel, "Usuário")
    entrada_senha = campo_form(painel, "Senha")

    entrada_senha.config(show="*")

    tipo_conta = tk.StringVar(value="Aluno")

    tk.Label(
        painel,
        text="Tipo da conta",
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(15, 5))

    linha_tipo = tk.Frame(painel, bg=BRANCO)
    linha_tipo.pack(anchor="w")

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
            font=("Arial", 10)
        ).pack(side="left", padx=(0, 18))

    mensagem = tk.Label(
        painel,
        text="",
        bg=BRANCO,
        fg=VERMELHO,
        font=("Arial", 9),
        wraplength=380
    )
    mensagem.pack(pady=(15, 8))

    def entrar():
        global usuario_atual

        usuario = entrada_usuario.get().strip()
        senha = entrada_senha.get().strip()

        if not usuario or not senha:
            mensagem.config(
                text="Preencha usuário e senha.",
                fg=VERMELHO
            )
            return

        dados = obter_usuario(usuario)

        if not dados:
            mensagem.config(
                text="Usuário não encontrado. Crie uma conta primeiro.",
                fg=VERMELHO
            )
            return

        if dados["senha_hash"] != hash_senha(senha):
            mensagem.config(
                text="Senha incorreta.",
                fg=VERMELHO
            )
            return

        if dados["tipo"] != tipo_conta.get():
            mensagem.config(
                text="O tipo de conta selecionado não corresponde ao cadastro.",
                fg=VERMELHO
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
                fg=VERMELHO
            )
            return

        if len(senha) < 4:
            mensagem.config(
                text="A senha deve possuir pelo menos 4 caracteres.",
                fg=VERMELHO
            )
            return

        if obter_usuario(usuario):
            mensagem.config(
                text="Este usuário já existe.",
                fg=VERMELHO
            )
            return

        try:
            conn = conectar()
            conn.execute(
                """
                INSERT INTO usuarios
                    (usuario, senha_hash, tipo, curso)
                VALUES (?, ?, ?, ?)
                """,
                (
                    usuario,
                    hash_senha(senha),
                    tipo_conta.get(),
                    "Curso não informado"
                )
            )
            conn.commit()
            conn.close()

            mensagem.config(
                text="Conta criada! Agora clique em Entrar.",
                fg=VERDE
            )
            entrada_senha.delete(0, tk.END)

        except sqlite3.Error as exc:
            mensagem.config(
                text=f"Não foi possível criar a conta: {exc}",
                fg=VERMELHO
            )

    criar_botao(
        painel,
        "Entrar no UNIMAPP",
        entrar,
        largura=28,
        destaque=True
    ).pack(fill="x", pady=(5, 8))

    criar_botao(
        painel,
        "Criar minha conta",
        criar_conta,
        largura=28
    ).pack(fill="x")

    tk.Label(
        painel,
        text="Protótipo acadêmico • dados armazenados localmente em SQLite",
        bg=BRANCO,
        fg="#8A99A6",
        font=("Arial", 8)
    ).pack(anchor="w", pady=(28, 0))

    entrada_usuario.focus()
    entrada_senha.bind("<Return>", lambda _event: entrar())

# DASHBOARD

def criar_dashboard():
    limpar_frame(janela)
    janela.configure(bg=FUNDO)

    dados = obter_usuario(usuario_atual)
    tipo = dados["tipo"]
    curso = dados["curso"]

    lateral = tk.Frame(
        janela,
        bg=AZUL_MUITO_ESCURO,
        width=235
    )
    lateral.pack(side="left", fill="y")
    lateral.pack_propagate(False)

    tk.Label(
        lateral,
        text="UNIMAPP",
        bg=AZUL_MUITO_ESCURO,
        fg=BRANCO,
        font=("Arial", 25, "bold")
    ).pack(anchor="w", padx=25, pady=(28, 2))

    tk.Label(
        lateral,
        text="UNIMAR • Área acadêmica",
        bg=AZUL_MUITO_ESCURO,
        fg="#B9DDF2",
        font=("Arial", 9)
    ).pack(anchor="w", padx=25, pady=(0, 25))

    menu = [
        ("⌂  Início", mostrar_inicio),
        ("▣  Materiais digitais", mostrar_materiais),
        ("✓  Provas e avaliações", mostrar_avaliacoes),
        ("◷  Agenda acadêmica", mostrar_agenda),
        ("▤  Biblioteca", mostrar_biblioteca),
        ("▥  Notas e desempenho", mostrar_notas),
        ("⚙  Meu perfil", mostrar_perfil),
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
            pady=12,
        ).pack(fill="x")

    tk.Frame(
        lateral,
        bg="#1E567C",
        height=1
    ).pack(fill="x", padx=20, pady=18)

    tk.Label(
        lateral,
        text="CONTA",
        bg=AZUL_MUITO_ESCURO,
        fg="#86B7D5",
        font=("Arial", 8, "bold")
    ).pack(anchor="w", padx=25, pady=(0, 8))

    tk.Label(
        lateral,
        text=usuario_atual,
        bg=AZUL_MUITO_ESCURO,
        fg=BRANCO,
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=25)

    tk.Label(
        lateral,
        text=tipo,
        bg=AZUL_MUITO_ESCURO,
        fg="#B9DDF2",
        font=("Arial", 9)
    ).pack(anchor="w", padx=25, pady=(2, 2))

    tk.Label(
        lateral,
        text=curso,
        bg=AZUL_MUITO_ESCURO,
        fg="#B9DDF2",
        wraplength=180,
        justify="left",
        font=("Arial", 8)
    ).pack(anchor="w", padx=25)

    criar_botao(
        lateral,
        "Sair",
        sair,
        largura=14
    ).pack(side="bottom", pady=25)

    global conteudo
    conteudo = tk.Frame(janela, bg=FUNDO)
    conteudo.pack(side="right", fill="both", expand=True)

    mostrar_inicio()


def sair():
    global usuario_atual
    usuario_atual = None
    criar_tela_login()

# INÍCIO dos dados

def obter_estatisticas():
    uid = usuario_id_atual()
    conn = conectar()

    materiais = conn.execute(
        "SELECT COUNT(*) AS total FROM materiais WHERE usuario_id = ?",
        (uid,)
    ).fetchone()["total"]

    avaliacoes = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM avaliacoes
        WHERE usuario_id = ? AND status != 'Concluída'
        """,
        (uid,)
    ).fetchone()["total"]

    media = conn.execute(
        """
        SELECT AVG((nota / valor_maximo) * 100) AS media
        FROM notas
        WHERE usuario_id = ?
        """,
        (uid,)
    ).fetchone()["media"]

    conn.close()

    return materiais, avaliacoes, (round(media) if media is not None else 0)


def mostrar_inicio():
    limpar_frame(conteudo)

    dados = obter_usuario(usuario_atual)
    materiais, avaliacoes, progresso = obter_estatisticas()

    cabecalho(
        f"Olá, {usuario_atual}!",
        "Que bom ter você de volta ao seu espaço de estudos."
    )

    banner = tk.Frame(
        conteudo,
        bg=AZUL,
        height=130
    )
    banner.pack(fill="x", padx=35)
    banner.pack_propagate(False)

    tk.Label(
        banner,
        text="Seu caminho acadêmico começa aqui.",
        bg=AZUL,
        fg=BRANCO,
        font=("Arial", 21, "bold")
    ).pack(anchor="w", padx=25, pady=(22, 4))

    tk.Label(
        banner,
        text=f"{dados['tipo']}  •  {dados['curso']}",
        bg=AZUL,
        fg="#D8EEFC",
        font=("Arial", 10)
    ).pack(anchor="w", padx=25)

    stats = tk.Frame(conteudo, bg=FUNDO)
    stats.pack(fill="x", padx=35, pady=20)

    for titulo, valor, detalhe in [
        ("Materiais", str(materiais), "cadastrados"),
        ("Avaliações", f"{avaliacoes:02d}", "pendentes"),
        ("Desempenho", f"{progresso}%", "média relativa"),
    ]:
        bloco = tk.Frame(
            stats,
            bg=BRANCO,
            highlightbackground=BORDA,
            highlightthickness=1,
            width=210,
            height=80
        )
        bloco.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )
        bloco.pack_propagate(False)

        tk.Label(
            bloco,
            text=valor,
            bg=BRANCO,
            fg=AZUL,
            font=("Arial", 20, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 0))

        tk.Label(
            bloco,
            text=f"{titulo} • {detalhe}",
            bg=BRANCO,
            fg=TEXTO_SEC,
            font=("Arial", 9)
        ).pack(anchor="w", padx=15)

    tk.Label(
        conteudo,
        text="Acesso rápido",
        bg=FUNDO,
        fg=TEXTO,
        font=("Arial", 16, "bold")
    ).pack(anchor="w", padx=35, pady=(0, 12))

    grade = tk.Frame(conteudo, bg=FUNDO)
    grade.pack(fill="x", padx=35)

    criar_card(
        grade,
        "Materiais digitais",
        "Apostilas, slides, links e arquivos.",
        "▤",
        mostrar_materiais,
        0
    )

    criar_card(
        grade,
        "Provas e avaliações",
        "Cadastre provas, trabalhos e acompanhe notas.",
        "✓",
        mostrar_avaliacoes,
        1
    )

    criar_card(
        grade,
        "Agenda acadêmica",
        "Organize aulas, prazos e eventos.",
        "◷",
        mostrar_agenda,
        2
    )


def criar_card(parent, titulo, subtitulo, icone, comando, coluna):
    caixa = tk.Frame(
        parent,
        bg=BRANCO,
        highlightbackground=BORDA,
        highlightthickness=1,
        width=230,
        height=205
    )

    caixa.grid(
        row=0,
        column=coluna,
        sticky="nsew",
        padx=(0 if coluna == 0 else 8, 8 if coluna < 2 else 0)
    )
    caixa.grid_propagate(False)

    tk.Label(
        caixa,
        text=icone,
        bg=AZUL_CLARO,
        fg=AZUL_ESCURO,
        font=("Arial", 20, "bold"),
        width=4,
        height=2
    ).pack(anchor="w", padx=18, pady=(18, 12))

    tk.Label(
        caixa,
        text=titulo,
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 13, "bold")
    ).pack(anchor="w", padx=18)

    tk.Label(
        caixa,
        text=subtitulo,
        bg=BRANCO,
        fg=TEXTO_SEC,
        font=("Arial", 9),
        justify="left",
        wraplength=200
    ).pack(anchor="w", padx=18, pady=(5, 10))

    criar_botao(
        caixa,
        "Abrir",
        comando,
        largura=12,
        destaque=True
    ).pack(anchor="w", padx=18)

    parent.columnconfigure(coluna, weight=1)

# MATERIAIS DIGITAIS

def mostrar_materiais():
    limpar_frame(conteudo)
    cabecalho(
        "Materiais digitais",
        "Cada usuário possui sua própria lista de materiais."
    )

    painel = criar_painel_secao()

    barra = tk.Frame(painel, bg=BRANCO)
    barra.pack(fill="x", padx=18, pady=18)

    criar_botao(
        barra,
        "+ Novo material",
        lambda: formulario_material(tree),
        largura=16,
        destaque=True
    ).pack(side="left")

    criar_botao(
        barra,
        "Abrir arquivo/link",
        lambda: abrir_item_tree(tree, "material"),
        largura=18
    ).pack(side="left", padx=8)

    criar_botao(
        barra,
        "Editar",
        lambda: editar_material(tree),
        largura=12
    ).pack(side="left")

    criar_botao(
        barra,
        "Excluir",
        lambda: excluir_item_tree(tree, "materiais", "material"),
        largura=12
    ).pack(side="left", padx=8)

    frame_tree, tree = criar_tree(
        painel,
        ("ID", "Título", "Disciplina", "Tipo", "Descrição"),
        (55, 220, 150, 110, 320)
    )
    frame_tree.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    carregar_materiais(tree)


def carregar_materiais(tree):
    tree.delete(*tree.get_children())

    conn = conectar()
    rows = conn.execute(
        """
        SELECT id, titulo, disciplina, tipo, descricao
        FROM materiais
        WHERE usuario_id = ?
        ORDER BY titulo
        """,
        (usuario_id_atual(),)
    ).fetchall()
    conn.close()

    for row in rows:
        tree.insert(
            "",
            "end",
            iid=str(row["id"]),
            values=(
                row["id"],
                row["titulo"],
                row["disciplina"],
                row["tipo"],
                row["descricao"]
            )
        )


def formulario_material(tree, item_id=None):
    dados = None

    if item_id:
        conn = conectar()
        dados = conn.execute(
            "SELECT * FROM materiais WHERE id = ? AND usuario_id = ?",
            (item_id, usuario_id_atual())
        ).fetchone()
        conn.close()

    refs = {}

    def montar(area):
        refs["titulo"] = campo_form(
            area, "Título", dados["titulo"] if dados else ""
        )
        refs["disciplina"] = campo_form(
            area, "Disciplina", dados["disciplina"] if dados else ""
        )
        refs["tipo"] = combo_form(
            area,
            "Tipo",
            ["Apostila", "PDF", "Slide", "Vídeo", "Link", "Outro"],
            dados["tipo"] if dados else "Apostila"
        )
        refs["caminho"] = campo_form(
            area, "Arquivo ou link", dados["caminho"] if dados else ""
        )

        def selecionar():
            caminho = filedialog.askopenfilename()
            if caminho:
                refs["caminho"].delete(0, tk.END)
                refs["caminho"].insert(0, caminho)

        criar_botao(
            area,
            "Selecionar arquivo",
            selecionar,
            largura=18
        ).pack(anchor="w", pady=8)

        refs["descricao"] = campo_form(
            area, "Descrição", dados["descricao"] if dados else ""
        )

    def salvar():
        titulo = refs["titulo"].get().strip()

        if not titulo:
            messagebox.showwarning("Atenção", "Informe o título do material.")
            return False

        valores = (
            titulo,
            refs["disciplina"].get().strip(),
            refs["tipo"].get(),
            refs["caminho"].get().strip(),
            refs["descricao"].get().strip()
        )

        conn = conectar()

        if item_id:
            conn.execute(
                """
                UPDATE materiais
                SET titulo=?, disciplina=?, tipo=?, caminho=?, descricao=?
                WHERE id=? AND usuario_id=?
                """,
                (*valores, item_id, usuario_id_atual())
            )
        else:
            conn.execute(
                """
                INSERT INTO materiais
                    (usuario_id, titulo, disciplina, tipo, caminho, descricao)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (usuario_id_atual(), *valores)
            )

        conn.commit()
        conn.close()
        carregar_materiais(tree)
        return True

    abrir_formulario(
        "Editar material" if item_id else "Novo material",
        montar,
        salvar
    )


def editar_material(tree):
    selecionado = tree.selection()

    if not selecionado:
        messagebox.showinfo("Materiais", "Selecione um material.")
        return

    formulario_material(tree, int(selecionado[0]))

# AVALIAÇÕES

def mostrar_avaliacoes():
    limpar_frame(conteudo)
    cabecalho(
        "Provas e avaliações",
        "Cadastre avaliações e acompanhe o que já foi concluído."
    )

    painel = criar_painel_secao()

    barra = tk.Frame(painel, bg=BRANCO)
    barra.pack(fill="x", padx=18, pady=18)

    criar_botao(
        barra,
        "+ Nova avaliação",
        lambda: formulario_avaliacao(tree),
        largura=17,
        destaque=True
    ).pack(side="left")

    criar_botao(
        barra,
        "Editar",
        lambda: editar_avaliacao(tree),
        largura=12
    ).pack(side="left", padx=8)

    criar_botao(
        barra,
        "Excluir",
        lambda: excluir_item_tree(tree, "avaliacoes", "avaliação"),
        largura=12
    ).pack(side="left")

    frame_tree, tree = criar_tree(
        painel,
        ("ID", "Título", "Disciplina", "Data", "Status", "Nota"),
        (50, 230, 150, 110, 120, 80)
    )
    frame_tree.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    carregar_avaliacoes(tree)


def carregar_avaliacoes(tree):
    tree.delete(*tree.get_children())

    conn = conectar()
    rows = conn.execute(
        """
        SELECT id, titulo, disciplina, data, status, nota
        FROM avaliacoes
        WHERE usuario_id = ?
        ORDER BY data
        """,
        (usuario_id_atual(),)
    ).fetchall()
    conn.close()

    for row in rows:
        nota = "" if row["nota"] is None else f"{row['nota']:.2f}"
        tree.insert(
            "",
            "end",
            iid=str(row["id"]),
            values=(
                row["id"],
                row["titulo"],
                row["disciplina"],
                row["data"],
                row["status"],
                nota
            )
        )


def formulario_avaliacao(tree, item_id=None):
    dados = None

    if item_id:
        conn = conectar()
        dados = conn.execute(
            "SELECT * FROM avaliacoes WHERE id = ? AND usuario_id = ?",
            (item_id, usuario_id_atual())
        ).fetchone()
        conn.close()

    refs = {}

    def montar(area):
        refs["titulo"] = campo_form(
            area, "Título", dados["titulo"] if dados else ""
        )
        refs["disciplina"] = campo_form(
            area, "Disciplina", dados["disciplina"] if dados else ""
        )
        refs["data"] = campo_form(
            area, "Data (DD/MM/AAAA)",
            dados["data"] if dados else ""
        )
        refs["status"] = combo_form(
            area,
            "Status",
            ["Pendente", "Em andamento", "Concluída"],
            dados["status"] if dados else "Pendente"
        )
        refs["nota"] = campo_form(
            area,
            "Nota (opcional)",
            "" if not dados or dados["nota"] is None else dados["nota"]
        )

    def salvar():
        titulo = refs["titulo"].get().strip()

        if not titulo:
            messagebox.showwarning("Atenção", "Informe o título da avaliação.")
            return False

        nota_texto = refs["nota"].get().strip()
        nota = None

        if nota_texto:
            try:
                nota = float(nota_texto.replace(",", "."))
            except ValueError:
                messagebox.showwarning("Atenção", "A nota precisa ser numérica.")
                return False

        valores = (
            titulo,
            refs["disciplina"].get().strip(),
            refs["data"].get().strip(),
            refs["status"].get(),
            nota
        )

        conn = conectar()

        if item_id:
            conn.execute(
                """
                UPDATE avaliacoes
                SET titulo=?, disciplina=?, data=?, status=?, nota=?
                WHERE id=? AND usuario_id=?
                """,
                (*valores, item_id, usuario_id_atual())
            )
        else:
            conn.execute(
                """
                INSERT INTO avaliacoes
                    (usuario_id, titulo, disciplina, data, status, nota)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (usuario_id_atual(), *valores)
            )

        conn.commit()
        conn.close()
        carregar_avaliacoes(tree)
        return True

    abrir_formulario(
        "Editar avaliação" if item_id else "Nova avaliação",
        montar,
        salvar
    )


def editar_avaliacao(tree):
    selecionado = tree.selection()

    if not selecionado:
        messagebox.showinfo("Avaliações", "Selecione uma avaliação.")
        return

    formulario_avaliacao(tree, int(selecionado[0]))

# AGENDA
def mostrar_agenda():
    limpar_frame(conteudo)
    cabecalho(
        "Agenda acadêmica",
        "Aulas, provas, prazos e eventos são armazenados por usuário."
    )

    painel = criar_painel_secao()

    barra = tk.Frame(painel, bg=BRANCO)
    barra.pack(fill="x", padx=18, pady=18)

    criar_botao(
        barra,
        "+ Novo evento",
        lambda: formulario_agenda(tree),
        largura=15,
        destaque=True
    ).pack(side="left")

    criar_botao(
        barra,
        "Editar",
        lambda: editar_agenda(tree),
        largura=12
    ).pack(side="left", padx=8)

    criar_botao(
        barra,
        "Excluir",
        lambda: excluir_item_tree(tree, "agenda", "evento"),
        largura=12
    ).pack(side="left")

    frame_tree, tree = criar_tree(
        painel,
        ("ID", "Título", "Data", "Hora", "Tipo", "Descrição"),
        (50, 220, 110, 90, 110, 300)
    )
    frame_tree.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    carregar_agenda(tree)


def carregar_agenda(tree):
    tree.delete(*tree.get_children())

    conn = conectar()
    rows = conn.execute(
        """
        SELECT id, titulo, data, hora, tipo, descricao
        FROM agenda
        WHERE usuario_id = ?
        ORDER BY data, hora
        """,
        (usuario_id_atual(),)
    ).fetchall()
    conn.close()

    for row in rows:
        tree.insert(
            "",
            "end",
            iid=str(row["id"]),
            values=(
                row["id"],
                row["titulo"],
                row["data"],
                row["hora"],
                row["tipo"],
                row["descricao"]
            )
        )


def formulario_agenda(tree, item_id=None):
    dados = None

    if item_id:
        conn = conectar()
        dados = conn.execute(
            "SELECT * FROM agenda WHERE id = ? AND usuario_id = ?",
            (item_id, usuario_id_atual())
        ).fetchone()
        conn.close()

    refs = {}

    def montar(area):
        refs["titulo"] = campo_form(
            area, "Título", dados["titulo"] if dados else ""
        )
        refs["data"] = campo_form(
            area, "Data (DD/MM/AAAA)", dados["data"] if dados else ""
        )
        refs["hora"] = campo_form(
            area, "Hora", dados["hora"] if dados else ""
        )
        refs["tipo"] = combo_form(
            area,
            "Tipo",
            ["Aula", "Prova", "Trabalho", "Prazo", "Evento", "Outro"],
            dados["tipo"] if dados else "Aula"
        )
        refs["descricao"] = campo_form(
            area, "Descrição", dados["descricao"] if dados else ""
        )

    def salvar():
        titulo = refs["titulo"].get().strip()

        if not titulo:
            messagebox.showwarning("Atenção", "Informe o título do evento.")
            return False

        valores = (
            titulo,
            refs["data"].get().strip(),
            refs["hora"].get().strip(),
            refs["tipo"].get(),
            refs["descricao"].get().strip()
        )

        conn = conectar()

        if item_id:
            conn.execute(
                """
                UPDATE agenda
                SET titulo=?, data=?, hora=?, tipo=?, descricao=?
                WHERE id=? AND usuario_id=?
                """,
                (*valores, item_id, usuario_id_atual())
            )
        else:
            conn.execute(
                """
                INSERT INTO agenda
                    (usuario_id, titulo, data, hora, tipo, descricao)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (usuario_id_atual(), *valores)
            )

        conn.commit()
        conn.close()
        carregar_agenda(tree)
        return True

    abrir_formulario(
        "Editar evento" if item_id else "Novo evento",
        montar,
        salvar
    )


def editar_agenda(tree):
    selecionado = tree.selection()

    if not selecionado:
        messagebox.showinfo("Agenda", "Selecione um evento.")
        return

    formulario_agenda(tree, int(selecionado[0]))

# BIBLIOTECA

def mostrar_biblioteca():
    limpar_frame(conteudo)
    cabecalho(
        "Biblioteca",
        "Organize livros, artigos e outras referências acadêmicas."
    )

    painel = criar_painel_secao()

    barra = tk.Frame(painel, bg=BRANCO)
    barra.pack(fill="x", padx=18, pady=18)

    criar_botao(
        barra,
        "+ Novo item",
        lambda: formulario_biblioteca(tree),
        largura=14,
        destaque=True
    ).pack(side="left")

    criar_botao(
        barra,
        "Abrir link",
        lambda: abrir_item_tree(tree, "biblioteca"),
        largura=13
    ).pack(side="left", padx=8)

    criar_botao(
        barra,
        "Editar",
        lambda: editar_biblioteca(tree),
        largura=12
    ).pack(side="left")

    criar_botao(
        barra,
        "Excluir",
        lambda: excluir_item_tree(tree, "biblioteca", "item"),
        largura=12
    ).pack(side="left", padx=8)

    frame_tree, tree = criar_tree(
        painel,
        ("ID", "Título", "Autor", "Categoria", "Status"),
        (50, 250, 190, 140, 120)
    )
    frame_tree.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    carregar_biblioteca(tree)


def carregar_biblioteca(tree):
    tree.delete(*tree.get_children())

    conn = conectar()
    rows = conn.execute(
        """
        SELECT id, titulo, autor, categoria, status
        FROM biblioteca
        WHERE usuario_id = ?
        ORDER BY titulo
        """,
        (usuario_id_atual(),)
    ).fetchall()
    conn.close()

    for row in rows:
        tree.insert(
            "",
            "end",
            iid=str(row["id"]),
            values=(
                row["id"],
                row["titulo"],
                row["autor"],
                row["categoria"],
                row["status"]
            )
        )


def formulario_biblioteca(tree, item_id=None):
    dados = None

    if item_id:
        conn = conectar()
        dados = conn.execute(
            "SELECT * FROM biblioteca WHERE id = ? AND usuario_id = ?",
            (item_id, usuario_id_atual())
        ).fetchone()
        conn.close()

    refs = {}

    def montar(area):
        refs["titulo"] = campo_form(
            area, "Título", dados["titulo"] if dados else ""
        )
        refs["autor"] = campo_form(
            area, "Autor", dados["autor"] if dados else ""
        )
        refs["categoria"] = campo_form(
            area, "Categoria", dados["categoria"] if dados else ""
        )
        refs["status"] = combo_form(
            area,
            "Status",
            ["Disponível", "Lido", "Lendo", "Favorito"],
            dados["status"] if dados else "Disponível"
        )
        refs["link"] = campo_form(
            area, "Link", dados["link"] if dados else ""
        )

    def salvar():
        titulo = refs["titulo"].get().strip()

        if not titulo:
            messagebox.showwarning("Atenção", "Informe o título.")
            return False

        valores = (
            titulo,
            refs["autor"].get().strip(),
            refs["categoria"].get().strip(),
            refs["status"].get(),
            refs["link"].get().strip()
        )

        conn = conectar()

        if item_id:
            conn.execute(
                """
                UPDATE biblioteca
                SET titulo=?, autor=?, categoria=?, status=?, link=?
                WHERE id=? AND usuario_id=?
                """,
                (*valores, item_id, usuario_id_atual())
            )
        else:
            conn.execute(
                """
                INSERT INTO biblioteca
                    (usuario_id, titulo, autor, categoria, status, link)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (usuario_id_atual(), *valores)
            )

        conn.commit()
        conn.close()
        carregar_biblioteca(tree)
        return True

    abrir_formulario(
        "Editar item" if item_id else "Novo item",
        montar,
        salvar
    )


def editar_biblioteca(tree):
    selecionado = tree.selection()

    if not selecionado:
        messagebox.showinfo("Biblioteca", "Selecione um item.")
        return

    formulario_biblioteca(tree, int(selecionado[0]))


# NOTAS E DESEMPENHO

def mostrar_notas():
    limpar_frame(conteudo)
    cabecalho(
        "Notas e desempenho",
        "Suas notas são calculadas somente a partir dos seus próprios registros."
    )

    painel = criar_painel_secao()

    barra = tk.Frame(painel, bg=BRANCO)
    barra.pack(fill="x", padx=18, pady=18)

    criar_botao(
        barra,
        "+ Nova nota",
        lambda: formulario_nota(tree),
        largura=14,
        destaque=True
    ).pack(side="left")

    criar_botao(
        barra,
        "Editar",
        lambda: editar_nota(tree),
        largura=12
    ).pack(side="left", padx=8)

    criar_botao(
        barra,
        "Excluir",
        lambda: excluir_item_tree(tree, "notas", "nota"),
        largura=12
    ).pack(side="left")

    resumo = tk.Label(
        painel,
        text="",
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 12, "bold")
    )
    resumo.pack(anchor="w", padx=18, pady=(0, 10))

    frame_tree, tree = criar_tree(
        painel,
        ("ID", "Disciplina", "Atividade", "Nota", "Máximo", "Semestre"),
        (50, 180, 230, 80, 80, 100)
    )
    frame_tree.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    def atualizar_resumo():
        conn = conectar()
        row = conn.execute(
            """
            SELECT AVG((nota / valor_maximo) * 100) AS media,
                   COUNT(*) AS quantidade
            FROM notas
            WHERE usuario_id = ?
            """,
            (usuario_id_atual(),)
        ).fetchone()
        conn.close()

        media = row["media"]
        if media is None:
            resumo.config(text="Nenhuma nota cadastrada ainda.")
        else:
            resumo.config(
                text=f"Média relativa: {media:.1f}%   •   Registros: {row['quantidade']}"
            )

    carregar_notas(tree)
    atualizar_resumo()


def carregar_notas(tree):
    tree.delete(*tree.get_children())

    conn = conectar()
    rows = conn.execute(
        """
        SELECT id, disciplina, atividade, nota, valor_maximo, semestre
        FROM notas
        WHERE usuario_id = ?
        ORDER BY disciplina, atividade
        """,
        (usuario_id_atual(),)
    ).fetchall()
    conn.close()

    for row in rows:
        tree.insert(
            "",
            "end",
            iid=str(row["id"]),
            values=(
                row["id"],
                row["disciplina"],
                row["atividade"],
                f"{row['nota']:.2f}",
                f"{row['valor_maximo']:.2f}",
                row["semestre"]
            )
        )


def formulario_nota(tree, item_id=None):
    dados = None

    if item_id:
        conn = conectar()
        dados = conn.execute(
            "SELECT * FROM notas WHERE id = ? AND usuario_id = ?",
            (item_id, usuario_id_atual())
        ).fetchone()
        conn.close()

    refs = {}

    def montar(area):
        refs["disciplina"] = campo_form(
            area, "Disciplina", dados["disciplina"] if dados else ""
        )
        refs["atividade"] = campo_form(
            area, "Atividade", dados["atividade"] if dados else ""
        )
        refs["nota"] = campo_form(
            area, "Nota", dados["nota"] if dados else ""
        )
        refs["maximo"] = campo_form(
            area, "Valor máximo", dados["valor_maximo"] if dados else "10"
        )
        refs["semestre"] = campo_form(
            area, "Semestre", dados["semestre"] if dados else "Atual"
        )

    def salvar():
        disciplina = refs["disciplina"].get().strip()
        atividade = refs["atividade"].get().strip()

        if not disciplina or not atividade:
            messagebox.showwarning(
                "Atenção",
                "Informe a disciplina e a atividade."
            )
            return False

        try:
            nota = float(refs["nota"].get().replace(",", "."))
            maximo = float(refs["maximo"].get().replace(",", "."))
        except ValueError:
            messagebox.showwarning(
                "Atenção",
                "Nota e valor máximo precisam ser numéricos."
            )
            return False

        if maximo <= 0:
            messagebox.showwarning(
                "Atenção",
                "O valor máximo deve ser maior que zero."
            )
            return False

        valores = (
            disciplina,
            atividade,
            nota,
            maximo,
            refs["semestre"].get().strip()
        )

        conn = conectar()

        if item_id:
            conn.execute(
                """
                UPDATE notas
                SET disciplina=?, atividade=?, nota=?, valor_maximo=?, semestre=?
                WHERE id=? AND usuario_id=?
                """,
                (*valores, item_id, usuario_id_atual())
            )
        else:
            conn.execute(
                """
                INSERT INTO notas
                    (usuario_id, disciplina, atividade, nota, valor_maximo, semestre)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (usuario_id_atual(), *valores)
            )

        conn.commit()
        conn.close()
        carregar_notas(tree)
        return True

    abrir_formulario(
        "Editar nota" if item_id else "Nova nota",
        montar,
        salvar
    )


def editar_nota(tree):
    selecionado = tree.selection()

    if not selecionado:
        messagebox.showinfo("Notas", "Selecione uma nota.")
        return

    formulario_nota(tree, int(selecionado[0]))


# PERFIL

def mostrar_perfil():
    limpar_frame(conteudo)

    dados = obter_usuario(usuario_atual)

    cabecalho(
        "Meu perfil",
        "Atualize os dados básicos da sua conta."
    )

    painel = tk.Frame(
        conteudo,
        bg=BRANCO,
        highlightbackground=BORDA,
        highlightthickness=1
    )
    painel.pack(fill="x", padx=35, pady=(0, 25))

    area = tk.Frame(painel, bg=BRANCO)
    area.pack(fill="x", padx=25, pady=25)

    usuario_var = tk.StringVar(value=dados["usuario"])
    tipo_var = tk.StringVar(value=dados["tipo"])
    curso_var = tk.StringVar(value=dados["curso"])

    tk.Label(
        area,
        text="Usuário",
        bg=BRANCO,
        fg=TEXTO_SEC,
        font=("Arial", 9, "bold")
    ).pack(anchor="w")

    tk.Label(
        area,
        textvariable=usuario_var,
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 14, "bold")
    ).pack(anchor="w", pady=(2, 12))

    tk.Label(
        area,
        text="Tipo da conta",
        bg=BRANCO,
        fg=TEXTO_SEC,
        font=("Arial", 9, "bold")
    ).pack(anchor="w")

    tk.Label(
        area,
        textvariable=tipo_var,
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 11)
    ).pack(anchor="w", pady=(2, 12))

    tk.Label(
        area,
        text="Curso",
        bg=BRANCO,
        fg=TEXTO,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    entrada_curso = tk.Entry(
        area,
        font=("Arial", 11),
        relief="solid",
        bd=1
    )
    entrada_curso.pack(fill="x", ipady=7)
    entrada_curso.insert(0, dados["curso"])

    criar_botao(
        area,
        "Salvar alterações",
        lambda: salvar_perfil(entrada_curso),
        largura=20,
        destaque=True
    ).pack(anchor="w", pady=(15, 5))

    criar_botao(
        area,
        "Alterar senha",
        alterar_senha,
        largura=20
    ).pack(anchor="w", pady=5)


def salvar_perfil(entrada_curso):
    curso = entrada_curso.get().strip() or "Curso não informado"

    conn = conectar()
    conn.execute(
        "UPDATE usuarios SET curso=? WHERE id=?",
        (curso, usuario_id_atual())
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Perfil", "Dados atualizados com sucesso.")
    criar_dashboard()


def alterar_senha():
    janela_form = tk.Toplevel(janela)
    janela_form.title("Alterar senha")
    janela_form.geometry("420x300")
    janela_form.configure(bg=BRANCO)
    janela_form.transient(janela)
    janela_form.grab_set()

    area = tk.Frame(janela_form, bg=BRANCO)
    area.pack(fill="both", expand=True, padx=25, pady=20)

    atual = campo_form(area, "Senha atual")
    nova = campo_form(area, "Nova senha")
    confirmar = campo_form(area, "Confirmar nova senha")

    atual.config(show="*")
    nova.config(show="*")
    confirmar.config(show="*")

    def salvar():
        dados = obter_usuario(usuario_atual)

        if dados["senha_hash"] != hash_senha(atual.get()):
            messagebox.showwarning("Atenção", "A senha atual está incorreta.")
            return

        if len(nova.get()) < 4:
            messagebox.showwarning(
                "Atenção",
                "A nova senha deve possuir pelo menos 4 caracteres."
            )
            return

        if nova.get() != confirmar.get():
            messagebox.showwarning(
                "Atenção",
                "A confirmação da nova senha não confere."
            )
            return

        conn = conectar()
        conn.execute(
            "UPDATE usuarios SET senha_hash=? WHERE id=?",
            (hash_senha(nova.get()), usuario_id_atual())
        )
        conn.commit()
        conn.close()

        janela_form.destroy()
        messagebox.showinfo("Senha", "Senha alterada com sucesso.")

    criar_botao(
        area,
        "Salvar nova senha",
        salvar,
        largura=20,
        destaque=True
    ).pack(anchor="w", pady=20)

# FUNÇÕES GENÉRICAS DE TABELA


def criar_painel_secao():
    painel = tk.Frame(
        conteudo,
        bg=BRANCO,
        highlightbackground=BORDA,
        highlightthickness=1
    )
    painel.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=(0, 35)
    )
    return painel


def excluir_item_tree(tree, tabela, nome):
    selecionado = tree.selection()

    if not selecionado:
        messagebox.showinfo(
            "Exclusão",
            f"Selecione {nome} para excluir."
        )
        return

    item_id = int(selecionado[0])

    if not messagebox.askyesno(
        "Confirmar exclusão",
        f"Tem certeza que deseja excluir este {nome}?"
    ):
        return

    conn = conectar()

    conn.execute(
        f"DELETE FROM {tabela} WHERE id=? AND usuario_id=?",
        (item_id, usuario_id_atual())
    )

    conn.commit()
    conn.close()

    tree.delete(selecionado)


def abrir_item_tree(tree, tipo):
    selecionado = tree.selection()

    if not selecionado:
        messagebox.showinfo(
            "Abrir",
            "Selecione um item primeiro."
        )
        return

    item_id = int(selecionado[0])
    conn = conectar()

    if tipo == "material":
        row = conn.execute(
            """
            SELECT caminho
            FROM materiais
            WHERE id=? AND usuario_id=?
            """,
            (item_id, usuario_id_atual())
        ).fetchone()
        caminho = row["caminho"] if row else ""

    elif tipo == "biblioteca":
        row = conn.execute(
            """
            SELECT link
            FROM biblioteca
            WHERE id=? AND usuario_id=?
            """,
            (item_id, usuario_id_atual())
        ).fetchone()
        caminho = row["link"] if row else ""

    else:
        caminho = ""

    conn.close()
    abrir_caminho(caminho)

# INICIALIZAÇÃO


if __name__ == "__main__":
    inicializar_banco()

    janela = tk.Tk()
    janela.title("UNIMAPP • Universidade de Marília")
    janela.geometry("1180x720")
    janela.minsize(980, 650)
    janela.configure(bg=FUNDO)

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Treeview",
        rowheight=32,
        font=("Arial", 9)
    )
    style.configure(
        "Treeview.Heading",
        font=("Arial", 9, "bold")
    )

    criar_tela_login()
    janela.mainloop()
