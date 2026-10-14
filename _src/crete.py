"""Ligne de crête des Dentelles de Montmirail, dessinée une fois (graine fixe) : un massif qui monte doucement
   depuis les coteaux, et trois crêtes calcaires dentelées en haut, séparées par des cols."""
import math, os, random
ICI = os.path.dirname(os.path.abspath(__file__))
random.seed(1958)
W, H, BASE = 1600, 200, 192
g = lambda x, c, w: math.exp(-((x - c) / w) ** 2)
def massif(x):
    return (BASE - 8 * math.sin(x / 190 + .4) - 5 * math.sin(x / 61)
            - 62 * g(x, 800, 250) - 30 * g(x, 560, 150) - 26 * g(x, 1120, 170) - 14 * g(x, 300, 220))
# trois crêtes : (début, fin, hauteur max des dents)
cretes = [(600, 735, 30), (770, 965, 46), (1000, 1085, 24)]
dents = []
for a, b, hmax in cretes:
    x = a
    while x < b:
        l = random.uniform(7, 22)
        bord = min(1, (x - a) / 30, (b - x) / 30)
        h = hmax * random.uniform(.35, 1) * (.4 + .6 * bord)
        dents.append((x, x + l, h, random.uniform(.25, .75)))
        x += l
def profil(x):
    y = massif(x)
    for a, b, h, s in dents:
        if a <= x <= b:
            p = a + (b - a) * s
            t = (x - a) / (p - a) if x <= p else (b - x) / (b - p)
            y -= h * (t ** 1.3)
    for a, b, hmax in cretes:   # le pied des crêtes se relève un peu
        if a - 25 <= x <= b + 25:
            y -= 10 * min(1, (x - a + 25) / 25, (b + 25 - x) / 25)
    return y
pts = []
x = 0.0
while x <= W:
    pts.append((x, profil(x)))
    x += 1.0
simp = [pts[0]]
for i in range(1, len(pts) - 1):
    (x0, y0), (x1, y1), (x2, y2) = simp[-1], pts[i], pts[i + 1]
    if abs(math.atan2(y1 - y0, x1 - x0) - math.atan2(y2 - y1, x2 - x1)) > .05 or x1 - x0 > 40:
        simp.append(pts[i])
simp.append(pts[-1])
d = 'M' + ' L'.join(f'{x:.0f} {y:.1f}' for x, y in simp)
print(len(simp), len(d))
open(os.path.join(ICI, 'crete.txt'), 'w').write(d)
open(os.path.join(ICI, 'crete.svg'), 'w').write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="1600" height="200" style="background:#151112">'
    f'<path d="{d} L{W} {H} L0 {H} Z" fill="#2a2122"/><path d="{d}" fill="none" stroke="#e2b4a8" stroke-width="1.2"/></svg>')
