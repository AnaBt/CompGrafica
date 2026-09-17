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
                for v in obj.vertices:
                    f.write(f"v {v[0]} {v[1]} 0.0\n")
                
                f.write("l ")
                for i in range(len(obj.vertices)):
                    f.write(f"{offset + i} ")
                if obj.tipo in ["wireframe", "triangulo"]:
                    f.write(f"{offset}") # Fecha polígono
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
                        objetos.append(ObjetoGrafico(nome_atual, tipo, v_obj))
                        nome_atual = f"Obj_{len(objetos)+1}"
            return objetos
        except Exception:
            return []