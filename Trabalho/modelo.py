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
    def __init__(self, nome, tipo, vertices, cor="#1a73e8", preenchido=False, cor_preenchimento="#8ab4f8"):
        self.nome = nome
        self.tipo = tipo  # "ponto", "reta", "wireframe" / "poligono", "curva"
        self.vertices = vertices
        self.cor = cor
        self.preenchido = preenchido
        self.cor_preenchimento = cor_preenchimento

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

class Curva2D(ObjetoGrafico):
    def __init__(self, nome, pontos_controle, passos=20, cor="#1a73e8"):
        """
        pontos_controle: Lista de tuplas/pontos [(P0), (P1), (V0), (V1), ...]
        passos: Número de divisões/segmentos por sub-curva de Hermite
        """
        self.pontos_controle = pontos_controle
        self.algoritmo = "hermite"
        self.passos = passos
        
        # Gera os vértices aproximados (segmentos de reta) para renderização
        vertices_gerados = self.gerar_pontos_curva()
        
        super().__init__(nome=nome, tipo="curva", vertices=vertices_gerados, cor=cor)

    def transformar(self, matriz):
        novos_pc = []
        for x, y in self.pontos_controle:
            nx = matriz[0][0]*x + matriz[0][1]*y + matriz[0][2]*1
            ny = matriz[1][0]*x + matriz[1][1]*y + matriz[1][2]*1
            novos_pc.append((nx, ny))
        self.pontos_controle = novos_pc
        self.vertices = self.gerar_pontos_curva()

    def gerar_pontos_curva(self):
        if len(self.pontos_controle) < 4:
            return list(self.pontos_controle)

        vertices = []
        
        # Agrupa de 4 em 4: P0 (ponto inicial), P1 (ponto final), V0 (vetor tangente inicial), V1 (vetor tangente final)
        # Para continuidade G(0), a sub-curva seguinte é formada a partir dos próximos pontos
        i = 0
        while i + 3 < len(self.pontos_controle):
            p0, p1, v0, v1 = self.pontos_controle[i:i+4]
            for step in range(self.passos + 1):
                t = step / float(self.passos)
                
                # Funções de blending de Hermite
                h1 = 2*(t**3) - 3*(t**2) + 1
                h2 = -2*(t**3) + 3*(t**2)
                h3 = t**3 - 2*(t**2) + t
                h4 = t**3 - t**2
                
                x = h1 * p0[0] + h2 * p1[0] + h3 * v0[0] + h4 * v1[0]
                y = h1 * p0[1] + h2 * p1[1] + h3 * v0[1] + h4 * v1[1]
                
                if step == 0 and len(vertices) > 0:
                    continue
                vertices.append((x, y))
            i += 3

        return vertices

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
                for v in obj.vertices:
                    f.write(f"v {v[0]} {v[1]} 0.0\n")
                
                prefixo = "f " if (obj.preenchido and obj.tipo == "wireframe") else "l "
                f.write(prefixo)
                for i in range(len(obj.vertices)):
                    f.write(f"{offset + i} ")
                if not obj.preenchido and obj.tipo in ["wireframe", "triangulo"]:
                    f.write(f"{offset}")
                f.write("\n")
                offset += len(obj.vertices)

    @staticmethod
    def importar(filepath):
        objetos = []
        vertices_globais = []
        nome_atual = "ObjImportado"
        try:
            with open(filepath, 'r') as f:
                for linha in f:
                    partes = linha.strip().split()
                    if not partes: continue
                    
                    if partes[0] == 'o':
                        nome_atual = partes[1]
                    elif partes[0] == 'v':
                        vertices_globais.append((float(partes[1]), float(partes[2])))
                    elif partes[0] in ['l', 'f', 'p']:
                        indices = [int(i.split('/')[0]) - 1 for i in partes[1:]]
                        v_obj = [vertices_globais[i] for i in indices]
                        tipo = "ponto" if len(v_obj) == 1 else "reta" if len(v_obj) == 2 else "wireframe"
                        preenchido = (partes[0] == 'f')
                        objetos.append(ObjetoGrafico(nome_atual, tipo, v_obj, preenchido=preenchido))
                        nome_atual = f"Obj_{len(objetos)+1}"
            return objetos
        except Exception:
            return []