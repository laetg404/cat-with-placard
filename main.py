import turtle
import math
import random
import tkinter

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================

WIDTH, HEIGHT = 1000, 700
HORIZON = -120

screen = turtle.Screen()
screen.setup(WIDTH, HEIGHT)
screen.title("Un gatito para ti ♡")
screen.bgcolor("#FFF1E9")
screen.tracer(0)

static_pen = turtle.Turtle()   # fondo: se dibuja una sola vez
pen = turtle.Turtle()          # animación: se redibuja en cada cuadro
for t in (static_pen, pen):
    t.hideturtle()
    t.speed(0)
    t.penup()

P = static_pen  # lápiz activo

# Paleta
ORANGE = "#F2A65A"
LIGHT_ORANGE = "#FFCB8E"
CREAM = "#FFF1DC"
DARK_ORANGE = "#C46E2F"
OUTLINE = "#8C5232"
BROWN = "#5A3626"
PINK = "#F7A8BC"
SOFT_PINK = "#FFC9D6"
RED = "#E5586B"
WHITE = "#FFFFFF"
GOLD = "#F7C948"

SKY_TOP = "#FFCFCF"
SKY_BOTTOM = "#FFF4E8"
GROUND = "#F3BBA4"

# Vista actual (posición y escala del objeto que se dibuja)
VX, VY, VS = 0, 0, 1


def set_view(cx=0, cy=0, scale=1):
    global VX, VY, VS
    VX, VY, VS = cx, cy, scale


# ==========================================
# UTILIDADES
# ==========================================

def hex_to_rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def tf(p):
    return VX + p[0] * VS, VY + p[1] * VS


def bezier(p0, p1, p2, p3, n=14):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def quad(p0, p1, p2, n=8):
    return bezier(p0, ((p0[0] + 2 * p1[0]) / 3, (p0[1] + 2 * p1[1]) / 3),
                  ((p2[0] + 2 * p1[0]) / 3, (p2[1] + 2 * p1[1]) / 3), p2, n)


# ==========================================
# FUNCIONES DE DIBUJO
# ==========================================

def poly(points, fill, outline=None, width=2):
    if outline is None:
        outline, width = fill, 1
    P.penup()
    P.goto(*tf(points[0]))
    P.color(outline, fill)
    P.pensize(max(1, width * VS))
    P.pendown()
    P.begin_fill()
    for p in points[1:]:
        P.goto(*tf(p))
    P.goto(*tf(points[0]))
    P.end_fill()
    P.penup()


def ellipse(x, y, rx, ry, fill, outline=OUTLINE, width=2, rot=0, seg=36):
    r = math.radians(rot)
    pts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ex, ey = rx * math.cos(a), ry * math.sin(a)
        pts.append((x + ex * math.cos(r) - ey * math.sin(r),
                    y + ex * math.sin(r) + ey * math.cos(r)))
    poly(pts, fill, outline, width)


def line(points, color=OUTLINE, width=2):
    P.penup()
    P.goto(*tf(points[0]))
    P.pencolor(color)
    P.pensize(max(1, width * VS))
    P.pendown()
    for p in points[1:]:
        P.goto(*tf(p))
    P.penup()


def rounded_rect(x, y, w, h, r, fill, outline=None, width=2):
    pts = []
    corners = [(x + w / 2 - r, y + h / 2 - r, 0), (x - w / 2 + r, y + h / 2 - r, 90),
               (x - w / 2 + r, y - h / 2 + r, 180), (x + w / 2 - r, y - h / 2 + r, 270)]
    for cx, cy, start in corners:
        for i in range(9):
            a = math.radians(start + 90 * i / 8)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    poly(pts, fill, outline, width)


def star(x, y, r, color):
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.22
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    poly(pts, color)


def heart(x, y, s, color, outline=None, width=1):
    pts = []
    for i in range(41):
        t = 2 * math.pi * i / 40
        px = 16 * math.sin(t) ** 3
        py = (13 * math.cos(t) - 5 * math.cos(2 * t)
              - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x + px * s, y + py * s))
    poly(pts, color, outline, width)


def text(x, y, msg, size, color, font="Georgia", style="bold italic",
         shadow=None, align="center"):
    px, py = tf((x, y))
    fnt = (font, max(1, int(size * VS)), style)
    if shadow:
        P.penup()
        P.goto(px + 2, py - 2)
        P.color(shadow)
        P.write(msg, align=align, font=fnt)
    P.penup()
    P.goto(px, py)
    P.color(color)
    P.write(msg, align=align, font=fnt)


# ==========================================
# FONDO ESTÁTICO (se dibuja una sola vez)
# ==========================================

def draw_static_background():
    global P
    P = static_pen
    set_view()

    # Cielo con degradado
    bands = 56
    for i in range(bands):
        y0 = HEIGHT / 2 - i * HEIGHT / bands
        y1 = y0 - HEIGHT / bands - 1
        c = lerp_color(SKY_TOP, SKY_BOTTOM, i / (bands - 1))
        poly([(-WIDTH / 2, y0), (WIDTH / 2, y0), (WIDTH / 2, y1), (-WIDTH / 2, y1)], c)

    # Halo suave detrás del gatito
    for i in range(9):
        r = 340 - i * 34
        ellipse(-40, 30, r, r * 0.85,
                lerp_color("#FFE0D2", "#FFF9F1", i / 8), outline=None)

    # Colinas lejanas
    ellipse(-380, HORIZON - 40, 420, 120, "#F9D5C4", outline=None, seg=48)
    ellipse(330, HORIZON - 50, 460, 130, "#F7CBB9", outline=None, seg=48)

    # Suelo
    ellipse(0, HORIZON - 280, 760, 280, GROUND, outline=None, seg=60)
    ellipse(0, HORIZON - 300, 700, 250, "#F6C6B2", outline=None, seg=60)

    # Flores y pastito con perspectiva
    random.seed(11)
    for _ in range(26):
        x = random.randint(-470, 470)
        y = random.randint(-340, HORIZON - 12)
        s = 0.55 + (HORIZON - y) / 260
        line([(x, y), (x, y - 14 * s)], "#8FB48A", 2)
        c = random.choice([WHITE, SOFT_PINK, "#FFE29A"])
        for k in range(5):
            a = 2 * math.pi * k / 5
            ellipse(x + 5 * s * math.cos(a), y + 5 * s * math.sin(a),
                    3.6 * s, 3.6 * s, c, outline=None, seg=10)
        ellipse(x, y, 2.6 * s, 2.6 * s, GOLD, outline=None, seg=10)
    for _ in range(22):
        x = random.randint(-480, 480)
        y = random.randint(-345, HORIZON - 10)
        s = 0.6 + (HORIZON - y) / 300
        for dx in (-4, 0, 4):
            line([(x, y), (x + dx * 1.4 * s, y + 11 * s)], "#B7D3A8", 2)


# ==========================================
# ELEMENTOS ANIMADOS DEL ESCENARIO
# ==========================================

CLOUDS = [[-380, 250, 1.0, 0.18], [120, 290, 0.8, 0.12], [400, 190, 1.2, 0.22]]


def draw_clouds():
    for c in CLOUDS:
        c[0] += c[3]
        if c[0] > 620:
            c[0] = -620
        x, y, s = c[0], c[1], c[2]
        for dx, dy, rx, ry in [(0, 0, 50, 22), (-34, 8, 30, 18), (32, 10, 34, 20), (6, 18, 30, 20)]:
            ellipse(x + dx * s, y + dy * s, rx * s, ry * s, "#FFFFFF", outline=None, seg=24)


def draw_balloon(x, y, color, shine, phase):
    y += math.sin(phase) * 9
    sway = math.sin(phase * 0.8) * 10
    line(bezier((x, y - 48), (x - 12 + sway, y - 80), (x + 14 - sway, y - 115),
                (x + sway * 0.6, y - 160)), "#B89A8C", 2)
    ellipse(x, y, 32, 42, color, outline=None)
    ellipse(x + 6, y - 8, 26, 33, lerp_color(color, "#FFFFFF", 0.08), outline=None)
    ellipse(x - 11, y + 16, 6, 12, shine, outline=None, rot=25, seg=16)
    poly([(x - 6, y - 40), (x + 6, y - 40), (x, y - 51)], color)


def draw_balloons(frame):
    draw_balloon(-340, 190, PINK, "#FFF0F3", frame * 0.045)
    draw_balloon(340, 225, RED, "#FFD9DE", frame * 0.05)
    draw_balloon(425, 80, "#F5A16B", "#FFE6D2", frame * 0.04)
    draw_balloon(-430, 70, "#F7C86B", "#FFF2CF", frame * 0.06)


SPARKLES = [(-250, 280, 0), (180, 320, 1.5), (-120, 300, 3), (460, 290, 2),
            (-470, 250, 4), (60, 230, 5), (300, 150, 0.7), (-300, 120, 2.4)]


def draw_sparkles(frame):
    for x, y, ph in SPARKLES:
        s = 4 + 5 * (0.5 + 0.5 * math.sin(frame * 0.08 + ph))
        star(x, y, s, "#FFFFFF")


particles = []


def update_particles(frame, spawn):
    if spawn and frame % 6 == 0:
        particles.append({
            "x": random.randint(-420, 420), "y": -300,
            "s": random.uniform(0.35, 0.8),
            "c": random.choice([PINK, RED, SOFT_PINK]),
            "v": random.uniform(1.0, 2.2), "ph": random.uniform(0, 6.28)
        })
    for p in particles[:]:
        p["y"] += p["v"]
        p["x"] += math.sin(frame * 0.05 + p["ph"]) * 0.8
        if p["y"] > 380:
            particles.remove(p)
            continue
        heart(p["x"], p["y"], p["s"], p["c"])


# ==========================================
# LETRERO (coordenadas locales del gatito)
# ==========================================

def draw_sign():
    # Palo de madera
    line([(195, -22), (195, -192)], "#8A5A3B", 11)
    line([(195, -22), (195, -192)], "#C99A6B", 6)

    # Sombra y tablero
    rounded_rect(199, 33, 204, 120, 24, "#EBC7B6")
    rounded_rect(195, 38, 204, 120, 24, WHITE, "#E58E9E", 5)
    rounded_rect(195, 38, 188, 104, 18, "#FFF8F3", "#F7C3CC", 1.5)

    # Detalles
    heart(120, 82, 0.5, SOFT_PINK)
    heart(270, 82, 0.5, SOFT_PINK)
    star(278, 6, 5, GOLD)
    star(112, 8, 4, GOLD)

    text(195, 56, "Te amo,", 24, RED, shadow="#FFD9DE")
    text(195, 20, "mi amor", 20, DARK_ORANGE, shadow="#FBE3D2")
    heart(195, 1, 0.55, RED)


# ==========================================
# GATITO
# ==========================================

def draw_cat(cx, cy, scale, frame, walking):
    bob = abs(math.sin(frame * 0.22)) * 5 if walking else math.sin(frame * 0.05) * 1.5
    breath = math.sin(frame * 0.07) * 2
    set_view(cx, cy + bob, scale)

    # Sombra en el suelo
    set_view(cx, cy, scale)
    ellipse(0, -205, 95 - bob * 2, 15, "#E5AE97", outline=None)
    set_view(cx, cy + bob, scale)

    # Cola con curva suave y rayas
    sw = math.sin(frame * 0.13) * 22
    tail = bezier((-50, -160), (-150, -150), (-150 + sw, -50), (-98 + sw * 1.2, -30), 14)
    line(tail, DARK_ORANGE, 25)
    line(tail, ORANGE, 19)
    line(tail[4:6], DARK_ORANGE, 19)
    line(tail[8:10], DARK_ORANGE, 19)
    line(tail[12:], CREAM, 19)

    # Patitas traseras
    lm = math.sin(frame * 0.30) * 12 if walking else 0
    for sx, mv in ((-1, lm), (1, -lm)):
        ellipse(35 * sx + mv, -192, 27, 15, LIGHT_ORANGE)
        for k in (-8, 0, 8):
            line([(35 * sx + mv + k, -200), (35 * sx + mv + k, -193)], OUTLINE, 1.2)

    # Cuerpo
    ellipse(0, -105, 68, 95 + breath, ORANGE)
    ellipse(0, -128, 42, 64, CREAM, outline=None)

    # Rayitas del cuerpo
    for y in (-72, -100, -128):
        edge = 67 * math.sqrt(max(0, 1 - ((y + 105) / 95) ** 2))
        line([(-edge, y), (-edge + 17, y - 4)], DARK_ORANGE, 4)
        line([(edge, y), (edge - 17, y - 4)], DARK_ORANGE, 4)

    # Letrero (detrás del brazo y la cabeza)
    draw_sign()

    # Patita delantera izquierda
    ellipse(-38, -140, 20, 48, LIGHT_ORANGE)
    for k in (-6, 0, 6):
        line([(-38 + k, -184), (-38 + k, -176)], OUTLINE, 1.2)

    # Collar
    ellipse(0, -50, 56, 15, RED, outline="#B8404F", width=1.5)
    ellipse(0, -46, 56, 13, "#F2778A", outline=None)

    # Brazo derecho sujetando el palo
    line([(40, -70), (115, -88), (186, -86)], DARK_ORANGE, 31)
    line([(40, -70), (115, -88), (186, -86)], ORANGE, 26)
    ellipse(195, -86, 19, 17, LIGHT_ORANGE)
    for k in (-1, 1):
        line([(195 + 5 * k, -96), (195 + 5 * k, -90)], OUTLINE, 1.2)

    # Orejas (antes de la cabeza para que ésta las tape en la base)
    poly([(-82, 66), (-72, 160), (-10, 108)], ORANGE, OUTLINE, 2)
    poly([(82, 66), (72, 160), (10, 108)], ORANGE, OUTLINE, 2)
    poly([(-67, 92), (-64, 138), (-33, 108)], PINK)
    poly([(67, 92), (64, 138), (33, 108)], PINK)

    # Cabeza
    ellipse(0, 35, 92, 82, LIGHT_ORANGE)

    # Rayitas de la frente
    poly([(-29, 112), (-21, 112), (-25, 90)], DARK_ORANGE)
    poly([(-4, 116), (4, 116), (0, 90)], DARK_ORANGE)
    poly([(21, 112), (29, 112), (25, 90)], DARK_ORANGE)

    # Mechones de las mejillas
    poly([(-88, 42), (-108, 30), (-86, 18)], LIGHT_ORANGE, OUTLINE, 1.5)
    poly([(88, 42), (108, 30), (86, 18)], LIGHT_ORANGE, OUTLINE, 1.5)

    # Mejillas
    ellipse(-62, 16, 16, 10, "#F6A0A8", outline=None)
    ellipse(62, 16, 16, 10, "#F6A0A8", outline=None)

    # Hocico
    ellipse(-13, 11, 17, 13, CREAM, outline=None)
    ellipse(13, 11, 17, 13, CREAM, outline=None)

    # Ojos (con parpadeo)
    blink = (frame % 150) < 6
    for ex in (-34, 34):
        if blink:
            line(quad((ex - 12, 42), (ex, 32), (ex + 12, 42)), BROWN, 3)
        else:
            ellipse(ex, 44, 12, 16, "#3E2419", outline=None)
            ellipse(ex, 40, 9, 12, "#6B3F27", outline=None)
            ellipse(ex - 4, 50, 5, 6, WHITE, outline=None, seg=16)
            ellipse(ex + 5, 36, 2.4, 2.8, WHITE, outline=None, seg=12)

    # Nariz y boca
    poly([(-7, 26), (7, 26), (0, 17)], "#E27C8D", "#C95E70", 1.5)
    line([(0, 17), (0, 11)], BROWN, 2)
    line(quad((0, 11), (-5, 4), (-13, 8)), BROWN, 2)
    line(quad((0, 11), (5, 4), (13, 8)), BROWN, 2)

    # Bigotes curvos
    for sx in (-1, 1):
        for y0, y1, bend in ((18, 28, 6), (11, 11, 0), (4, -6, -6)):
            line(quad((sx * 52, y0), (sx * 78, y1 + bend), (sx * 104, y1)), "#9C6B52", 1.5)

    # Campanita del collar
    ellipse(0, -66, 10, 10, GOLD, outline="#C99A1E", width=1.5)
    line([(-6, -68), (6, -68)], "#C99A1E", 1.2)
    ellipse(0, -72, 2, 2, "#C99A1E", outline=None, seg=8)

    set_view()


# ==========================================
# ANIMACIÓN PRINCIPAL
# ==========================================

frame = 0
progress = 0.0
done_frame = None

draw_static_background()


def animate():
    global frame, progress, done_frame, P

    try:
        P = pen
        pen.clear()
        set_view()

        draw_clouds()
        draw_balloons(frame)
        draw_sparkles(frame)

        progress = min(progress + 0.0065, 1)
        smooth = progress * progress * (3 - 2 * progress)
        walking = progress < 1

        cat_x = -270 + 210 * smooth
        cat_y = -70 + 10 * smooth
        cat_scale = 0.30 + 0.75 * smooth

        if progress >= 1 and done_frame is None:
            done_frame = frame

        update_particles(frame, spawn=progress > 0.75)

        draw_cat(cat_x, cat_y, cat_scale, frame, walking)

        # Título con aparición suave
        fade = frame / 40
        text(0, 282, "Un gatito para ti", 30,
             lerp_color(SKY_TOP, "#D9566E", fade), shadow=lerp_color(SKY_TOP, WHITE, fade))

        # Mensaje final
        if done_frame is not None:
            f = (frame - done_frame) / 45
            col = lerp_color(GROUND, "#B04A60", f)
            text(0, -330, "He venido a recordarte que te amo", 20, col,
                 shadow=lerp_color(GROUND, "#FFE8E0", f))
            pulse = 0.55 + 0.08 * math.sin(frame * 0.15)
            heart(-245, -318, pulse, lerp_color(GROUND, RED, f))
            heart(245, -318, pulse, lerp_color(GROUND, RED, f))

        screen.update()
        frame += 1
        screen.ontimer(animate, 30)
    except (turtle.Terminator, tkinter.TclError):
        pass


animate()
try:
    screen.mainloop()
except (turtle.Terminator, tkinter.TclError):
    pass