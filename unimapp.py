import hashlib
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

#CONFIGURAÇÃO
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
DB_FILE = "unimapp.db"

janela = None
conteudo = None
usuario_atual = None


def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def inicializar_banco():
    with conectar() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                tipo TEXT NOT NULL DEFAULT 'Aluno',
                curso TEXT NOT NULL DEFAULT 'Curso não informado'
            );
            CREATE TABLE IF NOT EXISTS materiais (
                id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL,
                titulo TEXT NOT NULL, disciplina TEXT NOT NULL DEFAULT '',
                tipo TEXT NOT NULL DEFAULT 'Apostila', caminho TEXT NOT NULL DEFAULT '',
                descricao TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL,
                titulo TEXT NOT NULL, disciplina TEXT NOT NULL DEFAULT '',
                data TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Pendente', nota REAL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS agenda (
                id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL,
                titulo TEXT NOT NULL, data TEXT NOT NULL DEFAULT '', hora TEXT NOT NULL DEFAULT '',
                tipo TEXT NOT NULL DEFAULT 'Aula', descricao TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS biblioteca (
                id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL,
                titulo TEXT NOT NULL, autor TEXT NOT NULL DEFAULT '', categoria TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Disponível', link TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL,
                disciplina TEXT NOT NULL, atividade TEXT NOT NULL, nota REAL NOT NULL,
                valor_maximo REAL NOT NULL DEFAULT 10, semestre TEXT NOT NULL DEFAULT 'Atual',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
        """)
        if not conn.execute("SELECT id FROM usuarios WHERE usuario='aluno'").fetchone():
            conn.execute("""INSERT INTO usuarios (usuario, senha_hash, tipo, curso)
                           VALUES (?, ?, ?, ?)""",
                         ("aluno", hash_senha("1234"), "Aluno", "Projeto Jovem Programador"))


def obter_usuario(usuario):
    with conectar() as conn:
        return conn.execute("SELECT * FROM usuarios WHERE usuario=?", (usuario,)).fetchone()


def usuario_id_atual():
    dados = obter_usuario(usuario_atual)
    return dados["id"] if dados else None


#INTERFACE
def limpar(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def botao(parent, texto, comando, largura=18, destaque=False):
    return tk.Button(parent, text=texto, command=comando, width=largura,
                     bg=AZUL if destaque else BRANCO,
                     fg=BRANCO if destaque else AZUL_ESCURO,
                     activebackground=AZUL_ESCURO if destaque else AZUL_CLARO,
                     activeforeground=BRANCO if destaque else AZUL_ESCURO,
                     relief="flat", bd=0, cursor="hand2",
                     font=("Arial", 10, "bold"), padx=12, pady=9)


def cabecalho(titulo, subtitulo):
    tk.Label(conteudo, text=titulo, bg=FUNDO, fg=TEXTO,
             font=("Arial", 27, "bold")).pack(anchor="w", padx=35, pady=(30, 2))
    tk.Label(conteudo, text=subtitulo, bg=FUNDO, fg=TEXTO_SEC,
             font=("Arial", 11)).pack(anchor="w", padx=35, pady=(0, 20))


def painel_secao():
    painel = tk.Frame(conteudo, bg=BRANCO, highlightbackground=BORDA, highlightthickness=1)
    painel.pack(fill="both", expand=True, padx=35, pady=(0, 35))
    return painel


def criar_tree(parent, colunas, larguras):
    frame = tk.Frame(parent, bg=BRANCO)
    tree = ttk.Treeview(frame, columns=colunas, show="headings", selectmode="browse")
    for coluna, largura in zip(colunas, larguras):
        tree.heading(coluna, text=coluna)
        tree.column(coluna, width=largura, anchor="w")
    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return frame, tree


def campo(parent, texto, valor="", largura=45, senha=False):
    tk.Label(parent, text=texto, bg=BRANCO, fg=TEXTO,
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 3))
    entrada = tk.Entry(parent, width=largura, font=("Arial", 11), relief="solid", bd=1)
    entrada.pack(fill="x", ipady=6)
    if valor != "":
        entrada.insert(0, str(valor))
    if senha:
        entrada.config(show="*")
    return entrada


def combo(parent, texto, valores, valor=None):
    tk.Label(parent, text=texto, bg=BRANCO, fg=TEXTO,
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 3))
    var = tk.StringVar(value=valor if valor is not None else valores[0])
    ttk.Combobox(parent, textvariable=var, values=valores, state="readonly",
                 font=("Arial", 10)).pack(fill="x", ipady=5)
    return var


def formulario(titulo, montar, salvar, geometria="520x620"):
    win = tk.Toplevel(janela)
    win.title(titulo)
    win.geometry(geometria)
    win.configure(bg=BRANCO)
    win.transient(janela)
    win.grab_set()
    area = tk.Frame(win, bg=BRANCO)
    area.pack(fill="both", expand=True, padx=25, pady=20)
    montar(area)

    def confirmar():
        if salvar():
            win.destroy()

    botoes = tk.Frame(area, bg=BRANCO)
    botoes.pack(fill="x", pady=(20, 0))
    botao(botoes, "Cancelar", win.destroy, 14).pack(side="right", padx=(8, 0))
    botao(botoes, "Salvar", confirmar, 14, True).pack(side="right")


def abrir_caminho(caminho):
    if not caminho:
        messagebox.showinfo("Abrir", "Este item não possui arquivo ou link cadastrado.")
        return
    try:
        if caminho.startswith(("http://", "https://")):
            import webbrowser
            webbrowser.open(caminho)
        elif os.path.exists(caminho):
            os.startfile(os.path.abspath(caminho))
        else:
            messagebox.showwarning("Arquivo não encontrado", f"O caminho cadastrado não existe mais:\n\n{caminho}")
    except Exception as exc:
        messagebox.showerror("Erro", f"Não foi possível abrir o item.\n\n{exc}")


#LOGIN 
def criar_tela_login():
    limpar(janela)
    janela.configure(bg=FUNDO)

    esquerda = tk.Frame(janela, bg=AZUL_MUITO_ESCURO, width=620)
    esquerda.pack(side="left", fill="both", expand=True)
    canvas = tk.Canvas(esquerda, bg=AZUL_MUITO_ESCURO, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def desenhar(_=None):
        canvas.delete("all")
        w, h = max(1, canvas.winfo_width()), max(1, canvas.winfo_height())
        faixas = [AZUL_MUITO_ESCURO, "#07538A", "#086AA7", "#0877B7"]
        largura = max(1, w // 4)
        for i, cor in enumerate(faixas):
            canvas.create_rectangle(i*largura, 0, (i+1)*largura+2, h, fill=cor, outline=cor)
        base = h * .68
        canvas.create_polygon(w*.08, base, w*.50, base-80, w*.92, base, fill=AZUL_CLARO, outline="")
        canvas.create_rectangle(w*.12, base, w*.88, h*.88, fill="#F7FBFF", outline="")
        for x in (w*.20, w*.31, w*.42, w*.53, w*.64, w*.75):
            canvas.create_rectangle(x, base+25, x+34, h*.88, fill="#D8E6EF", outline="")
        canvas.create_text(w*.10, h*.12, anchor="nw", text="UNIMAPP", fill=BRANCO, font=("Arial", 34, "bold"))
        canvas.create_text(w*.10, h*.20, anchor="nw", text="Seu espaço acadêmico em um só lugar.", fill="#D6EEFC", font=("Arial", 13))
        canvas.create_text(w*.10, h*.92, anchor="sw", text="UNIVERSIDADE DE MARÍLIA • PROJETO ACADÊMICO", fill="#C7E4F5", font=("Arial", 9, "bold"))
    canvas.bind("<Configure>", desenhar)

    direita = tk.Frame(janela, bg=BRANCO, width=530)
    direita.pack(side="right", fill="both", expand=True)
    painel = tk.Frame(direita, bg=BRANCO)
    painel.pack(expand=True, padx=60, pady=35)

    tk.Label(painel, text="UNIMAR", bg=BRANCO, fg=AZUL, font=("Arial", 30, "bold")).pack(anchor="w")
    tk.Label(painel, text="UNIVERSIDADE DE MARÍLIA", bg=BRANCO, fg=AZUL_ESCURO, font=("Arial", 10, "bold")).pack(anchor="w", pady=(0,22))
    tk.Label(painel, text="Bem-vindo ao UNIMAPP", bg=BRANCO, fg=TEXTO, font=("Arial",25,"bold")).pack(anchor="w")
    tk.Label(painel, text="Estude, organize sua rotina e encontre seus recursos acadêmicos em um só lugar.",
             bg=BRANCO, fg=TEXTO_SEC, wraplength=400, justify="left", font=("Arial",11)).pack(anchor="w", pady=(8,28))

    usuario = campo(painel, "Usuário")
    senha = campo(painel, "Senha", senha=True)
    tipo = tk.StringVar(value="Aluno")
    tk.Label(painel, text="Tipo da conta", bg=BRANCO, fg=TEXTO, font=("Arial",10,"bold")).pack(anchor="w", pady=(15,5))
    linha = tk.Frame(painel, bg=BRANCO); linha.pack(anchor="w")
    for valor in ("Aluno", "Professor"):
        tk.Radiobutton(linha, text=valor, variable=tipo, value=valor, bg=BRANCO, fg=TEXTO,
                       activebackground=BRANCO, selectcolor=AZUL_CLARO, font=("Arial",10)).pack(side="left", padx=(0,18))
    msg = tk.Label(painel, text="", bg=BRANCO, fg=VERMELHO, font=("Arial",9), wraplength=380)
    msg.pack(pady=(15,8))

    def entrar():
        global usuario_atual
        nome, senha_texto = usuario.get().strip(), senha.get().strip()
        if not nome or not senha_texto:
            msg.config(text="Preencha usuário e senha.", fg=VERMELHO); return
        dados = obter_usuario(nome)
        if not dados:
            msg.config(text="Usuário não encontrado. Crie uma conta primeiro.", fg=VERMELHO); return
        if dados["senha_hash"] != hash_senha(senha_texto):
            msg.config(text="Senha incorreta.", fg=VERMELHO); return
        if dados["tipo"] != tipo.get():
            msg.config(text="O tipo de conta selecionado não corresponde ao cadastro.", fg=VERMELHO); return
        usuario_atual = nome
        criar_dashboard()

    def criar_conta():
        nome, senha_texto = usuario.get().strip(), senha.get().strip()
        if not nome or not senha_texto:
            msg.config(text="Digite um usuário e uma senha para criar a conta.", fg=VERMELHO); return
        if len(senha_texto) < 4:
            msg.config(text="A senha deve possuir pelo menos 4 caracteres.", fg=VERMELHO); return
        if obter_usuario(nome):
            msg.config(text="Este usuário já existe.", fg=VERMELHO); return
        try:
            with conectar() as conn:
                conn.execute("INSERT INTO usuarios (usuario,senha_hash,tipo,curso) VALUES (?,?,?,?)",
                             (nome, hash_senha(senha_texto), tipo.get(), "Curso não informado"))
            msg.config(text="Conta criada! Agora clique em Entrar.", fg=VERDE)
            senha.delete(0, tk.END)
        except sqlite3.Error as exc:
            msg.config(text=f"Não foi possível criar a conta: {exc}", fg=VERMELHO)

    botao(painel, "Entrar no UNIMAPP", entrar, 28, True).pack(fill="x", pady=(5,8))
    botao(painel, "Criar minha conta", criar_conta, 28).pack(fill="x")
    tk.Label(painel, text="Protótipo acadêmico • dados armazenados localmente em SQLite", bg=BRANCO,
             fg="#8A99A6", font=("Arial",8)).pack(anchor="w", pady=(28,0))
    usuario.focus()
    senha.bind("<Return>", lambda _: entrar())


#DASHBOARD
def criar_dashboard():
    global conteudo
    limpar(janela)
    dados = obter_usuario(usuario_atual)
    janela.configure(bg=FUNDO)

    lateral = tk.Frame(janela, bg=AZUL_MUITO_ESCURO, width=235)
    lateral.pack(side="left", fill="y"); lateral.pack_propagate(False)
    tk.Label(lateral, text="UNIMAPP", bg=AZUL_MUITO_ESCURO, fg=BRANCO, font=("Arial",25,"bold")).pack(anchor="w", padx=25, pady=(28,2))
    tk.Label(lateral, text="UNIMAR • Área acadêmica", bg=AZUL_MUITO_ESCURO, fg="#B9DDF2", font=("Arial",9)).pack(anchor="w", padx=25, pady=(0,25))

    menu = [("⌂  Início", mostrar_inicio), ("▣  Materiais digitais", lambda: mostrar_secao("materiais")),
            ("✓  Provas e avaliações", lambda: mostrar_secao("avaliacoes")), ("◷  Agenda acadêmica", lambda: mostrar_secao("agenda")),
            ("▤  Biblioteca", lambda: mostrar_secao("biblioteca")), ("▥  Notas e desempenho", lambda: mostrar_secao("notas")),
            ("⚙  Meu perfil", mostrar_perfil)]
    for texto, comando in menu:
        tk.Button(lateral, text=texto, command=comando, anchor="w", bg=AZUL_MUITO_ESCURO, fg="#DCEFFA",
                  activebackground=AZUL, activeforeground=BRANCO, relief="flat", bd=0, cursor="hand2",
                  font=("Arial",10,"bold"), padx=24, pady=12).pack(fill="x")
    tk.Frame(lateral, bg="#1E567C", height=1).pack(fill="x", padx=20, pady=18)
    tk.Label(lateral, text="CONTA", bg=AZUL_MUITO_ESCURO, fg="#86B7D5", font=("Arial",8,"bold")).pack(anchor="w", padx=25, pady=(0,8))
    tk.Label(lateral, text=usuario_atual, bg=AZUL_MUITO_ESCURO, fg=BRANCO, font=("Arial",11,"bold")).pack(anchor="w", padx=25)
    tk.Label(lateral, text=dados["tipo"], bg=AZUL_MUITO_ESCURO, fg="#B9DDF2", font=("Arial",9)).pack(anchor="w", padx=25, pady=2)
    tk.Label(lateral, text=dados["curso"], bg=AZUL_MUITO_ESCURO, fg="#B9DDF2", wraplength=180, justify="left", font=("Arial",8)).pack(anchor="w", padx=25)
    botao(lateral, "Sair", sair, 14).pack(side="bottom", pady=25)

    conteudo = tk.Frame(janela, bg=FUNDO)
    conteudo.pack(side="right", fill="both", expand=True)
    mostrar_inicio()


def sair():
    global usuario_atual
    usuario_atual = None
    criar_tela_login()


#INÍCIO
def obter_estatisticas():
    with conectar() as conn:
        uid = usuario_id_atual()
        materiais = conn.execute("SELECT COUNT(*) n FROM materiais WHERE usuario_id=?", (uid,)).fetchone()["n"]
        avaliacoes = conn.execute("SELECT COUNT(*) n FROM avaliacoes WHERE usuario_id=? AND status!='Concluída'", (uid,)).fetchone()["n"]
        media = conn.execute("SELECT AVG(nota/valor_maximo*100) n FROM notas WHERE usuario_id=?", (uid,)).fetchone()["n"]
    return materiais, avaliacoes, round(media) if media is not None else 0


def criar_card(parent, titulo, subtitulo, icone, comando, coluna):
    caixa = tk.Frame(parent, bg=BRANCO, highlightbackground=BORDA, highlightthickness=1, width=230, height=205)
    caixa.grid(row=0, column=coluna, sticky="nsew", padx=(0 if coluna==0 else 8, 8 if coluna<2 else 0)); caixa.grid_propagate(False)
    tk.Label(caixa, text=icone, bg=AZUL_CLARO, fg=AZUL_ESCURO, font=("Arial",20,"bold"), width=4, height=2).pack(anchor="w", padx=18, pady=(18,12))
    tk.Label(caixa, text=titulo, bg=BRANCO, fg=TEXTO, font=("Arial",13,"bold")).pack(anchor="w", padx=18)
    tk.Label(caixa, text=subtitulo, bg=BRANCO, fg=TEXTO_SEC, font=("Arial",9), justify="left", wraplength=200).pack(anchor="w", padx=18, pady=(5,10))
    botao(caixa, "Abrir", comando, 12, True).pack(anchor="w", padx=18)
    parent.columnconfigure(coluna, weight=1)


def mostrar_inicio():
    limpar(conteudo)
    dados = obter_usuario(usuario_atual)
    materiais, avaliacoes, progresso = obter_estatisticas()
    cabecalho(f"Olá, {usuario_atual}!", "Que bom ter você de volta ao seu espaço de estudos.")
    banner = tk.Frame(conteudo, bg=AZUL, height=130); banner.pack(fill="x", padx=35); banner.pack_propagate(False)
    tk.Label(banner, text="Seu caminho acadêmico começa aqui.", bg=AZUL, fg=BRANCO, font=("Arial",21,"bold")).pack(anchor="w", padx=25, pady=(22,4))
    tk.Label(banner, text=f"{dados['tipo']}  •  {dados['curso']}", bg=AZUL, fg="#D8EEFC", font=("Arial",10)).pack(anchor="w", padx=25)
    stats = tk.Frame(conteudo, bg=FUNDO); stats.pack(fill="x", padx=35, pady=20)
    for titulo, valor, detalhe in (("Materiais",str(materiais),"cadastrados"),("Avaliações",f"{avaliacoes:02d}","pendentes"),("Desempenho",f"{progresso}%","média relativa")):
        bloco=tk.Frame(stats,bg=BRANCO,highlightbackground=BORDA,highlightthickness=1,width=210,height=80); bloco.pack(side="left",fill="both",expand=True,padx=(0,12)); bloco.pack_propagate(False)
        tk.Label(bloco,text=valor,bg=BRANCO,fg=AZUL,font=("Arial",20,"bold")).pack(anchor="w",padx=15,pady=(10,0))
        tk.Label(bloco,text=f"{titulo} • {detalhe}",bg=BRANCO,fg=TEXTO_SEC,font=("Arial",9)).pack(anchor="w",padx=15)
    tk.Label(conteudo,text="Acesso rápido",bg=FUNDO,fg=TEXTO,font=("Arial",16,"bold")).pack(anchor="w",padx=35,pady=(0,12))
    grade=tk.Frame(conteudo,bg=FUNDO); grade.pack(fill="x",padx=35)
    criar_card(grade,"Materiais digitais","Apostilas, slides, links e arquivos.","▤",lambda: mostrar_secao("materiais"),0)
    criar_card(grade,"Provas e avaliações","Cadastre provas, trabalhos e acompanhe notas.","✓",lambda: mostrar_secao("avaliacoes"),1)
    criar_card(grade,"Agenda acadêmica","Organize aulas, prazos e eventos.","◷",lambda: mostrar_secao("agenda"),2)


# SEÇÕES
CONFIG = {
    "materiais": {
        "titulo":"Materiais digitais", "subtitulo":"Cada usuário possui sua própria lista de materiais.",
        "tabela":"materiais", "nome":"material", "novo":"+ Novo material", "abrir":"Abrir arquivo/link",
        "colunas":("ID","Título","Disciplina","Tipo","Descrição"), "larguras":(55,220,150,110,320),
        "select":"id,titulo,disciplina,tipo,descricao", "ordem":"titulo", "abrir_campo":"caminho",
        "campos":[("titulo","Título",None),("disciplina","Disciplina",None),("tipo","Tipo",["Apostila","PDF","Slide","Vídeo","Link","Outro"]),("caminho","Arquivo ou link",None),("descricao","Descrição",None)]
    },
    "avaliacoes": {
        "titulo":"Provas e avaliações", "subtitulo":"Cadastre avaliações e acompanhe o que já foi concluído.",
        "tabela":"avaliacoes", "nome":"avaliação", "novo":"+ Nova avaliação",
        "colunas":("ID","Título","Disciplina","Data","Status","Nota"), "larguras":(50,230,150,110,120,80),
        "select":"id,titulo,disciplina,data,status,nota", "ordem":"data",
        "campos":[("titulo","Título",None),("disciplina","Disciplina",None),("data","Data (DD/MM/AAAA)",None),("status","Status",["Pendente","Em andamento","Concluída"]),("nota","Nota (opcional)",None)]
    },
    "agenda": {
        "titulo":"Agenda acadêmica", "subtitulo":"Aulas, provas, prazos e eventos são armazenados por usuário.",
        "tabela":"agenda", "nome":"evento", "novo":"+ Novo evento",
        "colunas":("ID","Título","Data","Hora","Tipo","Descrição"), "larguras":(50,220,110,90,110,300),
        "select":"id,titulo,data,hora,tipo,descricao", "ordem":"data,hora",
        "campos":[("titulo","Título",None),("data","Data (DD/MM/AAAA)",None),("hora","Hora",None),("tipo","Tipo",["Aula","Prova","Trabalho","Prazo","Evento","Outro"]),("descricao","Descrição",None)]
    },
    "biblioteca": {
        "titulo":"Biblioteca", "subtitulo":"Organize livros, artigos e outras referências acadêmicas.",
        "tabela":"biblioteca", "nome":"item", "novo":"+ Novo item", "abrir":"Abrir link", "abrir_campo":"link",
        "colunas":("ID","Título","Autor","Categoria","Status"), "larguras":(50,250,190,140,120), "select":"id,titulo,autor,categoria,status", "ordem":"titulo",
        "campos":[("titulo","Título",None),("autor","Autor",None),("categoria","Categoria",None),("status","Status",["Disponível","Lido","Lendo","Favorito"]),("link","Link",None)]
    },
    "notas": {
        "titulo":"Notas e desempenho", "subtitulo":"Suas notas são calculadas somente a partir dos seus próprios registros.",
        "tabela":"notas", "nome":"nota", "novo":"+ Nova nota", "colunas":("ID","Disciplina","Atividade","Nota","Máximo","Semestre"),
        "larguras":(50,180,230,80,80,100), "select":"id,disciplina,atividade,nota,valor_maximo,semestre", "ordem":"disciplina,atividade",
        "campos":[("disciplina","Disciplina",None),("atividade","Atividade",None),("nota","Nota",None),("valor_maximo","Valor máximo",None),("semestre","Semestre",None)]
    }
}


def mostrar_secao(chave):
    cfg=CONFIG[chave]; limpar(conteudo); cabecalho(cfg["titulo"],cfg["subtitulo"])
    painel = painel_secao()
    barra=tk.Frame(painel,bg=BRANCO); barra.pack(fill="x",padx=18,pady=18)
    tree_ref={}
    resumo = None
    if chave == "notas":
        resumo = tk.Label(painel, text="", bg=BRANCO, fg=TEXTO, font=("Arial", 12, "bold"))
        resumo.pack(anchor="w", padx=18, pady=(0, 10))
    tree_frame, tree=criar_tree(painel,cfg["colunas"],cfg["larguras"]); tree_frame.pack(fill="both",expand=True,padx=18,pady=(0,18)); tree_ref["tree"]=tree
    botao(barra,cfg["novo"],lambda: abrir_editor(chave,tree),16 if chave=="materiais" else 15,True).pack(side="left")
    if cfg.get("abrir"):
        botao(barra,cfg["abrir"],lambda: abrir_item(tree,chave),18 if chave=="materiais" else 13).pack(side="left",padx=8)
    botao(barra,"Editar",lambda: editar_item(tree,chave),12).pack(side="left",padx=8 if cfg.get("abrir") else 8)
    botao(barra,"Excluir",lambda: excluir_item(tree,cfg["tabela"],cfg["nome"]),12).pack(side="left")
    carregar_tree(tree,chave)
    if resumo is not None:
        atualizar_resumo(resumo)


def carregar_tree(tree,chave):
    cfg=CONFIG[chave]; tree.delete(*tree.get_children())
    with conectar() as conn:
        rows=conn.execute(f"SELECT {cfg['select']} FROM {cfg['tabela']} WHERE usuario_id=? ORDER BY {cfg['ordem']}",(usuario_id_atual(),)).fetchall()
    for row in rows:
        vals=[]
        for coluna in cfg["colunas"]:
            campo_sql={"ID":"id","Título":"titulo","Disciplina":"disciplina","Tipo":"tipo","Descrição":"descricao","Data":"data","Status":"status","Nota":"nota","Hora":"hora","Autor":"autor","Categoria":"categoria","Atividade":"atividade","Máximo":"valor_maximo","Semestre":"semestre"}[coluna]
            valor=row[campo_sql]
            if chave=="avaliacoes" and campo_sql=="nota" and valor is not None: valor=f"{valor:.2f}"
            if chave=="notas" and campo_sql in ("nota","valor_maximo"): valor=f"{valor:.2f}"
            vals.append(valor)
        tree.insert("","end",iid=str(row["id"]),values=vals)


def abrir_editor(chave,tree,item_id=None):
    cfg=CONFIG[chave]; dados=None
    if item_id:
        with conectar() as conn:
            dados=conn.execute(f"SELECT * FROM {cfg['tabela']} WHERE id=? AND usuario_id=?",(item_id,usuario_id_atual())).fetchone()
    refs={}
    def montar(area):
        for nome,label,opcoes in cfg["campos"]:
            valor=dados[nome] if dados else ("10" if nome=="valor_maximo" else "Atual" if nome=="semestre" else "")
            refs[nome]=combo(area,label,opcoes,valor) if opcoes else campo(area,label,valor)
        if chave=="materiais":
            def selecionar():
                caminho=filedialog.askopenfilename()
                if caminho: refs["caminho"].delete(0,tk.END); refs["caminho"].insert(0,caminho)
            botao(area,"Selecionar arquivo",selecionar,18).pack(anchor="w",pady=8)
    def salvar():
        valores=[]
        for nome,_,_ in cfg["campos"]:
            valor=refs[nome].get().strip() if hasattr(refs[nome],"get") else refs[nome].get()
            valores.append(valor)
        if not validar(chave,refs,valores): return False
        nomes=[c[0] for c in cfg["campos"]]
        if chave=="avaliacoes": valores[-1]=float(valores[-1].replace(",",".")) if valores[-1] else None
        if chave=="notas":
            try: valores[2]=float(valores[2].replace(",",".")); valores[3]=float(valores[3].replace(",","."))
            except ValueError: messagebox.showwarning("Atenção","Nota e valor máximo precisam ser numéricos."); return False
        with conectar() as conn:
            if item_id:
                conn.execute(f"UPDATE {cfg['tabela']} SET {','.join(n+'=?' for n in nomes)} WHERE id=? AND usuario_id=?",(*valores,item_id,usuario_id_atual()))
            else:
                conn.execute(f"INSERT INTO {cfg['tabela']} (usuario_id,{','.join(nomes)}) VALUES (?,{','.join('?' for _ in nomes)})",(usuario_id_atual(),*valores))
        carregar_tree(tree,chave)
        return True
    formulario(("Editar " if item_id else "Novo ")+cfg["nome"],montar,salvar)


def validar(chave,refs,valores):
    if chave=="materiais" and not valores[0]: messagebox.showwarning("Atenção","Informe o título do material."); return False
    if chave=="avaliacoes":
        if not valores[0]: messagebox.showwarning("Atenção","Informe o título da avaliação."); return False
        if valores[-1]:
            try: float(valores[-1].replace(",","."))
            except ValueError: messagebox.showwarning("Atenção","A nota precisa ser numérica."); return False
    if chave=="agenda" and not valores[0]: messagebox.showwarning("Atenção","Informe o título do evento."); return False
    if chave=="biblioteca" and not valores[0]: messagebox.showwarning("Atenção","Informe o título."); return False
    if chave=="notas":
        if not valores[0] or not valores[1]: messagebox.showwarning("Atenção","Informe a disciplina e a atividade."); return False
        try:
            nota=float(valores[2].replace(",",".")); maximo=float(valores[3].replace(",","."))
            if maximo<=0: raise ValueError
        except ValueError: messagebox.showwarning("Atenção","Nota e valor máximo precisam ser numéricos e o máximo deve ser maior que zero."); return False
    return True


def editar_item(tree,chave):
    sel=tree.selection()
    if not sel: messagebox.showinfo(CONFIG[chave]["titulo"],f"Selecione {CONFIG[chave]['nome']}."); return
    abrir_editor(chave,tree,int(sel[0]))


def excluir_item(tree,tabela,nome):
    sel=tree.selection()
    if not sel: messagebox.showinfo("Exclusão",f"Selecione {nome} para excluir."); return
    if not messagebox.askyesno("Confirmar exclusão",f"Tem certeza que deseja excluir este {nome}?"): return
    with conectar() as conn: conn.execute(f"DELETE FROM {tabela} WHERE id=? AND usuario_id=?",(int(sel[0]),usuario_id_atual()))
    tree.delete(sel[0])


def abrir_item(tree,chave):
    sel=tree.selection()
    if not sel: messagebox.showinfo("Abrir","Selecione um item primeiro."); return
    campo_sql=CONFIG[chave].get("abrir_campo")
    if not campo_sql: return
    with conectar() as conn:
        row=conn.execute(f"SELECT {campo_sql} FROM {CONFIG[chave]['tabela']} WHERE id=? AND usuario_id=?",(int(sel[0]),usuario_id_atual())).fetchone()
    abrir_caminho(row[campo_sql] if row else "")


def atualizar_resumo(label):
    with conectar() as conn:
        row=conn.execute("SELECT AVG(nota/valor_maximo*100) media, COUNT(*) quantidade FROM notas WHERE usuario_id=?",(usuario_id_atual(),)).fetchone()
    label.config(text="Nenhuma nota cadastrada ainda." if row["media"] is None else f"Média relativa: {row['media']:.1f}%   •   Registros: {row['quantidade']}")


#PERFIL
def mostrar_perfil():
    limpar(conteudo); dados=obter_usuario(usuario_atual)
    cabecalho("Meu perfil","Atualize os dados básicos da sua conta.")
    painel=tk.Frame(conteudo,bg=BRANCO,highlightbackground=BORDA,highlightthickness=1); painel.pack(fill="x",padx=35,pady=(0,25))
    area=tk.Frame(painel,bg=BRANCO); area.pack(fill="x",padx=25,pady=25)
    for titulo,valor,tamanho in (("Usuário",dados["usuario"],14),("Tipo da conta",dados["tipo"],11)):
        tk.Label(area,text=titulo,bg=BRANCO,fg=TEXTO_SEC,font=("Arial",9,"bold")).pack(anchor="w")
        tk.Label(area,text=valor,bg=BRANCO,fg=TEXTO,font=("Arial",tamanho,"bold" if tamanho==14 else "normal")).pack(anchor="w",pady=(2,12))
    entrada=campo(area,"Curso",dados["curso"])
    botao(area,"Salvar alterações",lambda: salvar_perfil(entrada),20,True).pack(anchor="w",pady=(15,5))
    botao(area,"Alterar senha",alterar_senha,20).pack(anchor="w",pady=5)


def salvar_perfil(entrada):
    curso=entrada.get().strip() or "Curso não informado"
    with conectar() as conn: conn.execute("UPDATE usuarios SET curso=? WHERE id=?",(curso,usuario_id_atual()))
    messagebox.showinfo("Perfil","Dados atualizados com sucesso."); criar_dashboard()


def alterar_senha():
    def montar(area):
        refs["atual"]=campo(area,"Senha atual",senha=True); refs["nova"]=campo(area,"Nova senha",senha=True); refs["confirmar"]=campo(area,"Confirmar nova senha",senha=True)
    refs={}
    def salvar():
        dados=obter_usuario(usuario_atual); atual,nova,conf=(refs[x].get() for x in ("atual","nova","confirmar"))
        if dados["senha_hash"]!=hash_senha(atual): messagebox.showwarning("Atenção","A senha atual está incorreta."); return False
        if len(nova)<4: messagebox.showwarning("Atenção","A nova senha deve possuir pelo menos 4 caracteres."); return False
        if nova!=conf: messagebox.showwarning("Atenção","A confirmação da nova senha não confere."); return False
        with conectar() as conn: conn.execute("UPDATE usuarios SET senha_hash=? WHERE id=?",(hash_senha(nova),usuario_id_atual()))
        messagebox.showinfo("Senha","Senha alterada com sucesso."); return True
    formulario("Alterar senha",montar,salvar,"420x300")


#EXECUÇÃO
if __name__ == "__main__":
    inicializar_banco()
    janela=tk.Tk(); janela.title("UNIMAPP • Universidade de Marília"); janela.geometry("1180x720"); janela.minsize(980,650); janela.configure(bg=FUNDO)
    style=ttk.Style()
    try: style.theme_use("clam")
    except tk.TclError: pass
    style.configure("Treeview",rowheight=32,font=("Arial",9)); style.configure("Treeview.Heading",font=("Arial",9,"bold"))
    criar_tela_login(); janela.mainloop()
