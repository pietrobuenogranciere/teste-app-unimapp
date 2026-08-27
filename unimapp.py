#tentativa n° sei lá
#descrições dos comandos feito por IA para mim não esquecer o que significa cada coisa, como json, radialbutton, etc. e etc

import json
import tkinter as tk

COR_AZUL = "#003B73"
COR_AZUL_CLARO = "#006BB6"
COR_BRANCA = "white"
COR_ERRO = "#B00020"
COR_SUCESSO = "#16803C"

TEXTO_IMAGEM = "COLOCAR\nLOGO UNIMAR"
ARQUIVO_USUARIOS = "usuarios.json"


# JSON serve para guardar as contas mesmo depois de fechar o programa.
# O arquivo usuarios.json será criado automaticamente ao cadastrar alguém.

def carregar_usuarios():
    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        # Conta de teste
        return {
            "aluno": {
                "senha": "1234",
                "tipo": "Aluno"
            }
        }


def salvar_usuarios():
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=4)


# Cada usuário terá uma senha e um tipo de conta.
usuarios = carregar_usuarios()


def mostrar_mensagem(texto, cor):
    """Mostra uma mensagem na tela, sem abrir uma janela extra."""
    mensagem.config(text=texto, fg=cor)


def limpar_campos():
    """Apaga o que foi digitado nos dois campos."""
    entrada_usuario.delete(0, tk.END)
    entrada_senha.delete(0, tk.END)
    entrada_usuario.focus()


def entrar():
    """Confere se o usuário existe e se a senha está correta."""
    usuario = entrada_usuario.get().strip()
    senha = entrada_senha.get().strip()

    if usuario == "" or senha == "":
        mostrar_mensagem("Preencha o usuário e a senha.", COR_ERRO)

    elif usuario not in usuarios:
        mostrar_mensagem("Usuário não encontrado. Crie uma conta primeiro.", COR_ERRO)

    elif usuarios[usuario]["senha"] != senha:
        mostrar_mensagem("Senha incorreta para o usuário " + usuario + ".", COR_ERRO)

    else:
        tipo = usuarios[usuario]["tipo"]
        mostrar_mensagem(
            "Login realizado! Bem-vindo(a), " + usuario + " (" + tipo + ")!",
            COR_SUCESSO
        )
        limpar_campos()


def criar_conta():
    """Adiciona um novo usuário ao dicionário de usuários."""
    usuario = entrada_usuario.get().strip()
    senha = entrada_senha.get().strip()

    if usuario == "" or senha == "":
        mostrar_mensagem("Digite um usuário e uma senha para criar a conta.", COR_ERRO)

    elif usuario in usuarios:
        mostrar_mensagem("Este usuário já existe. Escolha outro nome.", COR_ERRO)

    else:
        usuarios[usuario] = {
            "senha": senha,
            "tipo": tipo_conta.get()
        }
        salvar_usuarios()
        mostrar_mensagem("Conta criada! Agora clique em Entrar.", COR_SUCESSO)
        limpar_campos()


# -----------------------------------------------------------------------------
# JANELA PRINCIPAL
# O mainloop(), no final do código, mantém o aplicativo aberto.
# -----------------------------------------------------------------------------

janela = tk.Tk()
janela.title("UNIMAPP")
janela.geometry("1000x600")
janela.minsize(850, 520)
janela.configure(bg=COR_BRANCA)


lado_esquerdo = tk.Frame(janela, bg=COR_AZUL, width=500)
lado_esquerdo.pack(side="left", fill="both", expand=True)

tk.Label(
    lado_esquerdo,
    text="UNIMAR",
    bg=COR_AZUL,
    fg=COR_BRANCA,
    font=("Arial", 16, "bold")
).pack(anchor="w", padx=55, pady=(70, 15))

# Este Label é o espaço reservado para a sua imagem ou logo.
# Mais tarde, você pode trocar este Label por uma imagem feita por você.
espaco_imagem = tk.Label(
    lado_esquerdo,
    text=TEXTO_IMAGEM,
    bg="#15548E",
    fg=COR_BRANCA,
    font=("Arial", 12, "bold"),
    width=28,
    height=7,
    justify="center"
)
espaco_imagem.pack(padx=55, pady=(10, 25))

tk.Label(
    lado_esquerdo,
    text="UNIMAPP",
    bg=COR_AZUL,
    fg=COR_BRANCA,
    font=("Arial", 31, "bold")
).pack(anchor="w", padx=55)

tk.Label(
    lado_esquerdo,
    text="Seu espaço acadêmico em um só lugar.",
    bg=COR_AZUL,
    fg="#D6E9FF",
    font=("Arial", 13)
).pack(anchor="w", padx=55, pady=(8, 0))

tk.Label(
    lado_esquerdo,
    text="Projeto Jovem Programador • Bootcamp 2026",
    bg=COR_AZUL,
    fg="#C1DDF4",
    font=("Arial", 9)
).pack(side="bottom", pady=30)


lado_direito = tk.Frame(janela, bg=COR_BRANCA, width=500)
lado_direito.pack(side="right", fill="both", expand=True)

formulario = tk.Frame(lado_direito, bg=COR_BRANCA)
formulario.pack(expand=True)

tk.Label(
    formulario,
    text="Acesse o UNIMAPP",
    bg=COR_BRANCA,
    fg=COR_AZUL,
    font=("Arial", 25, "bold")
).pack(anchor="w")

tk.Label(
    formulario,
    text="Insira seu login para continuar.",
    bg=COR_BRANCA,
    fg="#5B6573",
    font=("Arial", 11)
).pack(anchor="w", pady=(7, 25))

tk.Label(
    formulario,
    text="Usuário",
    bg=COR_BRANCA,
    fg="#1D2A3A",
    font=("Arial", 11, "bold")
).pack(anchor="w")

entrada_usuario = tk.Entry(formulario, width=32, font=("Arial", 12))
entrada_usuario.pack(ipady=7, pady=(5, 18))

tk.Label(
    formulario,
    text="Senha",
    bg=COR_BRANCA,
    fg="#1D2A3A",
    font=("Arial", 11, "bold")
).pack(anchor="w")

entrada_senha = tk.Entry(formulario, width=32, font=("Arial", 12), show="*")
entrada_senha.pack(ipady=7, pady=(5, 20))

# Radiobutton: o tipo selecionado será salvo somente ao criar uma nova conta.
tk.Label(
    formulario,
    text="Tipo da nova conta",
    bg=COR_BRANCA,
    fg="#1D2A3A",
    font=("Arial", 11, "bold")
).pack(anchor="w")

tipo_conta = tk.StringVar()
tipo_conta.set("Aluno")

opcoes_tipo = tk.Frame(formulario, bg=COR_BRANCA)
opcoes_tipo.pack(anchor="w", pady=(5, 18))

tk.Radiobutton(
    opcoes_tipo,
    text="Aluno",
    variable=tipo_conta,
    value="Aluno",
    bg=COR_BRANCA,
    activebackground=COR_BRANCA
).pack(side="left")

tk.Radiobutton(
    opcoes_tipo,
    text="Professor",
    variable=tipo_conta,
    value="Professor",
    bg=COR_BRANCA,
    activebackground=COR_BRANCA
).pack(side="left", padx=(15, 0))

tk.Button(
    formulario,
    text="Entrar",
    bg=COR_AZUL_CLARO,
    fg=COR_BRANCA,
    activebackground=COR_AZUL,
    activeforeground=COR_BRANCA,
    font=("Arial", 11, "bold"),
    width=28,
    command=entrar
).pack(pady=(0, 8))

tk.Button(
    formulario,
    text="Criar conta",
    bg=COR_BRANCA,
    fg=COR_AZUL,
    font=("Arial", 11, "bold"),
    width=28,
    command=criar_conta
).pack()

# As mensagens de sucesso e erro aparecem aqui, dentro do aplicativo.
mensagem = tk.Label(
    formulario,
    text="",
    bg=COR_BRANCA,
    font=("Arial", 10),
    wraplength=290,
    justify="center"
)
mensagem.pack(pady=(18, 0))


# Deixa o cursor pronto no campo de usuário quando o app abre.
entrada_usuario.focus()

# Mantém a janela aberta. Sem esta linha, ela fecha logo depois de iniciar.
janela.mainloop()
