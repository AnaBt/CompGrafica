import math
from modelo import Transformacoes

class Window:
    def __init__(self, cx, cy, largura, altura):
        self.cx = cx
        self.cy = cy
        self.largura = largura
        self.altura = altura
        self.angulo = 0.0  # Em graus

    def mover(self, passo_frente, passo_lado):
        rad = math.radians(self.angulo)
        # Frente/Trás orientados pelo ângulo da câmera
        self.cx -= passo_frente * math.sin(rad)
        self.cy += passo_frente * math.cos(rad)
        # Lados orientados pelo ângulo da câmera
        self.cx += passo_lado * math.cos(rad)
        self.cy += passo_lado * math.sin(rad)

    def zoom(self, fator):
        self.largura *= fator
        self.altura *= fator

    def rotacionar(self, angulo):
        self.angulo = (self.angulo + angulo) % 360

    def matriz_scn(self):
        # 1. Translada o centro para origem
        t = Transformacoes.translacao(-self.cx, -self.cy)
        # 2. Rotaciona o mundo na direção OPOSTA à da Window
        r = Transformacoes.rotacao(-self.angulo)
        # 3. Normaliza para o espaço SCN [-1, 1]
        s = Transformacoes.escala(2.0 / self.largura, 2.0 / self.altura)
        
        # CORREÇÃO: Como M * P é lido da direita para a esquerda pela matemática,
        # a ordem correta para o SCN é Escala * Rotação * Translação.
        return Transformacoes.encadear(s, r, t)

class Viewport:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.largura_vp = xmax - xmin
        self.altura_vp = ymax - ymin

    def transformar_scn(self, x_scn, y_scn):
        # Mapeia de SCN [-1, 1] para Canvas (com Y invertido para tela gráfica)
        xvp = self.xmin + ((x_scn + 1) / 2) * self.largura_vp
        yvp = self.ymin + ((1 - y_scn) / 2) * self.altura_vp
        return xvp, yvp