import tkinter as tk 
from tkinter import messagebox, ttk
from modelo import DisplayFile, ObjetoGrafico, BSpline, Transformacoes, DescritorOBJ

# --- Inicialização do Sistema ---
janela = tk.Tk() 
janela.title("Sistema Gráfico 2D - Grupo 20") 
janela.geometry("900x700") 

canvas = tk.Canvas( 
    janela, 
    width=800, 
    height=500, 
    bg="white",
    highlightthickness=1,
    highlightbackground="gray"
) 
canvas.pack(side="top", pady=10) 

# --- Viewport e Window ---
xvpmin, yvpmin = 0, 0 
xvpmax, yvpmax = 800, 500 

xwmin, ywmin = 0, 0 
xwmax, ywmax = 800, 500 

# Display File global contendo os objetos do modelo
display_file = DisplayFile()

# Objetos Base Inicialização
display_file.adicionar(ObjetoGrafico("Quadrado Base", "wireframe", [(400, 300), (500, 300), (500, 400), (400, 400)]))
display_file.adicionar(ObjetoGrafico("Triângulo Base", "triangulo", [(400, 100), (500, 100), (450, 200)]))

# --- Mapeamento de Coordenadas (Window -> Viewport) ---
def transformar_viewport(xw, yw): 
    xvp = xvpmin + ((xw - xwmin) / (xwmax - xwmin)) * (xvpmax - xvpmin) 
    yvp = yvpmin + (1 - (yw - ywmin) / (ywmax - ywmin)) * (yvpmax - yvpmin) 
    return xvp, yvp 

# --- Funções de Desenho ---
def desenhar(): 
    canvas.delete("all") 

    for obj in display_file.objetos:
        pts = obj.vertices
        if not pts: continue

        # Transforma todos os vértices do objeto para a Viewport
        pts_vp = [transformar_viewport(x, y) for x, y in pts]

        if obj.tipo == "ponto":
            xvp, yvp = pts_vp[0]
            canvas.create_oval(xvp-2, yvp-2, xvp+2, yvp+2, fill=obj.cor, tags="forma")
        else:
            # Conecta vértices consecutivos
            num_pts = len(pts_vp)
            fechar = obj.tipo in ["wireframe", "triangulo"]
            limite = num_pts if fechar else num_pts - 1

            for i in range(limite):
                p1 = pts_vp[i]
                p2 = pts_vp[(i + 1) % num_pts]
                canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=obj.cor, width=2, tags="forma")

def atualizar_lista():
    lista_objetos.delete(0, tk.END)
    for obj in display_file.objetos:
        lista_objetos.insert(tk.END, f"• {obj.nome} ({obj.tipo})")

# --- Interface e Popups ---
painel = tk.Frame(janela, width=220, bg="#f0f0f0")
painel.pack(side="left", fill="y", padx=10, pady=5)

tk.Label(painel, text="Display File (Objetos)", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=5)

def abrir_popup_novo_objeto():
    popup = tk.Toplevel(janela)
    popup.title("Novo Objeto")
    popup.geometry("380x300")
    popup.resizable(False, False)
    popup.grab_set()

    tk.Label(popup, text="Nome do Objeto:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 2))
    e_nome = tk.Entry(popup, font=("Arial", 10))
    e_nome.pack(fill="x", padx=15, pady=2)

    tk.Label(popup, text="Tipo de Objeto:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(5, 2))
    cb_tipo = ttk.Combobox(popup, values=["Automático", "B-Spline"], state="readonly")
    cb_tipo.current(0)
    cb_tipo.pack(fill="x", padx=15, pady=2)

    tk.Label(popup, text="Coordenadas: (x1,y1),(x2,y2)...", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(5, 2))
    e_coords = tk.Entry(popup, font=("Arial", 10))
    e_coords.pack(fill="x", padx=15, pady=2)

    def salvar():
        nome = e_nome.get().strip() or f"Objeto {len(display_file.objetos) + 1}"
        raw_coords = e_coords.get().strip()
        tipo_selecionado = cb_tipo.get()
        
        if not raw_coords:
            messagebox.showwarning("Aviso", "Informe as coordenadas!")
            return
            
        try:
            pontos = list(eval(f"[{raw_coords}]"))

            if tipo_selecionado == "B-Spline":
                if len(pontos) < 4:
                    messagebox.showwarning("Aviso B-Spline", "Uma B-Spline exige pelo menos 4 pontos de controle!")
                    return
                novo_obj = BSpline(nome, pontos)
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
            
        except Exception as e:
            messagebox.showerror("Erro", f"Formato incorreto!\nExemplo: (100,100),(200,200),(300,100),(400,200)\n\n{e}")

    tk.Button(popup, text="Salvar Objeto", bg="#1a73e8", fg="white", font=("Arial", 9, "bold"), command=salvar).pack(pady=15)

btn_abrir_popup = tk.Button(painel, text="+ Novo Objeto", bg="#1a73e8", fg="white", font=("Arial", 9, "bold"), command=abrir_popup_novo_objeto)
btn_abrir_popup.pack(pady=5, fill="x", padx=5)

lista_objetos = tk.Listbox(painel, font=("Arial", 9), selectmode=tk.SINGLE)
lista_objetos.pack(fill="both", expand=True, padx=5, pady=5)

# --- Navegação da Window (Pan / Zoom) ---
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