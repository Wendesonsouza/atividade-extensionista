
import sqlite3

import tkinter as tk

from tkinter import messagebox, ttk

from PIL import Image, ImageTk

# Banco de dados

conn = sqlite3.connect("financeiro.db")

cursor = conn.cursor()

# Tabela de usuários

cursor.execute(""" 

CREATE TABLE IF NOT EXISTS usuarios ( 

    id INTEGER PRIMARY KEY AUTOINCREMENT, 

    usuario TEXT UNIQUE NOT NULL, 

    senha TEXT NOT NULL 

) 

""")

# Tabela de transações

cursor.execute(""" 

CREATE TABLE IF NOT EXISTS transacoes ( 

    id INTEGER PRIMARY KEY AUTOINCREMENT, 

    tipo TEXT NOT NULL, 

    valor REAL NOT NULL, 

    comentario TEXT 

) 

""")

conn.commit()


# Funções

def abrir_principal():
    login_window.destroy()

    root = tk.Tk()

    root.title("Gestão Financeira")

    root.geometry("1000x700")

    root.configure(bg="#f0f2f5")

    # Label de saldo

    saldo_label = tk.Label(root, text="Saldo Atual: R$ 0.00",

                           font=("Arial", 22, "bold"), bg="#f0f2f5", fg="#333")

    saldo_label.pack(pady=20)

    # Frame para inputs

    frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")

    frame.pack(pady=20, padx=20, fill="x")

    tk.Label(frame, text="Valor:", font=("Arial", 14), bg="#ffffff").grid(row=0, column=0, padx=10, pady=10)

    valor_entry = tk.Entry(frame, font=("Arial", 14))

    valor_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(frame, text="Comentário:", font=("Arial", 14), bg="#ffffff").grid(row=1, column=0, padx=10, pady=10)

    comentario_entry = tk.Entry(frame, font=("Arial", 14), width=40)

    comentario_entry.grid(row=1, column=1, padx=10, pady=10)

    # Treeview para listar transações

    tree = ttk.Treeview(root, columns=("ID", "Tipo", "Valor", "Comentário"), show="headings", height=10)

    tree.heading("ID", text="ID")

    tree.heading("Tipo", text="Tipo")

    tree.heading("Valor", text="Valor (R$)")

    tree.heading("Comentário", text="Comentário")

    tree.column("ID", width=50, anchor="center")

    tree.column("Tipo", width=100, anchor="center")

    tree.column("Valor", width=150, anchor="center")

    tree.column("Comentário", width=600, anchor="w")

    tree.pack(pady=20, fill="x")

    # Atualizar saldo e lista

    def atualizar_saldo_e_lista():

        cursor.execute("SELECT SUM(CASE WHEN tipo='entrada' THEN valor ELSE -valor END) FROM transacoes")

        saldo = cursor.fetchone()[0]

        if saldo is None:
            saldo = 0.0

        saldo_label.config(text=f"Saldo Atual: R$ {saldo:.2f}")

        # Atualizar lista

        for item in tree.get_children():
            tree.delete(item)

        cursor.execute("SELECT id, tipo, valor, comentario FROM transacoes ORDER BY id DESC")

        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

            # Registrar transações

    def registrar(tipo):

        try:

            valor = float(valor_entry.get())

            comentario = comentario_entry.get()

            cursor.execute("INSERT INTO transacoes (tipo, valor, comentario) VALUES (?, ?, ?)",

                           (tipo, valor, comentario))

            conn.commit()

            atualizar_saldo_e_lista()

            valor_entry.delete(0, tk.END)

            comentario_entry.delete(0, tk.END)

            messagebox.showinfo("Sucesso", f"{tipo.capitalize()} registrada!")

        except ValueError:

            messagebox.showerror("Erro", "Digite um valor válido!")

            # Função para apagar registro

    def apagar_registro():

        selecionado = tree.selection()

        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um registro para apagar!")

            return

        item = tree.item(selecionado)

        valores = item["values"]

        transacao_id = valores[0]  # Pegando o ID da transação

        if messagebox.askyesno("Confirmar", f"Deseja apagar o registro ID {transacao_id}?"):
            cursor.execute("DELETE FROM transacoes WHERE id=?", (transacao_id,))

            conn.commit()

            atualizar_saldo_e_lista()

            messagebox.showinfo("Sucesso", "Registro apagado com sucesso!")

            # Botões modernos

    btn_entrada = tk.Button(root, text="Registrar Entrada", command=lambda: registrar("entrada"),

                            bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), width=20)

    btn_saida = tk.Button(root, text="Registrar Saída", command=lambda: registrar("saida"),

                          bg="#F44336", fg="white", font=("Arial", 14, "bold"), width=20)

    btn_apagar = tk.Button(root, text="Apagar Registro Selecionado", command=apagar_registro,

                           bg="#FF9800", fg="white", font=("Arial", 14, "bold"), width=25)

    btn_entrada.pack(pady=10)

    btn_saida.pack(pady=10)

    btn_apagar.pack(pady=10)

    atualizar_saldo_e_lista()

    root.mainloop()


def verificar_login():
    usuario = usuario_entry.get()

    senha = senha_entry.get()

    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))

    if cursor.fetchone():

        abrir_principal()

    else:

        messagebox.showerror("Erro", "Usuário ou senha inválidos!")


def abrir_cadastro():
    cadastro_window = tk.Toplevel(login_window)

    cadastro_window.title("Cadastrar Conta")

    tk.Label(cadastro_window, text="Novo Usuário:").pack()

    novo_usuario = tk.Entry(cadastro_window)

    novo_usuario.pack()

    tk.Label(cadastro_window, text="Senha:").pack()

    nova_senha = tk.Entry(cadastro_window, show="*")

    nova_senha.pack()

    def salvar_usuario():

        try:

            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",

                           (novo_usuario.get(), nova_senha.get()))

            conn.commit()

            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")

            cadastro_window.destroy()

        except sqlite3.IntegrityError:

            messagebox.showerror("Erro", "Usuário já existe!")

    tk.Button(cadastro_window, text="Salvar", command=salvar_usuario).pack(pady=10)


# Tela de login

login_window = tk.Tk()

login_window.title("Login - Gestão Financeira")

# Pegar resolução da tela

screen_width = login_window.winfo_screenwidth()

screen_height = login_window.winfo_screenheight()

# Tela cheia

login_window.geometry(f"{screen_width}x{screen_height}+0+0")

# Carregar imagem de fundo

try:

    img = Image.open("imagen.jpeg")

    img = img.resize((screen_width, screen_height))

    bg = ImageTk.PhotoImage(img)

    canvas = tk.Canvas(login_window, width=screen_width, height=screen_height)

    canvas.pack(fill="both", expand=True)

    canvas.create_image(0, 0, image=bg, anchor="nw")

    # Campos de login

    usuario_entry = tk.Entry(login_window, font=("Arial", 14))

    senha_entry = tk.Entry(login_window, show="*", font=("Arial", 14))

    canvas.create_window(screen_width // 2, screen_height // 2 - 60,

                         window=tk.Label(login_window, text="Usuário:", bg="white", font=("Arial", 14)))

    canvas.create_window(screen_width // 2, screen_height // 2 - 30, window=usuario_entry)

    canvas.create_window(screen_width // 2, screen_height // 2 + 10,

                         window=tk.Label(login_window, text="Senha:", bg="white", font=("Arial", 14)))

    canvas.create_window(screen_width // 2, screen_height // 2 + 40, window=senha_entry)

    # Botões destacados

    btn_login = tk.Button(login_window, text="Entrar", command=verificar_login,

                          bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), width=15)

    btn_cadastro = tk.Button(login_window, text="Cadastrar Conta", command=abrir_cadastro,

                             bg="#2196F3", fg="white", font=("Arial", 14, "bold"), width=15)

    canvas.create_window(screen_width // 2, screen_height // 2 + 100, window=btn_login)

    canvas.create_window(screen_width // 2, screen_height // 2 + 150, window=btn_cadastro)



except Exception as e:

    tk.Label(login_window, text="Erro ao carregar imagem: " + str(e)).pack()

login_window.mainloop()

conn.close()


