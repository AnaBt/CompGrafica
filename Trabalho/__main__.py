import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog
from modelo import ObjetoGrafico, DisplayFile, Transformacoes, DescritorOBJ
from view import Window, Viewport
from clipping import (
    clip_ponto,
    clip_reta_cohen_sutherland,
    clip_reta_liang_barsky,
    clip_poligono_sutherland_hodgman
)

class InterfaceGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Gráfico 2D - SCN e OBJ")
        self.root.geometry("950x750")

        self.window = Window(cx=400, cy=250, largura=800, altura=500)
        # Viewport menor que a área do canvas (10, 10) até (790, 490)
        self.viewport = Viewport(10, 10, 790, 490)
        self.display_file = DisplayFile()
        self.ponto_central_mundo = (0, 0)

        # Algoritmo de clipagem de retas padrão
        self.algoritmo_clip_reta = tk.StringVar(value="cohen")

        self.setup_ui()
        self.carregar_objetos_iniciais()
        self.desenhar()

    def setup_ui(self):
        self.painel = tk.Frame(self.root, width=250, bg="#f0f0f0")
        self.painel.pack(side="left", fill="y", padx=10, pady=5)

        tk.Label(self.painel, text="Objetos (Mundo)", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Button(self.painel, text="+ Novo Objeto", bg="#1a73e8", fg="white", command=self.abrir_popup_novo_objeto).pack(pady=2, fill="x")
        tk.Button(self.painel, text="Transformar Objeto", bg="#34a853", fg="white", command=self.abrir_popup_transformar).pack(pady=2, fill="x")
        tk.Button(self.painel, text="[ Centralizar Visão ]", bg="#fbbc05", fg="black", font=("Arial", 9, "bold"),
                  command=self.centralizar_window).pack(pady=5, fill="x")

        # Seleção do Algoritmo de Clipagem de Retas
        frame_clip = tk.LabelFrame(self.painel, text="Clipagem de Reta", bg="#f0f0f0", font=("Arial", 9, "bold"))
        frame_clip.pack(pady=5, fill="x", padx=0)
        tk.Radiobutton(frame_clip, text="Cohen-Sutherland", variable=self.algoritmo_clip_reta, value="cohen", bg="#f0f0f0", command=self.desenhar).pack(anchor="w", padx=5)
        tk.Radiobutton(frame_clip, text="Liang-Barsky", variable=self.algoritmo_clip_reta, value="liang", bg="#f0f0f0", command=self.desenhar).pack(anchor="w", padx=5)

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
        # Exemplo com quadrado preenchido para demonstrar
        self.display_file.adicionar(
            ObjetoGrafico(
                "Quadrado Preenchido",
                "wireframe",
                [(100, 100), (200, 100), (200, 200), (100, 200)],
                cor="#ff0000",
                preenchido=True,
                cor_preenchimento="#ff8888"
            )
        )
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

        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        for obj in self.display_file.objetos:
            for x, y in obj.vertices:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y

        largura_mundo = (max_x - min_x) if max_x != min_x else 100
        altura_mundo = (max_y - min_y) if max_y != min_y else 100

        self.window.cx = (min_x + max_x) / 2
        self.window.cy = (min_y + max_y) / 2
        self.window.largura = largura_mundo * 1.2
        self.window.altura = altura_mundo * 1.2
        self.window.angulo = 0
        
        self.desenhar()

    def desenhar(self):
        self.canvas.delete("all")

        # Desenhar Moldura da Viewport
        self.canvas.create_rectangle(
            self.viewport.xmin, self.viewport.ymin,
            self.viewport.xmax, self.viewport.ymax,
            outline="red", width=1, dash=(4, 4)
        )

        matriz_cam = self.window.matriz_scn()

        def wc_para_scn(x_mundo, y_mundo):
            x_scn = matriz_cam[0][0]*x_mundo + matriz_cam[0][1]*y_mundo + matriz_cam[0][2]*1
            y_scn = matriz_cam[1][0]*x_mundo + matriz_cam[1][1]*y_mundo + matriz_cam[1][2]*1
            return x_scn, y_scn

        # Desenhar Origem do Mundo (0,0) com clipagem
        x0_scn, y0_scn = wc_para_scn(0, 0)
        ponto_clip = clip_ponto(x0_scn, y0_scn)
        if ponto_clip:
            xvp, yvp = self.viewport.transformar_scn(ponto_clip[0], ponto_clip[1])
            self.canvas.create_oval(xvp-3, yvp-3, xvp+3, yvp+3, fill="black", tags="ponto")

        # Processar objetos com clipagem no SCN [-1, 1] antes da Viewport
        for obj in self.display_file.objetos:
            vertices_scn = [wc_para_scn(vx, vy) for vx, vy in obj.vertices]

            if obj.tipo == "ponto":
                for x_scn, y_scn in vertices_scn:
                    p = clip_ponto(x_scn, y_scn)
                    if p:
                        xvp, yvp = self.viewport.transformar_scn(p[0], p[1])
                        self.canvas.create_oval(xvp-2, yvp-2, xvp+2, yvp+2, fill=obj.cor, tags="forma")

            elif obj.tipo == "reta":
                if len(vertices_scn) >= 2:
                    (x1, y1), (x2, y2) = vertices_scn[0], vertices_scn[1]
                    if self.algoritmo_clip_reta.get() == "cohen":
                        res = clip_reta_cohen_sutherland(x1, y1, x2, y2)
                    else:
                        res = clip_reta_liang_barsky(x1, y1, x2, y2)

                    if res:
                        x1c, y1c, x2c, y2c = res
                        x1vp, y1vp = self.viewport.transformar_scn(x1c, y1c)
                        x2vp, y2vp = self.viewport.transformar_scn(x2c, y2c)
                        self.canvas.create_line(x1vp, y1vp, x2vp, y2vp, fill=obj.cor, width=2, tags="forma")

            else:  # Polígono / Wireframe
                poly_clip = clip_poligono_sutherland_hodgman(vertices_scn)
                
                if len(poly_clip) >= 3 and obj.preenchido:
                    # Mapeia vértices clipados do SCN -> Viewport
                    pts_vp = []
                    for px, py in poly_clip:
                        xvp, yvp = self.viewport.transformar_scn(px, py)
                        pts_vp.extend([xvp, yvp])

                    # Utiliza a primitiva do Tkinter (canvas.create_polygon) para desenhar polígonos preenchidos
                    self.canvas.create_polygon(
                        pts_vp,
                        fill=obj.cor_preenchimento,
                        outline=obj.cor,
                        width=2,
                        tags="forma"
                    )

                elif len(poly_clip) >= 2:
                    # Desenha apenas o contorno (Modelo de Arame)
                    for i in range(len(poly_clip)):
                        p1 = poly_clip[i]
                        p2 = poly_clip[(i + 1) % len(poly_clip)]
                        x1vp, y1vp = self.viewport.transformar_scn(p1[0], p1[1])
                        x2vp, y2vp = self.viewport.transformar_scn(p2[0], p2[1])
                        self.canvas.create_line(x1vp, y1vp, x2vp, y2vp, fill=obj.cor, width=2, tags="forma")

    def atualizar_lista(self):
        self.lista_objetos.delete(0, tk.END)
        for obj in self.display_file.objetos:
            modo = "Preenchido" if obj.preenchido else "Wireframe"
            self.lista_objetos.insert(tk.END, f"• {obj.nome} ({obj.tipo} - {modo})")

    def abrir_popup_novo_objeto(self):
        popup = tk.Toplevel(self.root)
        popup.title("Novo Objeto")
        popup.geometry("380x420")
        popup.grab_set()

        tk.Label(popup, text="Nome do Objeto:", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        e_nome = tk.Entry(popup, font=("Arial", 10))
        e_nome.pack(fill="x", padx=15, pady=2)

        tk.Label(popup, text="Coordenadas: (x1,y1),(x2,y2)...", font=("Arial", 9, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        e_coords = tk.Entry(popup, font=("Arial", 10))
        e_coords.pack(fill="x", padx=15, pady=2)

        # Escolha do modelo de preenchimento
        var_preenchido = tk.BooleanVar(value=False)
        chk_preenchido = tk.Checkbutton(popup, text="Polígono Preenchido", variable=var_preenchido, font=("Arial", 9, "bold"))
        chk_preenchido.pack(anchor="w", padx=15, pady=10)

        cor_borda = ["#1a73e8"]
        cor_preenchimento = ["#8ab4f8"]

        def escolher_cor_borda():
            _, hex_color = colorchooser.askcolor(color=cor_borda[0], title="Escolha a cor da borda")
            if hex_color:
                cor_borda[0] = hex_color
                btn_cor_borda.config(bg=hex_color)

        def escolher_cor_preenchimento():
            _, hex_color = colorchooser.askcolor(color=cor_preenchimento[0], title="Escolha a cor de preenchimento")
            if hex_color:
                cor_preenchimento[0] = hex_color
                btn_cor_preenchimento.config(bg=hex_color)

        btn_cor_borda = tk.Button(popup, text="Cor da Borda", bg=cor_borda[0], fg="white", command=escolher_cor_borda)
        btn_cor_borda.pack(padx=15, pady=2, fill="x")

        btn_cor_preenchimento = tk.Button(popup, text="Cor de Preenchimento", bg=cor_preenchimento[0], fg="black", command=escolher_cor_preenchimento)
        btn_cor_preenchimento.pack(padx=15, pady=2, fill="x")

        def salvar():
            nome = e_nome.get().strip() or f"Objeto {len(self.display_file.objetos) + 1}"
            raw_coords = e_coords.get().strip()
            
            if not raw_coords:
                messagebox.showwarning("Aviso", "Informe as coordenadas!")
                return
                
            try:
                pontos = list(eval(f"[{raw_coords}]"))
                is_preenchido = var_preenchido.get()

                if len(pontos) == 1:
                    tipo = "ponto"
                    is_preenchido = False
                elif len(pontos) == 2:
                    tipo = "reta"
                    is_preenchido = False
                else:
                    tipo = "wireframe"
                    
                novo_obj = ObjetoGrafico(
                    nome=nome,
                    tipo=tipo,
                    vertices=pontos,
                    cor=cor_borda[0],
                    preenchido=is_preenchido,
                    cor_preenchimento=cor_preenchimento[0]
                )
                self.display_file.adicionar(novo_obj)
                self.atualizar_lista()
                self.desenhar()
                popup.destroy()
            except Exception:
                messagebox.showerror("Erro", "Formato incorreto!\nExemplo: (100,100),(200,100),(150,200)")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()