import tkinter as tk 
from tkinter import messagebox, ttk

# Importação dos módulos do sistema gráfico
from modelo import ObjetoGrafico, Curva2D, DisplayFile, Transformacoes
from clipping import (
    clip_ponto, 
    clip_reta_cohen_sutherland, 
    clip_poligono_sutherland_hodgman, 
    clip_curva
)

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

# Viewport
xvpmin, yvpmin = 0, 0 
xvpmax, yvpmax = 800, 500 

# Window Inicial
xwmin, ywmin = 0, 0 
xwmax, ywmax = 800, 500 

# Instância global do DisplayFile
display_file = DisplayFile()

# Objetos Iniciais de Exemplo
quadrado = ObjetoGrafico(
    "Quadrado Base", 
    "wireframe", 
    [(400, 300), (500, 300), (500, 400), (400, 400)]
)
triangulo = ObjetoGrafico(
    "Triângulo Base", 
    "wireframe", 
    [(400, 100), (500, 100), (450, 200)]
)

display_file.adicionar(quadrado)
display_file.adicionar(triangulo)

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

# Transformação da Window (Mundo) para Viewport (Tela)
def transformar(xw, yw): 
    xvp = xvpmin + ((xw - xwmin) / (xwmax - xwmin)) * (xvpmax - xvpmin) 
    yvp = yvpmin + (1 - (yw - ywmin) / (ywmax - ywmin)) * (yvpmax - yvpmin) 
    return xvp, yvp 

# Desenha objeto individual com clipping aplicado no espaço do Mundo
def desenhar_objeto(obj):
    if obj.tipo == "ponto":
        p = obj.vertices[0]
        res = clip_ponto(p[0], p[1], xwmin, ywmin, xwmax, ywmax)
        if res:
            xvp, yvp = transformar(res[0], res[1])
            raio = 3
            canvas.create_oval(
                xvp - raio, yvp - raio, xvp + raio, yvp + raio, 
                fill=obj.cor, outline=obj.cor, tags="forma"
            )

    elif obj.tipo == "reta":
        p1, p2 = obj.vertices[0], obj.vertices[1]
        res = clip_reta_cohen_sutherland(p1[0], p1[1], p2[0], p2[1], xwmin, ywmin, xwmax, ywmax)
        if res:
            x1, y1, x2, y2 = res
            x1vp, y1vp = transformar(x1, y1)
            x2vp, y2vp = transformar(x2, y2)
            canvas.create_line(x1vp, y1vp, x2vp, y2vp, tags="forma", fill=obj.cor, width=2)

    elif obj.tipo in ["wireframe", "triangulo"]:
        poly_clip = clip_poligono_sutherland_hodgman(obj.vertices, xwmin, ywmin, xwmax, ywmax)
        if poly_clip and len(poly_clip) >= 2:
            pontos_vp = [transformar(vx, vy) for vx, vy in poly_clip]
            
            if obj.preenchido and len(pontos_vp) >= 3:
                flat_coords = [c for p in pontos_vp for c in p]
                canvas.create_polygon(
                    flat_coords, 
                    fill=obj.cor_preenchimento, 
                    outline=obj.cor, 
                    width=2, 
                    tags="forma"
                )
            else:
                for i in range(len(pontos_vp)):
                    p1 = pontos_vp[i]
                    p2 = pontos_vp[(i + 1) % len(pontos_vp)]
                    canvas.create_line(p1[0], p1[1], p2[0], p2[1], tags="forma", fill=obj.cor, width=2)

    elif obj.tipo == "curva":
        segmentos_visiveis = clip_curva(obj.vertices, xwmin, ywmin, xwmax, ywmax)
        for (x1, y1), (x2, y2) in segmentos_visiveis:
            x1vp, y1vp = transformar(x1, y1)
            x2vp, y2vp = transformar(x2, y2)
            canvas.create_line(x1vp, y1vp, x2vp, y2vp, tags="forma", fill=obj.cor, width=2)

def desenhar(): 
    canvas.delete("forma") 
    canvas.delete("ponto") 

    for obj in display_file.objetos: 
        desenhar_objeto(obj) 

def atualizar_lista():
    lista_objetos.delete(0, tk.END)
    for obj in display_file.objetos:
        lista_objetos.insert(tk.END, f"• {obj.nome} ({obj.tipo})")

def abrir_popup_novo_objeto():
    popup = tk.Toplevel(janela)
    popup.title("Novo Objeto Gráfico")
    popup.geometry("380x280")
    popup.resizable(False, False)
    popup.grab_set()

    tk.Label(popup, text="Nome do Objeto:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
    e_nome = tk.Entry(popup, font=("Arial", 10))
    e_nome.pack(fill="x", padx=15, pady=2)

    tk.Label(popup, text="Tipo do Objeto:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
    combo_tipo = ttk.Combobox(
        popup, 
        values=["Polígono / Reta / Ponto", "Curva 2D (Hermite)"], 
        state="readonly", 
        font=("Arial", 9)
    )
    combo_tipo.current(0)
    combo_tipo.pack(fill="x", padx=15, pady=2)

    tk.Label(popup, text="Coordenadas: (x1,y1),(x2,y2)...", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
    e_coords = tk.Entry(popup, font=("Arial", 10))
    e_coords.pack(fill="x", padx=15, pady=2)

    def salvar():
        nome = e_nome.get().strip() or f"Objeto_{len(display_file.objetos) + 1}"
        raw_coords = e_coords.get().strip()
        
        if not raw_coords:
            messagebox.showwarning("Aviso", "Informe as coordenadas!")
            return
            
        try:
            pontos = list(eval(f"[{raw_coords}]"))
            
            if combo_tipo.get() == "Curva 2D (Hermite)":
                if len(pontos) < 4:
                    messagebox.showwarning("Aviso", "Para criar uma curva de Hermite são necessários no mínimo 4 pontos/vetores!\n(P0, P1, V0, V1)")
                    return
                
                novo_obj = Curva2D(nome, pontos)
            else:
                if len(pontos) == 1:
                    tipo = "ponto"
                elif len(pontos) == 2:
                    tipo = "reta"
                else:
                    tipo = "wireframe"
                
                novo_obj = ObjetoGrafico(nome, tipo, pontos)

            display_file.adicionar(novo_obj)
            atualizar_lista()
            desenhar()
            popup.destroy()
            
        except Exception:
            messagebox.showerror(
                "Erro", 
                "Formato de coordenadas incorreto!\n"
                "Exemplo válido: (150,250), (650,250), (300,400), (300,-400)"
            )

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

# Navegação e Controle da Window
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