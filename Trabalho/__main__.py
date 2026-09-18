import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog
from modelo import ObjetoGrafico, DisplayFile, Transformacoes, DescritorOBJ, BSpline
from view import Window, Viewport

class InterfaceGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Gráfico 2D - SCN e OBJ")
        self.root.geometry("950x700")

        self.window = Window(cx=400, cy=250, largura=800, altura=500)
        self.viewport = Viewport(0, 0, 800, 500)
        self.display_file = DisplayFile()
        self.ponto_central_mundo = (0, 0)

        self.setup_ui()
        self.carregar_objetos_iniciais()
        self.desenhar()

    def setup_ui(self):
        self.painel = tk.Frame(self.root, width=250, bg="#f0f0f0")
        self.painel.pack(side="left", fill="y", padx=10, pady=5)

        tk.Label(self.painel, text="Objetos (Mundo)", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Button(self.painel, text="+ Novo Objeto", bg="#1a73e8", fg="white", command=self.abrir_popup_novo_objeto).pack(pady=2, fill="x")
        tk.Button(self.painel, text="Transformar Objeto", bg="#34a853", fg="white", command=self.abrir_popup_transformar).pack(pady=2, fill="x")

        frame_io = tk.Frame(self.painel, bg="#f0f0f0")
        frame_io.pack(pady=5, fill="x")
        tk.Button(frame_io, text="Exportar .OBJ", command=self.exportar_obj).pack(side="left", expand=True, fill="x", padx=1)
        tk.Button(frame_io, text="Importar .OBJ", command=self.importar_obj).pack(side="right", expand=True, fill="x", padx=1)

        self.lista_objetos = tk.Listbox(self.painel, font=("Arial", 9), selectmode=tk.SINGLE)
        self.lista_objetos.pack(fill="both", expand=True, pady=5)

        self.canvas = tk.Canvas(self.root, width=800, height=500, bg="white", highlightthickness=1, highlightbackground="gray")
        self.canvas.pack(side="top", pady=10)

        frame_botoes = tk.Frame(self.root)
        frame_botoes.pack(side="bottom", pady=10)

        # Navegação com vetor Cima/Baixo/Lados
        tk.Button(frame_botoes, text="↑", width=5, command=lambda: self.acao_navegacao("cima")).grid(row=0, column=1, padx=2)
        tk.Button(frame_botoes, text="←", width=5, command=lambda: self.acao_navegacao("esquerda")).grid(row=1, column=0, padx=2)
        tk.Button(frame_botoes, text="↓", width=5, command=lambda: self.acao_navegacao("baixo")).grid(row=1, column=1, padx=2)
        tk.Button(frame_botoes, text="→", width=5, command=lambda: self.acao_navegacao("direita")).grid(row=1, column=2, padx=2)
        
        tk.Button(frame_botoes, text="Zoom +", width=8, command=lambda: self.acao_navegacao("zoom_in")).grid(row=0, column=3, padx=10)
        tk.Button(frame_botoes, text="Zoom -", width=8, command=lambda: self.acao_navegacao("zoom_out")).grid(row=1, column=3, padx=10)
        
        tk.Label(frame_botoes, text="Girar Window (°):").grid(row=0, column=4, padx=5)
        self.e_rot_win = tk.Entry(frame_botoes, width=5)
        self.e_rot_win.grid(row=0, column=5)
        self.e_rot_win.insert(0, "10")
        tk.Button(frame_botoes, text="↺ Esq", command=lambda: self.rotacionar_window(-float(self.e_rot_win.get()))).grid(row=1, column=4)
        tk.Button(frame_botoes, text="↻ Dir", command=lambda: self.rotacionar_window(float(self.e_rot_win.get()))).grid(row=1, column=5)

    def carregar_objetos_iniciais(self):
        self.display_file.adicionar(ObjetoGrafico("Quadrado", "wireframe", [(100, 100), (200, 100), (200, 200), (100, 200)], "#ff0000"))
        self.atualizar_lista()

    def acao_navegacao(self, acao):
        step = 50
        if acao == "cima": self.window.mover(step, 0)
        elif acao == "baixo": self.window.mover(-step, 0)
        elif acao == "esquerda": self.window.mover(0, -step)
        elif acao == "direita": self.window.mover(0, step)
        elif acao == "zoom_in": self.window.zoom(0.9)
        elif acao == "zoom_out": self.window.zoom(1.1)
        self.desenhar()

    def rotacionar_window(self, angulo):
        self.window.rotacionar(angulo)
        self.desenhar()

    def exportar_obj(self):
        arq = filedialog.asksaveasfilename(defaultextension=".obj")
        if arq:
            DescritorOBJ.exportar(self.display_file, arq)
            messagebox.showinfo("Sucesso", "Mundo exportado com sucesso!")

    def importar_obj(self):
        arq = filedialog.askopenfilename(filetypes=[("OBJ Files", "*.obj")])
        if arq:
            objetos = DescritorOBJ.importar(arq)
            for o in objetos: self.display_file.adicionar(o)
            self.atualizar_lista()
            self.desenhar()
        
    def desenhar(self):
        self.canvas.delete("forma", "ponto")
        matriz_cam = self.window.matriz_scn()

        def converter_desenhar_ponto(x_mundo, y_mundo):
            x_scn = matriz_cam[0][0]*x_mundo + matriz_cam[0][1]*y_mundo + matriz_cam[0][2]*1
            y_scn = matriz_cam[1][0]*x_mundo + matriz_cam[1][1]*y_mundo + matriz_cam[1][2]*1
            return self.viewport.transformar_scn(x_scn, y_scn)

        # Desenhar Origem do Mundo (0,0)
        xvp, yvp = converter_desenhar_ponto(0, 0)
        self.canvas.create_oval(xvp-3, yvp-3, xvp+3, yvp+3, fill="black", tags="ponto")

        # CORREÇÃO 2: Renderização diferenciada para B-Splines / Curvas abertas
        for obj in self.display_file.objetos:
            qtd_vertices = len(obj.vertices)
            if qtd_vertices == 0:
                continue

            if obj.tipo == "ponto":
                xvp, yvp = converter_desenhar_ponto(obj.vertices[0][0], obj.vertices[0][1])
                self.canvas.create_oval(xvp-2, yvp-2, xvp+2, yvp+2, fill=obj.cor, tags="forma")
            
            elif obj.tipo in ["bspline", "curva", "reta"]:
                for i in range(qtd_vertices - 1):
                    x1, y1 = obj.vertices[i]
                    x2, y2 = obj.vertices[i + 1]
                    x1vp, y1vp = converter_desenhar_ponto(x1, y1)
                    x2vp, y2vp = converter_desenhar_ponto(x2, y2)
                    self.canvas.create_line(x1vp, y1vp, x2vp, y2vp, tags="forma", fill=obj.cor, width=2)
            
            else:  # Wireframes e polígonos fechados
                for i in range(qtd_vertices):
                    x1, y1 = obj.vertices[i]
                    x2, y2 = obj.vertices[(i + 1) % qtd_vertices]
                    x1vp, y1vp = converter_desenhar_ponto(x1, y1)
                    x2vp, y2vp = converter_desenhar_ponto(x2, y2)
                    self.canvas.create_line(x1vp, y1vp, x2vp, y2vp, tags="forma", fill=obj.cor, width=2)

    def atualizar_lista(self):
        self.lista_objetos.delete(0, tk.END)
        for obj in self.display_file.objetos:
            self.lista_objetos.insert(tk.END, f"• {obj.nome} ({obj.tipo})")

    def abrir_popup_novo_objeto(self):
        popup = tk.Toplevel(self.root)
        popup.title("Novo Objeto")
        popup.geometry("380x380")
        popup.grab_set()

        tk.Label(popup, text="Nome do Objeto:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        e_nome = tk.Entry(popup, font=("Arial", 10))
        e_nome.pack(fill="x", padx=15, pady=2)

        tk.Label(popup, text="Tipo de Objeto:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        tipo_var = tk.StringVar(value="auto")
        combo_tipo = tk.OptionMenu(
            popup, tipo_var, 
            "auto", "bspline",
            command=lambda v: label_dica.config(
                text="Mínimo de 4 pontos para B-Spline!" if v == "bspline" else "Ex: (100,100),(200,200)"
            )
        )
        combo_tipo.pack(fill="x", padx=15, pady=2)

        tk.Label(popup, text="Coordenadas: (x1,y1),(x2,y2)...", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        e_coords = tk.Entry(popup, font=("Arial", 10))
        e_coords.pack(fill="x", padx=15, pady=2)

        label_dica = tk.Label(popup, text="Ex: (100,100),(200,200)", font=("Arial", 8, "italic"), fg="gray")
        label_dica.pack(anchor="w", padx=15)

        tk.Label(popup, text="Cor:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        cor_selecionada = ["#1a73e8"]
        
        def escolher_cor():
            _, hex_color = colorchooser.askcolor(color=cor_selecionada[0], title="Escolha uma cor")
            if hex_color:
                cor_selecionada[0] = hex_color
                btn_cor.config(bg=hex_color)

        btn_cor = tk.Button(popup, text="Selecionar Cor", bg=cor_selecionada[0], fg="white", command=escolher_cor)
        btn_cor.pack(padx=15, pady=2, fill="x")

        def salvar():
            nome = e_nome.get().strip() or f"Objeto {len(self.display_file.objetos) + 1}"
            raw_coords = e_coords.get().strip()
            
            if not raw_coords:
                messagebox.showwarning("Aviso", "Informe as coordenadas!")
                return
                
            try:
                pontos = list(eval(f"[{raw_coords}]"))
                
                if not all(isinstance(p, tuple) and len(p) == 2 for p in pontos):
                    raise ValueError("Formato de ponto inválido")

                tipo_selecionado = tipo_var.get()

                if tipo_selecionado == "bspline":
                    if len(pontos) < 4:
                        messagebox.showwarning("Aviso B-Spline", "Uma B-Spline exige pelo menos 4 pontos de controle!")
                        return
                    
                    novo_obj = BSpline(nome, pontos, cor_selecionada[0])
                else:
                    if len(pontos) == 1: tipo = "ponto"
                    elif len(pontos) == 2: tipo = "reta"
                    else: tipo = "wireframe"

                    novo_obj = ObjetoGrafico(nome, tipo, pontos, cor_selecionada[0])

                self.display_file.adicionar(novo_obj)
                self.atualizar_lista()
                self.desenhar()
                popup.destroy()

            except Exception:
                messagebox.showerror("Erro de Formato", "Use o padrão correto de coordenadas:\n(x1,y1),(x2,y2),(x3,y3)...")

        tk.Button(popup, text="Salvar Objeto", bg="#1a73e8", fg="white", font=("Arial", 9, "bold"), command=salvar).pack(pady=15)

    def abrir_popup_transformar(self):
        selecao = self.lista_objetos.curselection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um objeto na lista!")
            return
        
        obj = self.display_file.objetos[selecao[0]]

        popup = tk.Toplevel(self.root)
        popup.title(f"Transformar: {obj.nome}")
        popup.geometry("300x480")
        popup.grab_set()

        # Translação
        tk.Label(popup, text="Translação", font=("Arial", 10, "bold")).pack(pady=(10,0))
        f_t = tk.Frame(popup)
        f_t.pack()
        tk.Label(f_t, text="dx:").grid(row=0, column=0)
        e_dx = tk.Entry(f_t, width=5); e_dx.grid(row=0, column=1)
        tk.Label(f_t, text="dy:").grid(row=0, column=2)
        e_dy = tk.Entry(f_t, width=5); e_dy.grid(row=0, column=3)
        
        def aplicar_translacao():
            try:
                matriz = Transformacoes.translacao(float(e_dx.get()), float(e_dy.get()))
                obj.transformar(matriz)
                self.desenhar()
            except ValueError: messagebox.showerror("Erro", "Valores inválidos")
            
        tk.Button(popup, text="Aplicar Translação", command=aplicar_translacao).pack(pady=2)

        # Escala
        tk.Label(popup, text="Escalonamento (Centro)", font=("Arial", 10, "bold")).pack(pady=(15,0))
        f_e = tk.Frame(popup)
        f_e.pack()
        tk.Label(f_e, text="sx:").grid(row=0, column=0)
        e_sx = tk.Entry(f_e, width=5); e_sx.grid(row=0, column=1)
        tk.Label(f_e, text="sy:").grid(row=0, column=2)
        e_sy = tk.Entry(f_e, width=5); e_sy.grid(row=0, column=3)

        def aplicar_escala():
            try:
                cx, cy = obj.centro_geometrico()
                m = Transformacoes.encadear(
                    Transformacoes.translacao(cx, cy),
                    Transformacoes.escala(float(e_sx.get()), float(e_sy.get())),
                    Transformacoes.translacao(-cx, -cy)
                )
                obj.transformar(m)
                self.desenhar()
            except ValueError: messagebox.showerror("Erro", "Valores inválidos")

        tk.Button(popup, text="Aplicar Escala", command=aplicar_escala).pack(pady=2)

        # Rotação
        tk.Label(popup, text="Rotação (Graus)", font=("Arial", 10, "bold")).pack(pady=(15,0))
        e_ang = tk.Entry(popup, width=10)
        e_ang.pack()

        tipo_rot = tk.StringVar(value="objeto")
        tk.Radiobutton(popup, text="Centro do Objeto", variable=tipo_rot, value="objeto").pack()
        tk.Radiobutton(popup, text="Origem do Mundo", variable=tipo_rot, value="mundo").pack()
        
        f_r_ponto = tk.Frame(popup)
        f_r_ponto.pack()
        tk.Radiobutton(f_r_ponto, text="Ponto:", variable=tipo_rot, value="ponto").grid(row=0, column=0)
        tk.Label(f_r_ponto, text="X:").grid(row=0, column=1)
        e_px = tk.Entry(f_r_ponto, width=4); e_px.grid(row=0, column=2)
        tk.Label(f_r_ponto, text="Y:").grid(row=0, column=3)
        e_py = tk.Entry(f_r_ponto, width=4); e_py.grid(row=0, column=4)

        def aplicar_rotacao():
            try:
                ang = float(e_ang.get())
                if tipo_rot.get() == "mundo":
                    m = Transformacoes.rotacao(ang)
                else:
                    if tipo_rot.get() == "objeto":
                        cx, cy = obj.centro_geometrico()
                    else:
                        cx, cy = float(e_px.get()), float(e_py.get())
                        
                    m = Transformacoes.encadear(
                        Transformacoes.translacao(cx, cy),
                        Transformacoes.rotacao(ang),
                        Transformacoes.translacao(-cx, -cy)
                    )
                obj.transformar(m)
                self.desenhar()
            except ValueError: messagebox.showerror("Erro", "Valores inválidos")

        tk.Button(popup, text="Aplicar Rotação", command=aplicar_rotacao).pack(pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()