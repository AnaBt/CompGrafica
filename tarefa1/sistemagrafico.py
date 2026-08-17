import tkinter as tk

# Cria a janela principal
janela = tk.Tk()
janela.title("Minha Primeira Janela")
janela.geometry("800x700")

canvas = tk.Canvas(
    janela,
    width=800,
    height=600,
    bg="white"
)

canvas.pack(side="top")

xvpmin = 200
yvpmin = 0
xvpmax = 800
yvpmax = 800

view = canvas.create_rectangle(
    xvpmin,
    yvpmin,
    xvpmax,
    yvpmax,
    fill="blue"
)

xw, yw = 500, 500

xwmin = 0
ywmin = 0
xwmax = 800
ywmax = 800

def desenhar():

    # Apaga o ponto anterior
    canvas.delete("ponto")

    # Transformação X
    xvp = xvpmin + (
        (xw - xwmin) / (xwmax - xwmin)
    ) * (xvpmax - xvpmin)

    # Transformação Y
    yvp = yvpmin + (
        1 - (yw - ywmin) / (ywmax - ywmin)
    ) * (yvpmax - yvpmin)

    raio = 3

    canvas.create_oval(
        xvp - raio,
        yvp - raio,
        xvp + raio,
        yvp + raio,
        fill="black",
        outline="black",
        tags="ponto"
    )

def esquerda():
    global xwmin, xwmax

    xwmin -= 50
    xwmax -= 50

    desenhar()


def direita():
    global xwmin, xwmax

    xwmin += 50
    xwmax += 50

    desenhar()


def cima():
    global ywmin, ywmax

    ywmin += 50
    ywmax += 50

    desenhar()


def baixo():
    global ywmin, ywmax

    ywmin -= 50
    ywmax -= 50

    desenhar()


# Desenha inicialmente
desenhar()

frame_botoes = tk.Frame(janela)
frame_botoes.pack(side="bottom", pady=10)


botao_cima = tk.Button(
    frame_botoes,
    text="↑",
    width=5,
    command=cima
)

botao_cima.grid(row=0, column=1, padx=3, pady=3)


botao_esquerda = tk.Button(
    frame_botoes,
    text="←",
    width=5,
    command=esquerda
)

botao_esquerda.grid(row=1, column=0, padx=3, pady=3)


botao_baixo = tk.Button(
    frame_botoes,
    text="↓",
    width=5,
    command=baixo
)

botao_baixo.grid(row=1, column=1, padx=3, pady=3)


botao_direita = tk.Button(
    frame_botoes,
    text="→",
    width=5,
    command=direita
)

botao_direita.grid(row=1, column=2, padx=3, pady=3)

janela.mainloop()