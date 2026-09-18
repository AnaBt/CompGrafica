import math

class Transformacoes:
    @staticmethod
    def translacao(dx, dy):
        return [[1, 0, dx], [0, 1, dy], [0, 0, 1]]

    @staticmethod
    def escala(sx, sy):
        return [[sx, 0, 0], [0, sy, 0], [0, 0, 1]]

    @staticmethod
    def rotacao(angulo_graus):
        rad = math.radians(angulo_graus)
        c = math.cos(rad)
        s = math.sin(rad)
        return [[c, -s, 0], [s, c, 0], [0, 0, 1]]

    @staticmethod
    def multiplicar_matrizes(m1, m2):
        result = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            for j in range(3):
                result[i][j] = sum(m1[i][k] * m2[k][j] for k in range(3))
        return result

    @staticmethod
    def encadear(*matrizes):
        resultado = matrizes[0]
        for m in matrizes[1:]:
            resultado = Transformacoes.multiplicar_matrizes(resultado, m)
        return resultado

class ObjetoGrafico:
    def __init__(self, nome, tipo, vertices, cor="#1a73e8"):
        self.nome = nome
        self.tipo = tipo
        self.vertices = vertices
        self.cor = cor

    def transformar(self, matriz):
        novos_vertices = []
        for x, y in self.vertices:
            nx = matriz[0][0]*x + matriz[0][1]*y + matriz[0][2]*1
            ny = matriz[1][0]*x + matriz[1][1]*y + matriz[1][2]*1
            novos_vertices.append((nx, ny))
        self.vertices = novos_vertices

    def centro_geometrico(self):
        if not self.vertices: return 0, 0
        cx = sum(v[0] for v in self.vertices) / len(self.vertices)
        cy = sum(v[1] for v in self.vertices) / len(self.vertices)
        return cx, cy

class DisplayFile:
    def __init__(self):
        self.objetos = []

    def adicionar(self, objeto):
        self.objetos.append(objeto)

class DescritorOBJ:
    @staticmethod
    def exportar(display_file, filepath):
        with open(filepath, 'w') as f:
            f.write("# SGI - Wavefront OBJ\n")
            offset = 1
            for obj in display_file.objetos:
                f.write(f"o {obj.nome}\n")
                
                # Para B-Splines, exporta-se os pontos de controle com tag identificadora
                if isinstance(obj, BSpline):
                    f.write("# type bspline\n")
                    pts = obj.pontos_controle
                else:
                    pts = obj.vertices

                for v in pts:
                    f.write(f"v {v[0]} {v[1]} 0.0\n")
                
                f.write("l ")
                for i in range(len(pts)):
                    f.write(f"{offset + i} ")
                if obj.tipo in ["wireframe", "triangulo"]:
                    f.write(f"{offset}") # Fecha polígono
                f.write("\n")
                offset += len(pts)

    @staticmethod
    def importar(filepath):
        objetos = []
        vertices_globais = []
        nome_atual = "ObjImportado"
        eh_bspline = False

        try:
            with open(filepath, 'r') as f:
                for linha in f:
                    linha_clean = linha.strip()
                    if not linha_clean: continue
                    
                    if linha_clean.startswith("# type bspline"):
                        eh_bspline = True
                        continue

                    partes = linha_clean.split()
                    if partes[0] == 'o':
                        nome_atual = partes[1]
                        eh_bspline = False
                    elif partes[0] == 'v':
                        vertices_globais.append((float(partes[1]), float(partes[2])))
                    elif partes[0] in ['l', 'f', 'p']:
                        indices = [int(i.split('/')[0]) - 1 for i in partes[1:]]
                        v_obj = [vertices_globais[i] for i in indices]
                        
                        if eh_bspline and len(v_obj) >= 4:
                            objetos.append(BSpline(nome_atual, v_obj))
                        else:
                            tipo = "ponto" if len(v_obj) == 1 else "reta" if len(v_obj) == 2 else "wireframe"
                            objetos.append(ObjetoGrafico(nome_atual, tipo, v_obj))
                        
                        nome_atual = f"Obj_{len(objetos)+1}"
                        eh_bspline = False
            return objetos
        except Exception:
            return []

class BSpline(ObjetoGrafico):
    def __init__(self, nome, pontos_controle, cor="#1a73e8", passos=30):
        self.pontos_controle = pontos_controle
        self.passos = passos
        vertices_curva = self.gerar_curva()
        super().__init__(nome, "bspline", vertices_curva, cor)

    def gerar_curva(self):
        """Calcula os pontos da B-Spline utilizando Forward Differences sem duplicação de nós."""
        if len(self.pontos_controle) < 4:
            return list(self.pontos_controle)

        M_bs = [
            [-1/6,  3/6, -3/6,  1/6],
            [ 3/6, -6/6,  3/6,  0.0],
            [-3/6,  0.0,  3/6,  0.0],
            [ 1/6,  4/6,  1/6,  0.0]
        ]

        n = self.passos
        delta = 1.0 / n
        d2 = delta * delta
        d3 = d2 * delta

        E = [
            [0.0, 0.0, 0.0, 1.0],
            [d3,  d2,  delta, 0.0],
            [6*d3, 2*d2, 0.0, 0.0],
            [6*d3, 0.0,  0.0, 0.0]
        ]

        E_M = [[sum(E[i][k] * M_bs[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
        pontos_curva = []

        num_segmentos = len(self.pontos_controle) - 3
        for i in range(num_segmentos):
            p0 = self.pontos_controle[i]
            p1 = self.pontos_controle[i + 1]
            p2 = self.pontos_controle[i + 2]
            p3 = self.pontos_controle[i + 3]

            Gx = [p0[0], p1[0], p2[0], p3[0]]
            Gy = [p0[1], p1[1], p2[1], p3[1]]

            Dx = [sum(E_M[row][col] * Gx[col] for col in range(4)) for row in range(4)]
            Dy = [sum(E_M[row][col] * Gy[col] for col in range(4)) for row in range(4)]

            x, dx, d2x, d3x = Dx[0], Dx[1], Dx[2], Dx[3]
            y, dy, d2y, d3y = Dy[0], Dy[1], Dy[2], Dy[3]

            # Adiciona o primeiro ponto apenas no início do primeiro segmento
            if i == 0:
                pontos_curva.append((x, y))

            # Loop de Forward Differences
            for _ in range(n):
                x += dx
                dx += d2x
                d2x += d3x

                y += dy
                dy += d2y
                d2y += d3y

                pontos_curva.append((x, y))

        return pontos_curva

    def transformar(self, matriz):
        """Aplica a transformação geométrica nos PONTOS DE CONTROLE e regenera a curva."""
        novos_controles = []
        for x, y in self.pontos_controle:
            nx = matriz[0][0]*x + matriz[0][1]*y + matriz[0][2]*1
            ny = matriz[1][0]*x + matriz[1][1]*y + matriz[1][2]*1
            novos_controles.append((nx, ny))
        
        self.pontos_controle = novos_controles
        self.vertices = self.gerar_curva()

    def centro_geometrico(self):
        """Calcula o centro geométrico baseado nos pontos de controle."""
        if not self.pontos_controle: return 0, 0
        cx = sum(v[0] for v in self.pontos_controle) / len(self.pontos_controle)
        cy = sum(v[1] for v in self.pontos_controle) / len(self.pontos_controle)
        return cx, cy