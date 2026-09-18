# clipping.py

# Regiões para Cohen-Sutherland
INSIDE = 0  # 0000
LEFT = 1    # 0001
RIGHT = 2   # 0010
BOTTOM = 4  # 0100
TOP = 8     # 1000

def _calcular_codigo(x, y, xmin=-1.0, ymin=-1.0, xmax=1.0, ymax=1.0):
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code

# 1. Clipagem de Ponto
def clip_ponto(x, y, xmin=-1.0, ymin=-1.0, xmax=1.0, ymax=1.0):
    if xmin <= x <= xmax and ymin <= y <= ymax:
        return (x, y)
    return None

# 2. Clipagem de Reta - Cohen-Sutherland
def clip_reta_cohen_sutherland(x1, y1, x2, y2, xmin=-1.0, ymin=-1.0, xmax=1.0, ymax=1.0):
    code1 = _calcular_codigo(x1, y1, xmin, ymin, xmax, ymax)
    code2 = _calcular_codigo(x2, y2, xmin, ymin, xmax, ymax)

    while True:
        if code1 == 0 and code2 == 0:
            return (x1, y1, x2, y2)
        elif (code1 & code2) != 0:
            return None
        else:
            code_out = code1 if code1 != 0 else code2
            x, y = 0.0, 0.0

            if code_out & TOP:
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1) if y2 != y1 else x1
                y = ymax
            elif code_out & BOTTOM:
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1) if y2 != y1 else x1
                y = ymin
            elif code_out & RIGHT:
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1) if x2 != x1 else y1
                x = xmax
            elif code_out & LEFT:
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1) if x2 != x1 else y1
                x = xmin

            if code_out == code1:
                x1, y1 = x, y
                code1 = _calcular_codigo(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                code2 = _calcular_codigo(x2, y2, xmin, ymin, xmax, ymax)

# 3. Clipagem de Reta - Liang-Barsky
def clip_reta_liang_barsky(x1, y1, x2, y2, xmin=-1.0, ymin=-1.0, xmax=1.0, ymax=1.0):
    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]

    u1 = 0.0
    u2 = 1.0

    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return None
        else:
            r = q[i] / p[i]
            if p[i] < 0:
                if r > u2:
                    return None
                if r > u1:
                    u1 = r
            else:
                if r < u1:
                    return None
                if r < u2:
                    u2 = r

    nx1 = x1 + u1 * dx
    ny1 = y1 + u1 * dy
    nx2 = x1 + u2 * dx
    ny2 = y1 + u2 * dy

    return (nx1, ny1, nx2, ny2)

# 4. Clipagem de Polígono - Sutherland-Hodgman
def clip_poligono_sutherland_hodgman(polygon, xmin=-1.0, ymin=-1.0, xmax=1.0, ymax=1.0):
    if not polygon:
        return []

    def inside(p, edge):
        x, y = p
        if edge == 'left':   return x >= xmin
        if edge == 'right':  return x <= xmax
        if edge == 'bottom': return y >= ymin
        if edge == 'top':    return y <= ymax

    def intersect(p1, p2, edge):
        x1, y1 = p1
        x2, y2 = p2
        if edge == 'left':
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1) if x2 != x1 else y1
            return (xmin, y)
        elif edge == 'right':
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1) if x2 != x1 else y1
            return (xmax, y)
        elif edge == 'bottom':
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1) if y2 != y1 else x1
            return (x, ymin)
        elif edge == 'top':
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1) if y2 != y1 else x1
            return (x, ymax)

    output_list = list(polygon)

    for edge in ['left', 'right', 'bottom', 'top']:
        input_list = output_list
        output_list = []
        if not input_list:
            break

        s = input_list[-1]
        for p in input_list:
            if inside(p, edge):
                if inside(s, edge):
                    output_list.append(p)
                else:
                    output_list.append(intersect(s, p, edge))
                    output_list.append(p)
            elif inside(s, edge):
                output_list.append(intersect(s, p, edge))
            s = p

    return output_list