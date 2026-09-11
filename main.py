import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


# ============================================================
# BANCO DE DADOS
# ============================================================

conexao = sqlite3.connect("produtos.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    produto TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco REAL NOT NULL,
    estoque INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Ativo'
)
""")

conexao.commit()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def limpar_campos():
    entrada_codigo.delete(0, tk.END)
    entrada_produto.delete(0, tk.END)
    entrada_categoria.delete(0, tk.END)
    entrada_preco.delete(0, tk.END)
    entrada_estoque.delete(0, tk.END)


def formatar_preco(valor):
    """Formata o preço no padrão brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def converter_preco(valor):
    """Converte diferentes formatos de preço para número."""
    valor = valor.replace("R$", "").strip()

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    return float(valor)


def obter_dados_formulario():
    """Obtém e valida os dados preenchidos no formulário."""

    codigo = entrada_codigo.get().strip()
    produto = entrada_produto.get().strip()
    categoria = entrada_categoria.get().strip()
    preco = entrada_preco.get().strip()
    estoque = entrada_estoque.get().strip()

    if not codigo or not produto or not categoria or not preco or not estoque:
        messagebox.showwarning(
            "Atenção",
            "Preencha todos os campos."
        )
        return None

    try:
        preco = converter_preco(preco)
        estoque = int(estoque)

    except ValueError:
        messagebox.showerror(
            "Erro",
            "Informe um preço e um estoque válidos."
        )
        return None

    if preco < 0:
        messagebox.showerror(
            "Erro",
            "O preço não pode ser negativo."
        )
        return None

    if estoque < 0:
        messagebox.showerror(
            "Erro",
            "O estoque não pode ser negativo."
        )
        return None

    return codigo, produto, categoria, preco, estoque


# ============================================================
# CADASTRAR PRODUTO
# ============================================================

def cadastrar():
    dados = obter_dados_formulario()

    if dados is None:
        return

    codigo, produto, categoria, preco, estoque = dados

    try:

        cursor.execute("""
            INSERT INTO produtos
            (codigo, produto, categoria, preco, estoque)
            VALUES (?, ?, ?, ?, ?)
        """, (
            codigo,
            produto,
            categoria,
            preco,
            estoque
        ))

        conexao.commit()

        messagebox.showinfo(
            "Sucesso",
            "Produto cadastrado com sucesso."
        )

        limpar_campos()
        carregar_produtos()

    except sqlite3.IntegrityError:

        messagebox.showerror(
            "Erro",
            "Este código já está cadastrado."
        )

    except sqlite3.Error as erro:

        messagebox.showerror(
            "Erro no banco de dados",
            f"Não foi possível cadastrar o produto.\n\n{erro}"
        )


# ============================================================
# SELECIONAR PRODUTO
# ============================================================

def selecionar_produto(event):

    item = tabela.selection()

    if not item:
        return

    valores = tabela.item(item, "values")

    limpar_campos()

    entrada_codigo.insert(
        0,
        valores[0]
    )

    entrada_produto.insert(
        0,
        valores[1]
    )

    entrada_categoria.insert(
        0,
        valores[2]
    )

    entrada_preco.insert(
        0,
        valores[3]
    )

    entrada_estoque.insert(
        0,
        valores[4]
    )


# ============================================================
# EDITAR PRODUTO
# ============================================================

def editar_produto():

    item = tabela.selection()

    if not item:

        messagebox.showwarning(
            "Atenção",
            "Selecione um produto na tabela para editar."
        )

        return

    valores = tabela.item(
        item,
        "values"
    )

    status = valores[5]

    if status == "Inativo":

        messagebox.showwarning(
            "Atenção",
            "Produtos inativos não podem ser editados."
        )

        return

    dados = obter_dados_formulario()

    if dados is None:
        return

    codigo, produto, categoria, preco, estoque = dados

    try:

        cursor.execute("""
            UPDATE produtos
            SET produto = ?,
                categoria = ?,
                preco = ?,
                estoque = ?
            WHERE codigo = ?
              AND status = 'Ativo'
        """, (
            produto,
            categoria,
            preco,
            estoque,
            codigo
        ))

        conexao.commit()

        if cursor.rowcount == 0:

            messagebox.showwarning(
                "Atenção",
                "Nenhum produto ativo foi encontrado."
            )

            return

        messagebox.showinfo(
            "Sucesso",
            "Produto atualizado com sucesso."
        )

        limpar_campos()
        carregar_produtos()

    except sqlite3.Error as erro:

        messagebox.showerror(
            "Erro no banco de dados",
            f"Não foi possível atualizar o produto.\n\n{erro}"
        )


# ============================================================
# INATIVAR PRODUTO
# ============================================================

def inativar_produto():

    item = tabela.selection()

    if not item:

        messagebox.showwarning(
            "Atenção",
            "Selecione um produto na tabela para inativar."
        )

        return

    valores = tabela.item(
        item,
        "values"
    )

    codigo = valores[0]
    status = valores[5]

    if status == "Inativo":

        messagebox.showwarning(
            "Atenção",
            "Este produto já está inativo."
        )

        return

    confirmacao = messagebox.askyesno(
        "Confirmar inativação",
        f"Deseja realmente inativar o produto:\n\n"
        f"{valores[1]}?"
    )

    if not confirmacao:
        return

    try:

        cursor.execute("""
            UPDATE produtos
            SET status = 'Inativo'
            WHERE codigo = ?
              AND status = 'Ativo'
        """, (codigo,))

        conexao.commit()

        messagebox.showinfo(
            "Sucesso",
            "Produto inativado com sucesso."
        )

        limpar_campos()
        carregar_produtos()

    except sqlite3.Error as erro:

        messagebox.showerror(
            "Erro no banco de dados",
            f"Não foi possível inativar o produto.\n\n{erro}"
        )


# ============================================================
# ATIVAR PRODUTO
# ============================================================

def ativar_produto():

    item = tabela.selection()

    if not item:

        messagebox.showwarning(
            "Atenção",
            "Selecione um produto na tabela para ativar."
        )

        return

    valores = tabela.item(
        item,
        "values"
    )

    codigo = valores[0]
    status = valores[5]

    if status == "Ativo":

        messagebox.showwarning(
            "Atenção",
            "Este produto já está ativo."
        )

        return

    confirmacao = messagebox.askyesno(
        "Confirmar ativação",
        f"Deseja realmente ativar o produto:\n\n"
        f"{valores[1]}?"
    )

    if not confirmacao:
        return

    try:

        cursor.execute("""
            UPDATE produtos
            SET status = 'Ativo'
            WHERE codigo = ?
              AND status = 'Inativo'
        """, (codigo,))

        conexao.commit()

        messagebox.showinfo(
            "Sucesso",
            "Produto ativado com sucesso."
        )

        limpar_campos()
        carregar_produtos()

    except sqlite3.Error as erro:

        messagebox.showerror(
            "Erro no banco de dados",
            f"Não foi possível ativar o produto.\n\n{erro}"
        )


# ============================================================
# CONSULTAR PRODUTOS
# ============================================================

def consultar_produtos():

    termo = entrada_consulta.get().strip()
    status = filtro_status.get()

    for item in tabela.get_children():
        tabela.delete(item)

    try:

        if status == "Todos":

            cursor.execute("""
                SELECT
                    codigo,
                    produto,
                    categoria,
                    preco,
                    estoque,
                    status
                FROM produtos
                WHERE codigo LIKE ?
                   OR produto LIKE ?
                ORDER BY id DESC
            """, (
                f"%{termo}%",
                f"%{termo}%"
            ))

        else:

            cursor.execute("""
                SELECT
                    codigo,
                    produto,
                    categoria,
                    preco,
                    estoque,
                    status
                FROM produtos
                WHERE
                    (codigo LIKE ? OR produto LIKE ?)
                    AND status = ?
                ORDER BY id DESC
            """, (
                f"%{termo}%",
                f"%{termo}%",
                status
            ))

        produtos = cursor.fetchall()

        for produto in produtos:

            codigo = produto[0]
            nome = produto[1]
            categoria = produto[2]
            preco = produto[3]
            estoque = produto[4]
            status = produto[5]

            tabela.insert(
                "",
                tk.END,
                values=(
                    codigo,
                    nome,
                    categoria,
                    formatar_preco(preco),
                    estoque,
                    status
                )
            )

    except sqlite3.Error as erro:

        messagebox.showerror(
            "Erro no banco de dados",
            f"Não foi possível realizar a consulta.\n\n{erro}"
        )


# ============================================================
# CARREGAR TODOS OS PRODUTOS
# ============================================================

def carregar_produtos():

    for item in tabela.get_children():
        tabela.delete(item)

    try:

        cursor.execute("""
            SELECT
                codigo,
                produto,
                categoria,
                preco,
                estoque,
                status
            FROM produtos
            ORDER BY id DESC
        """)

        produtos = cursor.fetchall()

        for produto in produtos:

            codigo = produto[0]
            nome = produto[1]
            categoria = produto[2]
            preco = produto[3]
            estoque = produto[4]
            status = produto[5]

            tabela.insert(
                "",
                tk.END,
                values=(
                    codigo,
                    nome,
                    categoria,
                    formatar_preco(preco),
                    estoque,
                    status
                )
            )

    except sqlite3.Error as erro:

        messagebox.showerror(
            "Erro no banco de dados",
            f"Não foi possível carregar os produtos.\n\n{erro}"
        )


# ============================================================
# JANELA PRINCIPAL
# ============================================================

janela = tk.Tk()

janela.title(
    "Sistema de Cadastro de Produtos"
)

janela.geometry(
    "1050x620"
)

janela.resizable(
    False,
    False
)


# ============================================================
# TÍTULO
# ============================================================

titulo = tk.Label(
    janela,
    text="Sistema de Cadastro de Produtos",
    font=("Arial", 20, "bold")
)

titulo.pack(
    pady=20
)


# ============================================================
# FORMULÁRIO
# ============================================================

formulario = tk.Frame(
    janela
)

formulario.pack(
    pady=5
)


tk.Label(
    formulario,
    text="Código:"
).grid(
    row=0,
    column=0,
    padx=5,
    pady=5,
    sticky="e"
)


entrada_codigo = tk.Entry(
    formulario,
    width=30
)

entrada_codigo.grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    formulario,
    text="Produto:"
).grid(
    row=1,
    column=0,
    padx=5,
    pady=5,
    sticky="e"
)


entrada_produto = tk.Entry(
    formulario,
    width=30
)

entrada_produto.grid(
    row=1,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    formulario,
    text="Categoria:"
).grid(
    row=2,
    column=0,
    padx=5,
    pady=5,
    sticky="e"
)


entrada_categoria = tk.Entry(
    formulario,
    width=30
)

entrada_categoria.grid(
    row=2,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    formulario,
    text="Preço:"
).grid(
    row=3,
    column=0,
    padx=5,
    pady=5,
    sticky="e"
)


entrada_preco = tk.Entry(
    formulario,
    width=30
)

entrada_preco.grid(
    row=3,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    formulario,
    text="Estoque:"
).grid(
    row=4,
    column=0,
    padx=5,
    pady=5,
    sticky="e"
)


entrada_estoque = tk.Entry(
    formulario,
    width=30
)

entrada_estoque.grid(
    row=4,
    column=1,
    padx=5,
    pady=5
)


# ============================================================
# CONSULTA
# ============================================================

consulta_frame = tk.Frame(
    janela
)

consulta_frame.pack(
    pady=10
)


tk.Label(
    consulta_frame,
    text="Consultar:"
).grid(
    row=0,
    column=0,
    padx=5
)


entrada_consulta = tk.Entry(
    consulta_frame,
    width=30
)

entrada_consulta.grid(
    row=0,
    column=1,
    padx=5
)


tk.Label(
    consulta_frame,
    text="Status:"
).grid(
    row=0,
    column=2,
    padx=5
)


filtro_status = ttk.Combobox(
    consulta_frame,
    values=[
        "Todos",
        "Ativo",
        "Inativo"
    ],
    state="readonly",
    width=10
)

filtro_status.set(
    "Todos"
)

filtro_status.grid(
    row=0,
    column=3,
    padx=5
)


tk.Button(
    consulta_frame,
    text="Consultar",
    width=15,
    command=consultar_produtos
).grid(
    row=0,
    column=4,
    padx=5
)


tk.Button(
    consulta_frame,
    text="Mostrar Todos",
    width=15,
    command=carregar_produtos
).grid(
    row=0,
    column=5,
    padx=5
)


# ============================================================
# BOTÕES
# ============================================================

botoes = tk.Frame(
    janela
)

botoes.pack(
    pady=10
)


tk.Button(
    botoes,
    text="Cadastrar",
    width=15,
    command=cadastrar
).grid(
    row=0,
    column=0,
    padx=5
)


tk.Button(
    botoes,
    text="Editar",
    width=15,
    command=editar_produto
).grid(
    row=0,
    column=1,
    padx=5
)


tk.Button(
    botoes,
    text="Ativar",
    width=15,
    command=ativar_produto
).grid(
    row=0,
    column=2,
    padx=5
)


tk.Button(
    botoes,
    text="Inativar",
    width=15,
    command=inativar_produto
).grid(
    row=0,
    column=3,
    padx=5
)


tk.Button(
    botoes,
    text="Limpar",
    width=15,
    command=limpar_campos
).grid(
    row=0,
    column=4,
    padx=5
)


# ============================================================
# TABELA
# ============================================================

colunas = (
    "Código",
    "Produto",
    "Categoria",
    "Preço",
    "Estoque",
    "Status"
)


tabela = ttk.Treeview(
    janela,
    columns=colunas,
    show="headings",
    height=10
)


# Largura individual das colunas

tabela.column(
    "Código",
    width=100,
    anchor="center"
)

tabela.column(
    "Produto",
    width=230,
    anchor="w"
)

tabela.column(
    "Categoria",
    width=180,
    anchor="w"
)

tabela.column(
    "Preço",
    width=130,
    anchor="center"
)

tabela.column(
    "Estoque",
    width=100,
    anchor="center"
)

tabela.column(
    "Status",
    width=120,
    anchor="center"
)


# Cabeçalhos

for coluna in colunas:

    tabela.heading(
        coluna,
        text=coluna
    )


tabela.pack(
    pady=15
)


# Permite selecionar um produto clicando na tabela

tabela.bind(
    "<<TreeviewSelect>>",
    selecionar_produto
)


# ============================================================
# INICIALIZAÇÃO
# ============================================================

carregar_produtos()


janela.mainloop()


# ============================================================
# ENCERRAMENTO
# ============================================================

conexao.close()

