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
 
xvpmin = 0 
yvpmin = 0 
xvpmax = 800 
yvpmax = 800 
 
view = canvas.create_rectangle( 
    xvpmin, 
    yvpmin, 
    xvpmax, 
    yvpmax, 
    fill="purple" 
) 
 
xw, yw = 500, 500 
 
xwmin = 0 
ywmin = 0 
xwmax = 800 
ywmax = 800 
 
formas = [ 
    { 
        "tipo": "quadrado", 
        "linhas": [ 
            ((400, 400), (500, 400)),
            ((500, 400), (500, 500)),
            ((500, 500), (400, 500)),
            ((400, 500), (400, 400))
        ] 
    }, 
    { 
        "tipo": "triangulo", 
        "linhas": [ 
            ((400, 200), (500, 200)),
            ((500, 200), (450, 300)),
            ((450, 300), (400, 200)) 
        ] 
    } 
] 
 
def transformar(xw, yw): 
    xvp = xvpmin + ( 
        (xw - xwmin) / (xwmax - xwmin) 
    ) * (xvpmax - xvpmin) 
 
    yvp = yvpmin + ( 
        1 - (yw - ywmin) / (ywmax - ywmin) 
    ) * (yvpmax - yvpmin) 
 
    return xvp, yvp 
 
def desenhar_forma(forma): 
 
    for linha in forma["linhas"]: 
 
        (x1, y1), (x2, y2) = linha 
 
        x1vp, y1vp = transformar(x1, y1) 
        x2vp, y2vp = transformar(x2, y2) 
 
        canvas.create_line( 
            x1vp, y1vp, 
            x2vp, y2vp, 
            tags="forma" 
        ) 
 
def desenhar(): 
 
    # Apaga o ponto anterior 
    canvas.delete("forma") 
    canvas.delete("ponto") 
 
    # Transformação X 
    xvp,yvp = transformar(xw,yw) 
    raio = 3 
 
    canvas.create_oval( 
        xvp - raio + 10, 
        yvp - raio + 10, 
        xvp + raio + 10, 
        yvp + raio + 10, 
        fill="black", 
        outline="black", 
        tags="ponto" 
    ) 
 
    for forma in formas: 
        desenhar_forma(forma) 

painel = tk.Frame(
    janela,
    width=400,
    height=300,
    bg="lightgray"
)

painel.pack(side="left")

titulo = tk.Label(
    painel,
    text="Objetos",
    bg="lightgray",
    font=("Arial", 12, "bold")
)

titulo.pack(pady=5)

lista_objetos = tk.Listbox(
    painel,
    font=("Arial", 10),
    selectmode=tk.SINGLE
)

lista_objetos.pack(
    fill="both",
    expand=True,
    padx=5,
    pady=5
)

for forma in formas:
    lista_objetos.insert(
        tk.END,
        forma["tipo"]
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

botao_direita.grid(
    row=1,
    column=2,
    padx=3,
    pady=3
)

 
janela.mainloop() 