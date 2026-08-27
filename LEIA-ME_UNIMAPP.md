# UNIMAPP — versão para estudar

Este é um modelo simples feito com conteúdo de início de Python e Tkinter:

- Variáveis e constantes;
- Dicionário (`usuarios`) e um arquivo JSON simples;
- Funções (`entrar`, `criar_conta`, `limpar_campos`);
- Condições `if`, `elif` e `else`;
- Widgets básicos: `Tk`, `Frame`, `Label`, `Entry`, `Button` e `Radiobutton`.

## Como executar

No terminal aberto na pasta `outputs`, execute:

```powershell
py unimapp.py
```

Se esse comando não funcionar, tente:

```powershell
python unimapp.py
```

## Como testar

Você pode criar sua própria conta usando os dois campos e o botão **Criar conta**. Depois, digite os mesmos dados e clique em **Entrar**.

Também existe uma conta somente para teste:

```text
Usuário: aluno
Senha: 1234
```

As contas são salvas no arquivo `usuarios.json` quando você clica em **Criar conta**. Assim, elas continuam existindo depois de fechar o programa. O JSON usado é pequeno: ele guarda apenas o nome do usuário, a senha de demonstração e o tipo de conta.

Ao criar uma conta, escolha **Aluno** ou **Professor** nos dois `Radiobutton`s. Essa escolha aparece na mensagem depois do login.

## O que você pode personalizar

- Altere as variáveis de cor no começo do arquivo;
- Troque os textos dos `Label`s;
- Use o espaço `TEXTO_IMAGEM` para colocar seu logo/imagem depois;
- Remova ou altere a conta de teste no dicionário `usuarios`.

Não use senhas reais: este é apenas um projeto demonstrativo local.
