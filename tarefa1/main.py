import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog
from modelo import ObjetoGrafico, DisplayFile, Transformacoes, DescritorOBJ
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
    def centralizar_window(self):
        if not self.display_file.objetos:
            return

        # Inicializa limites ao infinito
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        # Varre todos os vértices de todos os objetos para achar a Bounding Box do mundo
        for obj in self.display_file.objetos:
            for x, y in obj.vertices:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y

        # Evita divisão por zero caso seja apenas um ponto no mundo
        largura_mundo = (max_x - min_x) if max_x != min_x else 100
        altura_mundo = (max_y - min_y) if max_y != min_y else 100

        # Define o centro da Window para o centro exato da Bounding Box
        self.window.cx = (min_x + max_x) / 2
        self.window.cy = (min_y + max_y) / 2
        
        # Aplica uma margem de segurança (20%) para os objetos não colarem na borda
        self.window.largura = largura_mundo * 1.2
        self.window.altura = altura_mundo * 1.2
        self.window.angulo = 0  # Remove rotações para alinhar a visualização
        
        self.desenhar()
        
    def desenhar(self):
        self.canvas.delete("forma", "ponto")
        
        # Pega a matriz de transformação do Mundo -> SCN
        matriz_cam = self.window.matriz_scn()

        def converter_desenhar_ponto(x_mundo, y_mundo):
            # Transforma WC -> SCN
            x_scn = matriz_cam[0][0]*x_mundo + matriz_cam[0][1]*y_mundo + matriz_cam[0][2]*1
            y_scn = matriz_cam[1][0]*x_mundo + matriz_cam[1][1]*y_mundo + matriz_cam[1][2]*1
            # Transforma SCN -> Viewport
            return self.viewport.transformar_scn(x_scn, y_scn)

        # Desenhar Origem do Mundo (0,0)
        xvp, yvp = converter_desenhar_ponto(0, 0)
        self.canvas.create_oval(xvp-3, yvp-3, xvp+3, yvp+3, fill="black", tags="ponto")

        # Desenhar Objetos via Cache visual (Não altera o Display File)
        for obj in self.display_file.objetos:
            qtd_vertices = len(obj.vertices)
            for i in range(qtd_vertices):
                x1, y1 = obj.vertices[i]
                
                if obj.tipo == "ponto":
                    x2, y2 = x1, y1
                elif obj.tipo == "reta":
                    if i == 1: break 
                    x2, y2 = obj.vertices[1]
                else:
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
        popup.geometry("350x300")
        popup.grab_set()

        tk.Label(popup, text="Nome do Objeto:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        e_nome = tk.Entry(popup, font=("Arial", 10))
        e_nome.pack(fill="x", padx=15, pady=2)

        tk.Label(popup, text="Coordenadas: (x1,y1),(x2,y2)...", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        e_coords = tk.Entry(popup, font=("Arial", 10))
        e_coords.pack(fill="x", padx=15, pady=2)

        tk.Label(popup, text="Cor da Borda:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
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
                if len(pontos) == 1: tipo = "ponto"
                elif len(pontos) == 2: tipo = "reta"
                else: tipo = "wireframe"
                    
                novo_obj = ObjetoGrafico(nome, tipo, pontos, cor_selecionada[0])
                self.display_file.adicionar(novo_obj)
                self.atualizar_lista()
                self.desenhar()
                popup.destroy()
            except Exception:
                messagebox.showerror("Erro", "Formato incorreto!\nExemplo: (100,100),(200,200)")

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

        # ----- TRANSLAÇÃO -----
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

        # ----- ESCALA -----
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

        # ----- ROTAÇÃO -----
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
        # Adicione este botão dentro do método setup_ui(self), no bloco do "self.painel":
        tk.Button(self.painel, text="[ Centralizar Visão ]", bg="#fbbc05", fg="black", font=("Arial", 9, "bold"),
                command=self.centralizar_window).pack(pady=10, fill="x", padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()