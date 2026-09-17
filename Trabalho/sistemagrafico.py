import tkinter as tk 
from tkinter import messagebox

# Cria a janela principal 
janela = tk.Tk() 
janela.title("Sistema Gráfico 2D - Grupo 20") 
janela.geometry("850x700") 

canvas = tk.Canvas( 
    janela, 
    width=800, 
    height=500, 
    bg="white",
    highlightthickness=1,
    highlightbackground="gray"
) 
canvas.pack(side="top", pady=10) 

xvpmin, yvpmin = 0, 0 
xvpmax, yvpmax = 800, 500 

xw, yw = 500, 500 

xwmin, ywmin = 0, 0 
xwmax, ywmax = 800, 500 

formas = [ 
    { 
        "nome": "Quadrado Base",
        "tipo": "wireframe", 
        "linhas": [ 
            ((400, 300), (500, 300)),
            ((500, 300), (500, 400)),
            ((500, 400), (400, 400)),
            ((400, 400), (400, 300))
        ] 
    }, 
    { 
        "nome": "Triângulo Base",
        "tipo": "triangulo", 
        "linhas": [ 
            ((400, 100), (500, 100)),
            ((500, 100), (450, 200)),
            ((450, 200), (400, 100)) 
        ] 
    } 
] 

# Painel Lateral
painel = tk.Frame(janela, width=220, bg="#f0f0f0")
painel.pack(side="left", fill="y", padx=10, pady=5)

titulo = tk.Label(
    painel,
    text="Display File (Objetos)",
    bg="#f0f0f0",
    font=("Arial", 10, "bold")
)
titulo.pack(pady=5)

def transformar(xw, yw): 
    xvp = xvpmin + ((xw - xwmin) / (xwmax - xwmin)) * (xvpmax - xvpmin) 
    yvp = yvpmin + (1 - (yw - ywmin) / (ywmax - ywmin)) * (yvpmax - yvpmin) 
    return xvp, yvp 

def desenhar_forma(forma): 
    for linha in forma["linhas"]: 
        (x1, y1), (x2, y2) = linha 
        x1vp, y1vp = transformar(x1, y1) 
        x2vp, y2vp = transformar(x2, y2) 

        canvas.create_line( 
            x1vp, y1vp, x2vp, y2vp, 
            tags="forma", fill="#1a73e8", width=2
        ) 

def desenhar(): 
    canvas.delete("forma") 
    canvas.delete("ponto") 

    xvp, yvp = transformar(xw, yw) 
    raio = 3 

    canvas.create_oval( 
        xvp - raio, yvp - raio, 
        xvp + raio, yvp + raio, 
        fill="black", outline="black", 
        tags="ponto" 
    ) 

    for forma in formas: 
        desenhar_forma(forma) 

def atualizar_lista():
    lista_objetos.delete(0, tk.END)
    for forma in formas:
        lista_objetos.insert(tk.END, f"• {forma['nome']} ({forma['tipo']})")

def abrir_popup_novo_objeto():
    popup = tk.Toplevel(janela)
    popup.title("Novo Objeto")
    popup.geometry("350x220")
    popup.resizable(False, False)
    popup.grab_set()

    tk.Label(popup, text="Nome do Objeto:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(15, 2))
    e_nome = tk.Entry(popup, font=("Arial", 10))
    e_nome.pack(fill="x", padx=15, pady=2)

    tk.Label(popup, text="Coordenadas: (x1,y1),(x2,y2)...", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
    e_coords = tk.Entry(popup, font=("Arial", 10))
    e_coords.pack(fill="x", padx=15, pady=2)

    def salvar():
        nome = e_nome.get().strip() or f"Objeto {len(formas) + 1}"
        raw_coords = e_coords.get().strip()
        
        if not raw_coords:
            messagebox.showwarning("Aviso", "Informe as coordenadas!")
            return
            
        try:
            pontos = list(eval(f"[{raw_coords}]"))
            if len(pontos) == 1:
                tipo = "ponto"
                linhas = [(pontos[0], pontos[0])]
            elif len(pontos) == 2:
                tipo = "reta"
                linhas = [(pontos[0], pontos[1])]
            else:
                tipo = "wireframe"
                linhas = [
                    (pontos[i], pontos[(i + 1) % len(pontos)]) 
                    for i in range(len(pontos))
                ]
                
            formas.append({"nome": nome, "tipo": tipo, "linhas": linhas})
            atualizar_lista()
            desenhar()
            popup.destroy()
            
        except Exception:
            messagebox.showerror("Erro", "Formato incorreto!\nExemplo: (100,100),(200,200),(150,300)")

    tk.Button(
        popup, 
        text="Salvar Objeto", 
        bg="#1a73e8", 
        fg="white", 
        font=("Arial", 9, "bold"),
        command=salvar
    ).pack(pady=15)

btn_abrir_popup = tk.Button(
    painel, 
    text="+ Novo Objeto", 
    bg="#1a73e8", 
    fg="white",
    font=("Arial", 9, "bold"),
    command=abrir_popup_novo_objeto
)
btn_abrir_popup.pack(pady=5, fill="x", padx=5)

lista_objetos = tk.Listbox(
    painel,
    font=("Arial", 9),
    selectmode=tk.SINGLE
)
lista_objetos.pack(fill="both", expand=True, padx=5, pady=5)

def esquerda(): 
    global xwmin, xwmax 
    xwmin -= 50; xwmax -= 50 
    desenhar() 

def direita(): 
    global xwmin, xwmax 
    xwmin += 50; xwmax += 50 
    desenhar() 
 
 
def cima(): 
    global ywmin, ywmax 
    ywmin += 50; ywmax += 50 
    desenhar() 
 
 
def baixo(): 
    global ywmin, ywmax 
    ywmin -= 50; ywmax -= 50 
    desenhar() 

def zoom_in():
    global xwmin, xwmax, ywmin, ywmax
    fator = 0.9  
    cx, cy = (xwmin + xwmax) / 2, (ywmin + ywmax) / 2
    largura, altura = (xwmax - xwmin) * fator, (ywmax - ywmin) * fator
    xwmin, xwmax = cx - largura / 2, cx + largura / 2
    ywmin, ywmax = cy - altura / 2, cy + altura / 2
    desenhar()

def zoom_out():
    global xwmin, xwmax, ywmin, ywmax
    fator = 1.1  
    cx, cy = (xwmin + xwmax) / 2, (ywmin + ywmax) / 2
    largura, altura = (xwmax - xwmin) * fator, (ywmax - ywmin) * fator
    xwmin, xwmax = cx - largura / 2, cx + largura / 2
    ywmin, ywmax = cy - altura / 2, cy + altura / 2
    desenhar()

frame_botoes = tk.Frame(janela) 
frame_botoes.pack(side="bottom", pady=10) 

tk.Button(frame_botoes, text="↑", width=5, command=cima).grid(row=0, column=1, padx=2, pady=2) 
tk.Button(frame_botoes, text="←", width=5, command=esquerda).grid(row=1, column=0, padx=2, pady=2) 
tk.Button(frame_botoes, text="↓", width=5, command=baixo).grid(row=1, column=1, padx=2, pady=2) 
tk.Button(frame_botoes, text="→", width=5, command=direita).grid(row=1, column=2, padx=2, pady=2) 

tk.Button(frame_botoes, text="Zoom +", width=8, command=zoom_in).grid(row=0, column=3, padx=10, pady=2)
tk.Button(frame_botoes, text="Zoom -", width=8, command=zoom_out).grid(row=1, column=3, padx=10, pady=2)

atualizar_lista()
desenhar() 
janela.mainloop()