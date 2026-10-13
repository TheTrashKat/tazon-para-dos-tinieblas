"""Generador de Tazón para Dos · Tinieblas (sub-marca oscura).

Escribe, a partir de la paleta de este archivo y de los logos originales en tools/origen/:
  brand/tokens.css, brand/tokens.json, brand/brand.json
  assets/logo/*.svg          logos recoloreados (se parte de los SVG originales, no se redibujan)
  assets/elementos/*.svg     ornamentos oscuros (luna, niebla, humedal, d20 agrietado, greca muisca…)
  assets/iconos/*.svg        íconos nuevos + sprite.svg con los 21 originales y los nuevos
  tema-tinieblas.css         tema de pantalla / noche para D:\\herramientas\\pdf-historias
  tema-tinieblas-pergamino.css  variante para imprimir (páginas pergamino, portadas oscuras)
  index.html                 rellena la tabla de contraste entre <!--contraste--> y <!--/contraste-->

Uso:  python -I tools/build.py
"""
import json, math, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ORIGEN = ROOT / "tools" / "origen"
FONTS = ROOT / "tools" / "fonts"

# ------------------------------------------------------------------ paleta
PALETA = {
    # fondos
    "abismo":          ("#110D18", "Abismo", "fondo", "Tinta #28203B llevada al fondo del pozo. Fondo más oscuro, contornos y sombras."),
    "noche":           ("#1C1629", "Noche", "fondo", "Fondo principal de pantalla y páginas."),
    "niebla":          ("#2B2340", "Niebla", "fondo", "Superficies elevadas: tarjetas, recuadros, paneles."),
    "pergamino":       ("#E9DDC1", "Pergamino", "fondo", "Crema #F7F2E8 envejecida. Texto sobre oscuro y fondo de impresión."),
    "pergamino_viejo": ("#D9C9A3", "Pergamino viejo", "fondo", "Recuadros sobre pergamino, papel manchado."),
    # acentos
    "musgo":           ("#7FA68C", "Musgo de humedal", "acento", "Turquesa #55C4BF apagada hacia el verde del humedal Jaboque."),
    "musgo_profundo":  ("#3E5E50", "Musgo profundo", "acento", "Bloques de color con texto pergamino encima."),
    "sangre":          ("#9E3A48", "Sangre seca", "acento", "Coral #EA6077 oxidado. Bloques, sombras duras, triángulo de esquina."),
    "coral_ceniza":    ("#E07D84", "Coral ceniza", "acento", "La versión del coral que sí se lee como texto sobre fondos oscuros."),
    "vela":            ("#E3B35C", "Oro de vela", "acento", "Sol #F8CB67 a la luz de una vela. Franjas, destellos, dados, CTA."),
    "ambar":           ("#7E5A1E", "Ámbar", "acento", "El oro de vela cuando va como texto sobre pergamino."),
    # texto
    "luna":            ("#CFCADF", "Luna", "texto", "Texto secundario y líneas finas sobre oscuro."),
    "ceniza":          ("#A39AB0", "Ceniza", "texto", "Texto atenuado, pies de foto, bordes sobre oscuro."),
    "tinta":           ("#28203B", "Tinta (original)", "texto", "La tinta de siempre, para texto sobre pergamino."),
    "tinta_suave":     ("#5A4E66", "Tinta suave", "texto", "Texto atenuado sobre pergamino."),
}
H = {k: v[0] for k, v in PALETA.items()}
ABISMO, NOCHE, NIEBLA, PERG, PERG_V = H["abismo"], H["noche"], H["niebla"], H["pergamino"], H["pergamino_viejo"]
MUSGO, MUSGO_P, SANGRE, CORAL_C, VELA, AMBAR = H["musgo"], H["musgo_profundo"], H["sangre"], H["coral_ceniza"], H["vela"], H["ambar"]
LUNA, CENIZA, TINTA, TINTA_S = H["luna"], H["ceniza"], H["tinta"], H["tinta_suave"]
OUT = "#0B0811"          # contorno de las ilustraciones (más oscuro que abismo)
VELA_L = "#EDC983"       # cara interior del d20
LUNA_S = "#ADA6C4"       # cráteres
ORIGINAL = {"ink": "#28203B", "teal": "#55C4BF", "coral": "#EA6077", "sun": "#F8CB67", "cream": "#F7F2E8", "paper": "#FFFDF8"}


# ------------------------------------------------------------------ contraste WCAG
def _lum(h):
    h = h.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contraste(a, b):
    la, lb = sorted([_lum(a), _lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


PARES = [  # (texto, fondo, uso)
    ("pergamino", "abismo", "Texto principal"), ("pergamino", "noche", "Texto principal"),
    ("pergamino", "niebla", "Texto en tarjetas"), ("luna", "noche", "Texto secundario"),
    ("ceniza", "noche", "Pies de foto, etiquetas"), ("ceniza", "niebla", "Atenuado en tarjetas"),
    ("vela", "noche", "Destacados, enlaces"), ("musgo", "noche", "Destacados"),
    ("coral_ceniza", "noche", "Avisos, rótulos"), ("coral_ceniza", "niebla", "Rótulos en tarjetas"),
    ("abismo", "vela", "Botones y píldoras"), ("abismo", "musgo", "Píldoras"),
    ("pergamino", "sangre", "Texto en bloque sangre"), ("pergamino", "musgo_profundo", "Texto en bloque musgo"),
    ("tinta", "pergamino", "Texto impreso"), ("tinta_suave", "pergamino", "Atenuado impreso"),
    ("sangre", "pergamino", "Titulares impresos"), ("ambar", "pergamino", "Oro como texto impreso"),
    ("musgo_profundo", "pergamino", "Musgo como texto impreso"), ("tinta", "pergamino_viejo", "Recuadros impresos"),
    ("vela", "pergamino", "NO: oro sobre pergamino"), ("sangre", "noche", "NO: sangre como texto en la noche"),
    ("pergamino", "musgo", "NO salvo titular grande con sombra"),
]


def tabla_contraste():
    filas = []
    for fg, bg, uso in PARES:
        c = contraste(H[fg], H[bg])
        nivel = "AAA" if c >= 7 else "AA" if c >= 4.5 else "AA grande" if c >= 3 else "No"
        filas.append({"texto": fg, "fondo": bg, "hex_texto": H[fg], "hex_fondo": H[bg],
                      "ratio": round(c, 2), "nivel": nivel, "uso": uso})
    return filas


# ------------------------------------------------------------------ utilidades
_font_cache = {}


def text_path(text, font, size, x, y, fill, anchor="start", tracking=0.0):
    """Texto a contornos (igual que tools/build.py del kit original)."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    if font not in _font_cache:
        f = TTFont(FONTS / font)
        _font_cache[font] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm, f["hmtx"])
    f, gs, cmap, upm, hmtx = _font_cache[font]
    s = size / upm
    names = [cmap.get(ord(ch), ".notdef") for ch in text]
    width = sum(hmtx[n][0] * s for n in names) + tracking * (len(names) - 1)
    cursor = x - (width / 2 if anchor == "middle" else 0)
    pen = SVGPathPen(gs)
    for n in names:
        gs[n].draw(TransformPen(pen, (s, 0, 0, -s, cursor, y)))
        cursor += hmtx[n][0] * s + tracking
    return f'<path fill="{fill}" d="{pen.getCommands()}"/>', width


COND, SANS = "BarlowCondensed-ExtraBold.ttf", "Barlow-SemiBold.ttf"


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print("  ", rel)


def recolor(svg, colores):
    """Sustituye, en orden de aparición, cada fill/stroke con color hexadecimal."""
    it = iter(colores)
    return re.sub(r'(fill|stroke)="#[0-9A-Fa-f]{6}"', lambda m: f'{m.group(1)}="{next(it)}"', svg)


def svg_uri(svg):
    s = re.sub(r"\s+", " ", svg.strip())
    return "data:image/svg+xml;utf8," + s.replace("%", "%25").replace("#", "%23").replace('"', "'")


def crescent(cx, cy, R, ox, oy, r):
    """Luna creciente = círculo (cx,cy,R) menos círculo (ox,oy,r). Devuelve un path."""
    d = math.hypot(ox - cx, oy - cy)
    a = (R * R - r * r + d * d) / (2 * d)
    h = math.sqrt(R * R - a * a)
    ux, uy = (ox - cx) / d, (oy - cy) / d
    px, py = cx + a * ux, cy + a * uy
    p1 = (px - h * uy, py + h * ux)
    p2 = (px + h * uy, py - h * ux)

    def arco(c, rad, p_ini, p_fin, dentro):
        a0 = math.atan2(p_ini[1] - c[1], p_ini[0] - c[0])
        a1 = math.atan2(p_fin[1] - c[1], p_fin[0] - c[0])
        for sentido in (1, -1):
            span = (a1 - a0) * sentido % (2 * math.pi)
            mid = a0 + sentido * span / 2
            mx, my = c[0] + rad * math.cos(mid), c[1] + rad * math.sin(mid)
            if dentro(mx, my):
                return f"A{rad} {rad} 0 {1 if span > math.pi else 0} {1 if sentido > 0 else 0} {p_fin[0]:.2f} {p_fin[1]:.2f}"
        raise ValueError
    fuera_c2 = lambda x, y: math.hypot(x - ox, y - oy) > r
    dentro_c1 = lambda x, y: math.hypot(x - cx, y - cy) < R
    return (f"M{p1[0]:.2f} {p1[1]:.2f} " + arco((cx, cy), R, p1, p2, fuera_c2) + " "
            + arco((ox, oy), r, p2, p1, dentro_c1) + "Z")


def sparkle(cx, cy, s, fill, stroke=OUT, sw=None):
    sw = sw if sw is not None else 0.12 * 100
    return (f'<path transform="translate({cx},{cy}) scale({s / 100})" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" '
            'd="M0,-50 C6,-10 10,-6 50,0 C10,6 6,10 0,50 C-6,10 -10,6 -50,0 C-10,-6 -6,-10 0,-50 Z"/>')


def spiral_points(cx, cy, r0, paso, vueltas, n=220, giro=0.0):
    pts = []
    for i in range(n + 1):
        t = vueltas * 2 * math.pi * i / n
        r = r0 + paso * t / (2 * math.pi)
        pts.append((cx + r * math.cos(t + giro), cy + r * math.sin(t + giro)))
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def bowl(body, face):
    """La mascota original (misma geometría que el kit), en caja 120 x 124."""
    src = (ORIGEN / "logo" / "mascota.svg").read_text(encoding="utf-8")
    inner = re.search(r"</title>(.*)</svg>", src, re.S).group(1)
    return recolor(inner, [body, body, face])


# ------------------------------------------------------------------ logos
def build_logos():
    lg = ORIGEN / "logo"
    sello_o = (lg / "sello.svg").read_text(encoding="utf-8")
    hor_o = (lg / "logotipo-horizontal.svg").read_text(encoding="utf-8")
    api_o = (lg / "logotipo-apilado.svg").read_text(encoding="utf-8")
    fav_o = (lg / "favicon.svg").read_text(encoding="utf-8")
    titulo = lambda s, t: re.sub(r"<title>.*?</title>", f"<title>{t}</title>", s)

    OSCURO = [NOCHE, VELA, LUNA, PERG, NOCHE]          # fondo sello, aro, vapor, tazón, cara
    CLARO = [PERG, TINTA, TINTA, TINTA, PERG]

    write("assets/logo/sello-tinieblas.svg", titulo(recolor(sello_o, OSCURO), "Sello Tazón para Dos · Tinieblas"))
    write("assets/logo/sello-tinieblas-pergamino.svg", titulo(recolor(sello_o, CLARO), "Sello Tazón para Dos · Tinieblas (pergamino)"))
    write("assets/logo/mascota-tinieblas.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 124" width="480" height="496"><title>Mascota · Tinieblas</title>{bowl(PERG, NOCHE)}</svg>\n')
    write("assets/logo/favicon.svg",
          titulo(recolor(fav_o, [NOCHE, PERG, PERG, NOCHE]), "Favicon Tazón para Dos · Tinieblas")
          .replace('<circle cx="32" cy="32" r="31" fill="' + NOCHE + '"/>',
                   f'<circle cx="32" cy="32" r="29.5" fill="{NOCHE}" stroke="{VELA}" stroke-width="3"/>'))

    # Sello de luna: el sello original dentro de un aro con dientes muiscas y una luna creciente.
    dientes = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        a1, a2 = a - math.pi / 36, a + math.pi / 36
        p = lambda ang, rad: f"{100 + rad * math.cos(ang):.2f},{100 + rad * math.sin(ang):.2f}"
        dientes.append(f"M{p(a1, 84)} L{p(a, 93)} L{p(a2, 84)}Z")
    sello_inner = re.search(r"</title>(.*)</svg>", recolor(sello_o, OSCURO), re.S).group(1)
    luna_p = crescent(158, 40, 22, 168, 32, 18)
    write("assets/logo/sello-luna.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="600" height="600"><title>Sello de luna · Tazón para Dos · Tinieblas</title>'
          f'<circle cx="100" cy="100" r="96" fill="{ABISMO}" stroke="{VELA}" stroke-width="4"/>'
          f'<path fill="{VELA}" d="{" ".join(dientes)}"/>'
          f'<circle cx="100" cy="100" r="84" fill="none" stroke="{VELA}" stroke-width="2.5"/>'
          f'<g transform="translate(20,20)">{sello_inner}</g>'
          f'<path d="{luna_p}" fill="{LUNA}" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/></svg>\n')

    def con_tinieblas(svg, base_w, x, y, fill, luna_fill, anchor="start", alto=None):
        """Añade «☾ TINIEBLAS» en la fila del descriptor."""
        palabra, w = text_path("TINIEBLAS", SANS, 20 if anchor == "start" else 18, 0, 0, fill, tracking=7)
        if anchor == "middle":
            total = 26 + w
            x0 = x - total / 2
        else:
            x0 = x
        lp = crescent(x0 + 8, y - 7, 8, x0 + 12, y - 10, 6.6)
        palabra, w = text_path("TINIEBLAS", SANS, 20 if anchor == "start" else 18, x0 + 26, y, fill, tracking=7)
        out = svg.replace("</svg>", f'<path d="{lp}" fill="{luna_fill}"/>{palabra}</svg>')
        need = int(x0 + 26 + w + 16)
        if need > base_w and anchor == "start":
            out = re.sub(r'viewBox="0 0 \d+ (\d+)" width="\d+" height="(\d+)"',
                         lambda m: f'viewBox="0 0 {need} {m.group(1)}" width="{need * 2}" height="{m.group(2)}"', out, count=1)
        if alto:
            out = re.sub(r'viewBox="0 0 (\d+) \d+" width="(\d+)" height="\d+"',
                         lambda m: f'viewBox="0 0 {m.group(1)} {alto}" width="{m.group(2)}" height="{alto * 2}"', out, count=1)
        return out

    hw = int(re.search(r'viewBox="0 0 (\d+)', hor_o).group(1))
    # ancho del descriptor original, para colocar TINIEBLAS a continuación
    _, w_sub = text_path("ESPACIO CULTURAL", SANS, 20, 199, 140, "#000", tracking=7)
    x_t = 199 + w_sub + 20
    for nombre, cols, fill_t, luna_f, fondo in (
            ("logotipo-horizontal-tinieblas", [NOCHE, VELA, LUNA, PERG, NOCHE, PERG, LUNA], VELA, VELA, None),
            ("logotipo-horizontal-tinieblas-fondo", [NOCHE, VELA, LUNA, PERG, NOCHE, PERG, LUNA], VELA, VELA, ABISMO),
            ("logotipo-horizontal-tinieblas-pergamino", [PERG, TINTA, TINTA, TINTA, PERG, TINTA, TINTA], SANGRE, SANGRE, None)):
        s = con_tinieblas(titulo(recolor(hor_o, cols), "Logotipo horizontal Tazón para Dos · Tinieblas"), hw, x_t, 140, fill_t, luna_f)
        if fondo:
            vw = re.search(r'viewBox="0 0 (\d+) (\d+)"', s)
            s = s.replace("</title>", f'</title><rect width="{vw.group(1)}" height="{vw.group(2)}" fill="{fondo}"/>', 1)
        write(f"assets/logo/{nombre}.svg", s)

    aw = int(re.search(r'viewBox="0 0 (\d+)', api_o).group(1))
    for nombre, cols, fill_t, fondo in (
            ("logotipo-apilado-tinieblas", [NOCHE, VELA, LUNA, PERG, NOCHE, PERG, LUNA], VELA, None),
            ("logotipo-apilado-tinieblas-pergamino", [PERG, TINTA, TINTA, TINTA, PERG, TINTA, TINTA], SANGRE, None)):
        s = con_tinieblas(titulo(recolor(api_o, cols), "Logotipo apilado Tazón para Dos · Tinieblas"), aw, aw / 2, 336, fill_t, fill_t,
                          anchor="middle", alto=356)
        write(f"assets/logo/{nombre}.svg", s)


# ------------------------------------------------------------------ ornamentos
def el(nombre, titulo, cuerpo, vb="0 0 440 440", w=440, h=440):
    write(f"assets/elementos/{nombre}.svg",
          f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">\n  <title>{titulo} · Tazón para Dos · Tinieblas</title>\n'
          f'  <!-- Generado por tools/build.py · abismo {ABISMO} · noche {NOCHE} · pergamino {PERG} · musgo {MUSGO} · sangre {SANGRE} · vela {VELA} · luna {LUNA} -->\n'
          f'{cuerpo}\n</svg>\n')


def d20_agrietado(cuerpo=VELA, cara=VELA_L, numero="20"):
    V = [(0, -200), (173, -100), (173, 100), (0, 200), (-173, 100), (-173, -100)]
    hexa = "M" + " L".join(f"{x},{y}" for x, y in V) + " Z"
    num, _ = text_path(numero, COND, 92, 0, 36, OUT, anchor="middle")
    grieta = "M-86,-150 L-62,-112 L-80,-84 L-44,-58 L-56,-30 L-22,-6"
    rama = "M-80,-84 L-112,-70 L-122,-40"
    grieta2 = "M130,125 L104,92 L118,70 L92,58"
    return f'''<ellipse cx="220" cy="414" rx="140" ry="14" fill="{OUT}" opacity="0.45"/>
<g transform="translate(220,212) rotate(-8)" stroke="{OUT}" stroke-width="9.8" stroke-linejoin="round" stroke-linecap="round">
    <path d="{hexa}" fill="{cuerpo}"/>
    <path d="M0.0,-105.0 L92.0,58.0 L-92.0,58.0 Z" fill="{cara}"/>
    <path d="M0,-200 L0,-105 M0,-105 L173,-100 M0,-105 L-173,-100 M92,58 L173,-100 M92,58 L173,100 M92,58 L0,200 M-92,58 L-173,-100 M-92,58 L-173,100 M-92,58 L0,200" fill="none"/>
    <path d="{grieta}" fill="none" stroke-width="7"/><path d="{rama}" fill="none" stroke-width="5"/><path d="{grieta2}" fill="none" stroke-width="6"/>
    <path d="M-150,-122 L-128,-100 L-158,-92 Z" fill="{OUT}" stroke-width="4"/>
    <g stroke="none">{num}</g>
  </g>'''


def build_elementos():
    el("d20-agrietado", "d20 agrietado", d20_agrietado())
    el("d20-agrietado-musgo", "d20 agrietado (musgo)", d20_agrietado(MUSGO, "#A9C6B2"))
    el("d20-pifia", "d20 en pifia (sangre, número 1)", d20_agrietado(SANGRE, "#C2606C", "1"))

    # Luna creciente con cráteres y destellos
    lp = crescent(220, 220, 150, 290, 180, 128)
    crat = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{LUNA_S}" stroke="{OUT}" stroke-width="5"/>'
                   for x, y, r in ((128, 230, 18), (160, 318, 13), (110, 168, 9), (208, 352, 9)))
    el("luna", "Luna creciente", f'''<circle cx="220" cy="220" r="196" fill="{VELA}" opacity="0.10"/>
<path d="{lp}" fill="{LUNA}" stroke="{OUT}" stroke-width="10" stroke-linejoin="round"/>
{crat}
{sparkle(330, 300, 70, VELA)}{sparkle(380, 200, 36, PERG)}{sparkle(300, 380, 28, VELA)}''')

    # Luna llena con niebla delante (para hombre lobo)
    el("luna-llena", "Luna llena entre la niebla", f'''<circle cx="220" cy="200" r="150" fill="{PERG}" stroke="{OUT}" stroke-width="10"/>
<circle cx="168" cy="160" r="26" fill="{PERG_V}"/><circle cx="262" cy="232" r="38" fill="{PERG_V}"/><circle cx="196" cy="270" r="16" fill="{PERG_V}"/><circle cx="270" cy="134" r="12" fill="{PERG_V}"/>
<path d="M30 300 C80 270 120 270 170 300 S260 330 310 300 S390 270 420 292 L420 440 L30 440 Z" fill="{LUNA}" opacity="0.92" stroke="{OUT}" stroke-width="8" stroke-linejoin="round"/>
<path d="M10 360 C60 330 110 330 160 360 S250 390 300 360 S380 330 430 352 L430 440 L10 440 Z" fill="{CENIZA}" stroke="{OUT}" stroke-width="8" stroke-linejoin="round"/>''')

    # Niebla: bandas onduladas
    def onda(y, amp, x0=-20, x1=460, paso=110):
        d = f"M{x0} {y}"
        x = x0
        s = 1
        while x < x1:
            d += f" q{paso / 2} {-amp * s} {paso} 0"
            x += paso
            s = -s
        return d
    el("niebla", "Niebla", f'''<g fill="none" stroke-linecap="round">
  <path d="{onda(110, 26)}" stroke="{LUNA}" stroke-width="22" opacity="0.35"/>
  <path d="{onda(180, 30, -60, 460, 130)}" stroke="{LUNA}" stroke-width="30" opacity="0.55"/>
  <path d="{onda(260, 24, -10, 460, 120)}" stroke="{LUNA}" stroke-width="26" opacity="0.75"/>
  <path d="{onda(330, 28, -70, 460, 140)}" stroke="{PERG}" stroke-width="20" opacity="0.9"/>
</g>''')

    # Humedal: agua, juncos y la luna reflejada (Jaboque, Engativá)
    juncos = ""
    for x, hgt, cab in ((96, 210, True), (130, 260, False), (162, 230, True), (300, 250, True), (336, 200, False), (366, 236, True)):
        juncos += f'<path d="M{x} 330 Q{x - 8} {330 - hgt / 2} {x + 6} {330 - hgt}" fill="none" stroke="{OUT}" stroke-width="14" stroke-linecap="round"/>'
        juncos += f'<path d="M{x} 330 Q{x - 8} {330 - hgt / 2} {x + 6} {330 - hgt}" fill="none" stroke="{MUSGO}" stroke-width="7" stroke-linecap="round"/>'
        if cab:
            juncos += f'<rect x="{x - 9}" y="{330 - hgt * 0.78}" width="20" height="54" rx="10" fill="{AMBAR}" stroke="{OUT}" stroke-width="6" transform="rotate(4 {x} {330 - hgt * 0.7})"/>'
    el("humedal", "Humedal con juncos", f'''<circle cx="236" cy="126" r="54" fill="{PERG}" stroke="{OUT}" stroke-width="8"/>
<path d="M20 330 H420 V420 Q220 440 20 420 Z" fill="{MUSGO_P}" stroke="{OUT}" stroke-width="9" stroke-linejoin="round"/>
<ellipse cx="236" cy="356" rx="46" ry="8" fill="{PERG}" opacity="0.8"/><ellipse cx="236" cy="378" rx="30" ry="5" fill="{PERG}" opacity="0.55"/><ellipse cx="236" cy="396" rx="16" ry="3.5" fill="{PERG}" opacity="0.35"/>
<path d="M60 372 h60 M300 392 h70 M150 404 h40" stroke="{LUNA}" stroke-width="5" stroke-linecap="round" opacity="0.7"/>
{juncos}''')

    # Medallón muisca de Chía (diosa de la luna)
    dientes = []
    for i in range(24):
        a = 2 * math.pi * i / 24 - math.pi / 2
        a1, a2 = a - math.pi / 24, a + math.pi / 24
        p = lambda ang, rad: f"{220 + rad * math.cos(ang):.1f},{220 + rad * math.sin(ang):.1f}"
        dientes.append(f"M{p(a1, 150)} L{p(a, 196)} L{p(a2, 150)}Z")
    escalones = []
    for i in range(12):
        a = 2 * math.pi * i / 12
        x, y = 220 + 122 * math.cos(a), 220 + 122 * math.sin(a)
        escalones.append(f'<rect x="{x - 11:.1f}" y="{y - 11:.1f}" width="22" height="22" fill="{SANGRE}" stroke="{OUT}" stroke-width="5" transform="rotate({math.degrees(a) + 45:.1f} {x:.1f} {y:.1f})"/>')
    cp = crescent(220, 220, 62, 248, 202, 52)
    el("chia", "Medallón de Chía (luna muisca)", f'''<path d="{" ".join(dientes)}" fill="{VELA}" stroke="{OUT}" stroke-width="7" stroke-linejoin="round"/>
<circle cx="220" cy="220" r="150" fill="{NIEBLA}" stroke="{OUT}" stroke-width="10"/>
<circle cx="220" cy="220" r="140" fill="none" stroke="{VELA}" stroke-width="4" stroke-dasharray="2 14" stroke-linecap="round"/>
{"".join(escalones)}
<circle cx="220" cy="220" r="96" fill="{ABISMO}" stroke="{OUT}" stroke-width="8"/>
<circle cx="220" cy="220" r="96" fill="none" stroke="{VELA}" stroke-width="3"/>
<path d="{cp}" fill="{PERG}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>''')

    # Greca muisca (banda repetible): rombos escalonados con espiral cuadrada
    tile = ""
    for i in range(11):
        x = 40 + i * 80
        tile += (f'<path d="M{x} 15 l10 10 h10 v10 l10 10 -10 10 v10 h-10 l-10 10 -10 -10 h-10 v-10 l-10 -10 10 -10 v-10 h10 Z" '
                 f'fill="{VELA}" stroke="{OUT}" stroke-width="5" stroke-linejoin="round"/>'
                 f'<path d="M{x - 8} {55 + 8} v-16 h16 v12 h-8 v-4" fill="none" stroke="{OUT}" stroke-width="4.5" stroke-linecap="square"/>')
        if i < 10:
            tile += f'<path d="M{x + 40} 30 l10 25 -10 25 -10 -25 Z" fill="{SANGRE}" stroke="{OUT}" stroke-width="4.5" stroke-linejoin="round"/>'
    el("greca-muisca", "Greca muisca", f'''<rect x="0" y="0" width="880" height="110" fill="{ABISMO}"/>
<rect x="0" y="4" width="880" height="6" fill="{VELA}"/><rect x="0" y="100" width="880" height="6" fill="{VELA}"/>
{tile}''', vb="0 0 880 110", w=880, h=110)

    # Zarpazo (Hombre Lobo): tres garras que suben de izquierda a derecha sobre luna
    garras = ""
    for k in range(3):
        dx = k * 62
        garras += (f'<path d="M{70 + dx} {372 - k * 6} C{120 + dx} {300 - k * 6} {180 + dx} {190 - k * 6} {250 + dx} {64 - k * 6} '
                   f'C{214 + dx} {200 - k * 6} {160 + dx} {300 - k * 6} {98 + dx} {388 - k * 6} Z" fill="{SANGRE}" stroke="{OUT}" stroke-width="9" stroke-linejoin="round"/>')
    el("zarpazo", "Zarpazo", f'''<circle cx="246" cy="196" r="150" fill="{PERG}" stroke="{OUT}" stroke-width="10"/>
<circle cx="300" cy="140" r="24" fill="{PERG_V}"/><circle cx="196" cy="268" r="34" fill="{PERG_V}"/>
{garras}''')

    # Espiral (Mago): doble trazo, contorno + oro
    sp = spiral_points(220, 214, 6, 30, 4.6)
    el("espiral", "Espiral", f'''<circle cx="220" cy="214" r="190" fill="{MUSGO_P}" stroke="{OUT}" stroke-width="10"/>
<polyline points="{sp}" fill="none" stroke="{OUT}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>
<polyline points="{sp}" fill="none" stroke="{VELA}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>
{sparkle(370, 70, 46, PERG)}''')

    # Anillo de hongos (Changeling)
    hongos = ""
    for i, (x, y, s) in enumerate(((110, 300, 1.0), (180, 250, .8), (268, 248, .9), (340, 296, 1.05), (226, 330, 1.2))):
        hongos += (f'<g transform="translate({x},{y}) scale({s})">'
                   f'<path d="M-14 0 Q-16 44 -10 58 H10 Q16 44 14 0 Z" fill="{PERG}" stroke="{OUT}" stroke-width="7" stroke-linejoin="round"/>'
                   f'<path d="M-52 4 Q-50 -54 0 -56 Q50 -54 52 4 Z" fill="{SANGRE}" stroke="{OUT}" stroke-width="8" stroke-linejoin="round"/>'
                   f'<circle cx="-22" cy="-22" r="7" fill="{PERG}"/><circle cx="10" cy="-36" r="6" fill="{PERG}"/><circle cx="26" cy="-12" r="5" fill="{PERG}"/></g>')
    el("anillo-hongos", "Anillo de hongos", f'''<ellipse cx="226" cy="330" rx="190" ry="62" fill="none" stroke="{MUSGO}" stroke-width="6" stroke-dasharray="3 18" stroke-linecap="round"/>
{hongos}{sparkle(80, 120, 50, VELA)}{sparkle(360, 90, 36, LUNA)}{sparkle(250, 120, 22, VELA)}''')

    # Vela
    el("vela", "Vela", f'''<circle cx="220" cy="128" r="110" fill="{VELA}" opacity="0.16"/><circle cx="220" cy="128" r="64" fill="{VELA}" opacity="0.18"/>
<path d="M220 40 C262 96 270 132 220 176 C170 132 178 96 220 40 Z" fill="{VELA}" stroke="{OUT}" stroke-width="9" stroke-linejoin="round"/>
<path d="M220 104 C236 128 236 146 220 162 C204 146 204 128 220 104 Z" fill="{CORAL_C}"/>
<path d="M220 176 V198" stroke="{OUT}" stroke-width="7" stroke-linecap="round"/>
<path d="M168 198 H272 V372 H168 Z" fill="{PERG}" stroke="{OUT}" stroke-width="9" stroke-linejoin="round"/>
<path d="M168 198 H272 V214 Q262 214 260 236 Q258 250 250 236 Q246 214 232 214 H212 Q200 214 198 252 Q196 270 188 252 Q184 214 168 214 Z" fill="{PERG_V}" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/>
<path d="M104 372 H336 Q336 404 300 404 H140 Q104 404 104 372 Z" fill="{NIEBLA}" stroke="{OUT}" stroke-width="9" stroke-linejoin="round"/>''')

    # Destello en oro de vela
    el("destello", "Destello", f'''{sparkle(200, 220, 300, VELA, OUT, 3.2)}{sparkle(350, 110, 90, PERG, OUT, 9)}{sparkle(352, 340, 60, CORAL_C, OUT, 12)}''')

    # La mascota original entre la niebla, con luna detrás
    lp = crescent(330, 96, 62, 352, 78, 52)
    el("tazon-en-la-niebla", "Tazón en la niebla", f'''<path d="{lp}" fill="{LUNA}" stroke="{OUT}" stroke-width="8" stroke-linejoin="round"/>
<g transform="translate(90,70) scale(2.15)">{bowl(PERG, NOCHE)}</g>
<path d="M0 330 C60 300 110 300 170 330 S280 360 340 330 S420 306 440 318 V440 H0 Z" fill="{LUNA}" opacity="0.85"/>
<path d="M0 380 C70 350 130 350 190 380 S300 404 360 380 S420 360 440 368 V440 H0 Z" fill="{CENIZA}" opacity="0.9"/>''')

    # Esquina (triángulo sangre + vela) y divisor diagonal, como piezas sueltas
    el("esquina", "Triángulo de esquina", f'<path d="M0 0H440V440Z" fill="{SANGRE}"/><path d="M200 0H440V240Z" fill="{VELA}"/>')
    el("divisor", "Divisor diagonal", f'''<path d="M0 82 L880 30 L880 52 L0 104Z" fill="{MUSGO}"/><path d="M0 62 L880 10 L880 28 L0 80Z" fill="{VELA}"/>
<path d="M0 88 L880 36" stroke="{OUT}" stroke-width="5" fill="none"/>{sparkle(440, 54, 46, VELA)}''', vb="0 0 880 110", w=880, h=110)


# ------------------------------------------------------------------ íconos
def _spiral_icon():
    return spiral_points(32, 32, 1.5, 7.2, 3.1, n=90)


ICONOS = {
    "luna": ("Luna", f'<path d="{crescent(32, 32, 24, 42, 24, 20)}"/>'),
    "luna-llena": ("Luna llena", '<circle cx="32" cy="28" r="18"/><circle cx="26" cy="24" r="3"/><circle cx="37" cy="33" r="4"/><path d="M8 54c6-4 11-4 16 0s11 4 16 0 11-4 16 0"/>'),
    "niebla": ("Niebla", '<path d="M8 20c6-4 10-4 16 0s10 4 16 0 10-4 16 0M8 32c6-4 10-4 16 0s10 4 16 0 10-4 16 0M14 44c6-4 10-4 16 0s10 4 16 0"/>'),
    "vela": ("Vela", '<path d="M32 6c6 7 7 12 0 18-7-6-6-11 0-18Z"/><path d="M32 24v4M22 28h20v24H22ZM14 56h36"/><path d="M36 28v7"/>'),
    "humedal": ("Humedal", '<path d="M6 52c5-3 9-3 14 0s9 3 14 0 9-3 14 0 9 3 14 0"/><path d="M22 46 21 22M32 46V12M43 46l1-20"/><rect x="29" y="12" width="6" height="12" rx="3"/><rect x="18" y="20" width="6" height="11" rx="3"/>'),
    "espiral": ("Espiral (Mago)", f'<polyline points="{_spiral_icon()}"/>'),
    "zarpazo": ("Zarpazo (Hombre Lobo)", '<path d="M10 52C20 42 26 28 30 10M22 56C32 46 38 32 42 14M34 58C44 48 50 34 54 18"/>'),
    "huella": ("Huella de lobo", '<path d="M32 34c8 0 14 7 14 14 0 5-4 8-8 7-3-1-4-2-6-2s-3 1-6 2c-4 1-8-2-8-7 0-7 6-14 14-14Z"/><ellipse cx="16" cy="28" rx="4" ry="6"/><ellipse cx="25" cy="17" rx="4" ry="6"/><ellipse cx="39" cy="17" rx="4" ry="6"/><ellipse cx="48" cy="28" rx="4" ry="6"/>'),
    "hongo": ("Hongo (Changeling)", '<path d="M10 32a22 20 0 0 1 44 0Z"/><path d="M26 32v16a6 6 0 0 0 12 0V32"/><circle cx="24" cy="23" r="2"/><circle cx="38" cy="20" r="2"/>'),
    "d20-agrietado": ("d20 agrietado", '<path d="M32 4 56 18v28L32 60 8 46V18Z"/><path d="M32 18 46 42H18Z"/><path d="M32 4v14M32 18H8M32 18h24M18 42 8 18M18 42 8 46M18 42l14 18M46 42l10-24M46 42l10 4M46 42 32 60"/><path d="m20 11 4 6-3 4 4 4" stroke-width="3"/>'),
    "greca": ("Greca muisca", '<path d="M32 6l6 6h6v6l6 6v16l-6 6v6h-6l-6 6-6-6h-6v-6l-6-6V24l6-6v-6h6Z"/><path d="M28 36v-8h8v6h-4"/>'),
    "chia": ("Chía (luna muisca)", f'<circle cx="32" cy="32" r="16"/><path d="{crescent(32, 32, 9, 36, 29, 7.5)}"/><path d="M32 4v6M32 54v6M4 32h6M54 32h6M12 12l4 4M48 48l4 4M52 12l-4 4M16 48l-4 4"/>'),
    "farol": ("Farol", '<path d="M24 14h16l4 8v24l-4 6H24l-4-6V22Z"/><path d="M32 6v8M20 22h24M26 56h12"/><path d="M32 28c3 4 3 7 0 10-3-3-3-6 0-10Z"/>'),
}


def build_iconos():
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" style="color:{c}"><title>{t}</title>{b}</svg>\n'
    sym = '  <symbol id="i-{n}" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><title>{t}</title>{b}</symbol>'
    simbolos = []
    for n, (t, b) in ICONOS.items():
        write(f"assets/iconos/{n}.svg", head.format(c=PERG, t=t, b=b))
        simbolos.append(sym.format(n=n, t=t, b=b))
    # los 21 originales también entran al sprite (son currentColor, toman el color del texto)
    for f in sorted((ORIGEN / "iconos").glob("*.svg")):
        s = f.read_text(encoding="utf-8")
        t = re.search(r"<title>(.*?)</title>", s).group(1)
        b = re.search(r"</title>(.*)</svg>", s, re.S).group(1)
        if f.stem not in ICONOS:
            simbolos.append(sym.format(n=f.stem, t=t, b=b))
    write("assets/iconos/sprite.svg", '<svg xmlns="http://www.w3.org/2000/svg" style="display:none">\n' + "\n".join(simbolos) + "\n</svg>\n")
    return list(ICONOS), sorted(f.stem for f in (ORIGEN / "iconos").glob("*.svg"))


# ------------------------------------------------------------------ tokens
def build_tokens():
    css = ["/* Tazón para Dos · Tinieblas · tokens (generado por tools/build.py) */", ":root {"]
    for k, (hx, nombre, grupo, _) in PALETA.items():
        css.append(f"  --{k.replace('_', '-')}: {hx};  /* {nombre} */")
    css += [
        "  /* compatibilidad con los nombres del kit original: los acentos pasan a su versión nocturna */",
        f"  --ink: {ABISMO};", f"  --paper: {NOCHE};", f"  --cream: {PERG};",
        f"  --teal: {MUSGO};", f"  --coral: {SANGRE};", f"  --sun: {VELA};", f"  --muted: {CENIZA};",
        "  /* roles */",
        "  --fondo: var(--noche);", "  --fondo-hondo: var(--abismo);", "  --superficie: var(--niebla);",
        "  --texto: var(--pergamino);", "  --texto-suave: var(--luna);", "  --texto-tenue: var(--ceniza);",
        f"  --borde: {CENIZA};", f"  --contorno: {OUT};",
        "  --radius-sm: 10px;", "  --radius-md: 16px;", "  --radius-lg: 22px;", "  --radius-xl: 28px;", "  --radius-pill: 999px;",
        f"  --sombra-dura: 8px 8px 0 {OUT};",
        f"  --sombra-sangre: 8px 8px 0 {SANGRE};",
        f"  --sombra-vela: 6px 6px 0 {VELA};",
        f"  --sombra-tarjeta: 0 8px 0 {OUT};",
        "  --font-web-display: 'Space Grotesk', sans-serif;", "  --font-web-text: 'DM Sans', sans-serif;", "  --font-mono: 'DM Mono', monospace;",
        "  --font-display: 'Space Grotesk', sans-serif;  /* el logotipo conserva Barlow Condensed en contornos */",
        "  --dots: radial-gradient(rgba(207, 202, 223, 0.08) 1.6px, transparent 1.7px) 0 0 / 22px 22px;",
        "  --dots-pergamino: radial-gradient(rgba(40, 32, 59, 0.10) 1.6px, transparent 1.7px) 0 0 / 22px 22px;",
        f"  --diagonal: linear-gradient(-3.5deg, transparent 46%, {VELA} 46% 52%, transparent 52%);",
        "}",
    ]
    write("brand/tokens.css", "\n".join(css) + "\n")
    tokens = {"$description": "Tokens de Tazón para Dos · Tinieblas. Fuente: tools/build.py.",
              "color": {k: {"value": v[0], "name": v[1], "group": v[2], "use": v[3]} for k, v in PALETA.items()},
              "outline": OUT,
              "derivation": {"teal→musgo": [ORIGINAL["teal"], MUSGO], "coral→sangre": [ORIGINAL["coral"], SANGRE],
                             "sun→vela": [ORIGINAL["sun"], VELA], "cream→pergamino": [ORIGINAL["cream"], PERG],
                             "ink→abismo/noche": [ORIGINAL["ink"], ABISMO, NOCHE]},
              "font": {"display": "Space Grotesk", "text": "DM Sans", "mono": "DM Mono", "logo": "Barlow Condensed ExtraBold (contornos)"},
              "shadow": {"dura": f"8px 8px 0 {OUT}", "sangre": f"8px 8px 0 {SANGRE}", "vela": f"6px 6px 0 {VELA}"},
              "pattern": {"dots": {"size": "22px", "dot": "1.6px", "color": "luna 8 % (oscuro) / tinta 10 % (pergamino)"}},
              "radius": {"sm": 10, "md": 16, "lg": 22, "xl": 28, "pill": 999}}
    write("brand/tokens.json", json.dumps(tokens, ensure_ascii=False, indent=2) + "\n")
    return tokens


def build_brand(iconos_nuevos, iconos_orig):
    brand = {
        "$description": "Perfil de la sub-marca oscura. Úsalo junto a tokens.json. Hereda todo lo que no se dice aquí del kit original (https://thetrashkat.github.io/tazon-para-dos-marca/).",
        "version": "1.0.0", "updated": "2026-10-13",
        "identity": {
            "name": "Tazón para Dos · Tinieblas", "parent": "Tazón para Dos",
            "parent_kit": "https://thetrashkat.github.io/tazon-para-dos-marca/",
            "descriptor": "Historias del Mundo de Tinieblas y leyendas de Engativá",
            "tagline": "Jugar también es escuchar lo que cuenta la niebla.",
            "secondary_taglines": ["La mesa también se juega de noche.", "Del humedal al aire.", "Toda leyenda empieza en voz baja."],
            "scope": ["Mago: La Ascensión", "Hombre Lobo: El Apocalipsis", "Changeling: El Ensueño",
                      "Leyendas urbanas de Bogotá y Engativá (humedal Jaboque, el río, el barrio)"],
            "why_name": "«Tinieblas» nombra a la vez el Mundo de Tinieblas y la hora en que se cuentan las leyendas. Va siempre después del nombre madre, nunca solo.",
        },
        "palette": {k: {"hex": v[0], "name": v[1], "group": v[2], "use": v[3]} for k, v in PALETA.items()},
        "outline": OUT,
        "contrast_wcag": tabla_contraste(),
        "typography": {"display": "Space Grotesk 700", "text": "DM Sans 400/700", "mono": "DM Mono 500, mayúsculas, espaciado 0,12–0,14 em",
                       "logo": "Barlow Condensed ExtraBold en contornos (no cambia)"},
        "system": {
            "shadows": "Sombra dura desplazada sin desenfoque. Sobre noche: sangre seca o contorno abismo; sobre pergamino: tinta al 18 %.",
            "dots": "Trama de puntos de 22 px: luna al 8 % sobre oscuro, tinta al 10 % sobre pergamino.",
            "diagonals": "Bloques separados por diagonales que suben de izquierda a derecha (3–5°) con franja de oro de vela.",
            "corner": "Triángulo sangre seca con otro de oro de vela, arriba a la derecha.",
            "motifs": ["luna creciente y llena", "niebla en bandas", "humedal con juncos", "greca muisca (rombo escalonado)",
                       "medallón de Chía", "d20 agrietado", "zarpazo", "espiral", "anillo de hongos", "vela", "destello en oro"],
        },
        "logos": sorted(p.name for p in (ROOT / "assets" / "logo").glob("*.svg")),
        "elements": sorted(p.name for p in (ROOT / "assets" / "elementos").glob("*.svg")),
        "icons": {"new": iconos_nuevos, "inherited": iconos_orig, "sprite": "assets/iconos/sprite.svg"},
        "rules": {
            "do": ["Partir siempre del logo original recoloreado; «Tinieblas» va en la fila del descriptor.",
                   "Texto largo en pergamino sobre noche o en tinta sobre pergamino.",
                   "Oro de vela para lo que debe brillar: franjas, destellos, botones, números.",
                   "Ilustraciones planas con contorno oscuro y pocos objetos (3–5).",
                   "Motivos muiscas como geometría (rombos, escalones, espirales) y con respeto: sin inventar significados sagrados."],
            "dont": ["Rostros de personas reales sin consentimiento.",
                     "Sangre realista, gore o calaveras: el miedo se sugiere con niebla, luna y silencio.",
                     "Oro de vela o sangre seca como texto sobre pergamino o noche (no pasa AA); usa ámbar o coral ceniza.",
                     "Degradados, brillos difusos o sombras con desenfoque.",
                     "Redibujar el tazón o usar «Tinieblas» sin el nombre madre.",
                     "Fuentes góticas o de imitación medieval: la tipografía es la de siempre."],
        },
        "story_tool_theme": {"tool": "D:\\herramientas\\pdf-historias\\maquetar.py",
                             "files": ["tema-tinieblas.css", "tema-tinieblas-pergamino.css"],
                             "proposed_option": "--tema RUTA.css (se añade como <style> después del CSS base y al final de estilo.css en --web)"},
    }
    write("brand/brand.json", json.dumps(brand, ensure_ascii=False, indent=2) + "\n")


# ------------------------------------------------------------------ tema para pdf-historias
def bloque_diagonal(sup, inf, alto=297, corte=0.70, pendiente=4.0):
    w, h = 210, alto
    y = h * corte
    d = w * math.tan(math.radians(pendiente))
    return svg_uri(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="none">
<rect width="{w}" height="{h}" fill="{sup}"/>
<path d="M0 {y:.1f} L{w} {y - d:.1f} L{w} {h} L0 {h}Z" fill="{VELA}"/>
<path d="M0 {y + 5:.1f} L{w} {y - d + 5:.1f} L{w} {h} L0 {h}Z" fill="{inf}"/>
<path d="M0 {y:.1f} L{w} {y - d:.1f} M0 {y + 5:.1f} L{w} {y - d + 5:.1f}" stroke="{OUT}" stroke-width="1.1" fill="none"/></svg>""")


def divisores_css(modo):
    """Variantes de divisor (::: divisor cinta, luna…) en colores Tinieblas. Las genera
    D:/tazon-para-dos-marca/tools/divisores.py en assets/divisores/."""
    f = ROOT / "assets" / "divisores" / f"divisores-{modo}.css"
    return "\n" + f.read_text(encoding="utf-8") if f.exists() else ""


def theme_css(modo):
    oscuro = modo == "noche"
    V = dict(
        PAGE=NOCHE if oscuro else PERG, TEXT=PERG if oscuro else TINTA, MUTED=CENIZA if oscuro else TINTA_S,
        SURF=NIEBLA if oscuro else PERG_V, BORDER=CENIZA if oscuro else TINTA, LINE=LUNA if oscuro else TINTA,
        DOTS=("radial-gradient(rgba(207,202,223,.08) 1.6px, transparent 1.7px) 0 0 / 22px 22px" if oscuro
              else "radial-gradient(rgba(40,32,59,.10) 1.6px, transparent 1.7px) 0 0 / 22px 22px"),
        RULE="rgba(207,202,223,.28)" if oscuro else "rgba(40,32,59,.35)",
        SHADOW=f"1.6mm 1.6mm 0 {SANGRE}" if oscuro else "1.6mm 1.6mm 0 rgba(40,32,59,.22)",
        H1SH=SANGRE if oscuro else MUSGO, CAP=VELA if oscuro else SANGRE, CAPSH=SANGRE if oscuro else TINTA,
        H2LINE=VELA if oscuro else SANGRE, LINK=MUSGO if oscuro else MUSGO_P, MARK=CORAL_C if oscuro else SANGRE,
        EPI=CORAL_C if oscuro else SANGRE, ACC_TXT=VELA if oscuro else AMBAR,
    )
    DOTS_L = "radial-gradient(rgba(207,202,223,.08) 1.6px, transparent 1.7px) 0 0 / 22px 22px"
    tri = svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0 0H100V100Z" fill="{SANGRE}"/><path d="M46 0H100V54Z" fill="{VELA}"/></svg>')
    hexa = svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M50 6 88 28V72L50 94 12 72V28Z" fill="{VELA}" stroke="{OUT}" stroke-width="7" stroke-linejoin="round"/><path d="M30 26 L38 40 L33 48" fill="none" stroke="{OUT}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    dest = svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-50 -50 100 100"><path d="M0,-50 C6,-10 10,-6 50,0 C10,6 6,10 0,50 C-6,10 -10,6 -50,0 C-10,-6 -6,-10 0,-50 Z" fill="{VELA}"/></svg>')
    div = svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 24" preserveAspectRatio="none"><path d="M0 20 L400 8 L400 13 L0 25Z" fill="{MUSGO if oscuro else MUSGO_P}"/><path d="M0 15 L400 3 L400 7 L0 19Z" fill="{VELA}"/><path d="M0 21.5 L400 9.5" stroke="{OUT}" stroke-width="1.6" fill="none"/></svg>')
    corte = svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 40" preserveAspectRatio="none"><path d="M0 26 L400 6 L400 13 L0 33Z" fill="{VELA}"/><path d="M0 33 L400 13 L400 40 L0 40Z" fill="{V["PAGE"]}"/><path d="M0 26 L400 6" stroke="{OUT}" stroke-width="2.4" fill="none"/><path d="M0 33 L400 13" stroke="{OUT}" stroke-width="2.4" fill="none"/></svg>')
    lee = lambda r: (ROOT / r).read_text(encoding="utf-8")
    sello = svg_uri(lee("assets/logo/sello-tinieblas.svg"))
    d20 = svg_uri(lee("assets/elementos/d20-agrietado.svg"))
    logo_inv = svg_uri(lee("assets/logo/logotipo-horizontal-tinieblas.svg"))

    # portada: el color elegido en el front matter se traduce a su versión nocturna
    portadas = []
    mapa = [("55C4BF", MUSGO_P, ABISMO, PERG, OUT), ("EA6077", SANGRE, ABISMO, PERG, OUT), ("F8CB67", VELA, ABISMO, ABISMO, SANGRE),
            ("28203B", ABISMO, SANGRE, PERG, SANGRE), ("F7F2E8", PERG_V, NOCHE, TINTA, PERG)]
    for orig, sup, inf, titulo, sombra in mapa:
        sel = f'section.portada[style*="height=\'297\' fill=\'%23{orig}\'"]'
        portadas.append(f'{sel}{{background-image:url("{bloque_diagonal(sup, inf)}")!important}}')
        portadas.append(f'{sel} .titulo-portada{{color:{titulo};text-shadow:calc(2.2*var(--mm)) calc(2.2*var(--mm)) 0 {sombra}}}')
        txt_marca = TINTA if sup in (VELA, PERG_V) else PERG
        portadas.append(f'{sel} .marca{{color:{txt_marca}}}')

    css = f"""/* ============================================================================
   Tazón para Dos · Tinieblas — tema «{modo}» para pdf-historias
   Generado por D:\\tazon-para-dos-tinieblas\\tools\\build.py. No lo edites a mano.
   Se aplica DESPUÉS del CSS base de maquetar.py (mismo documento), por eso basta con
   la misma especificidad; solo la portada (estilo en línea) necesita !important.
   ============================================================================ */
:root{{--ink:{OUT};--teal:{MUSGO};--coral:{SANGRE};--sun:{VELA};--cream:{PERG};--paper:{V['PAGE']};--muted:{V['MUTED']};
  --abismo:{ABISMO};--noche:{NOCHE};--niebla:{NIEBLA};--pergamino:{PERG};--vela:{VELA};--sangre:{SANGRE};--musgo:{MUSGO};
  --sombra:{V['SHADOW']};--sombra-dura:1.4mm 1.4mm 0 {OUT}}}

/* --- página, cabecera y pie ---------------------------------------------------- */
@page{{background:{V['PAGE']};
  @top-left{{color:{V['TEXT']};border-bottom-color:{V['LINE']}}}
  @top-center{{border-bottom-color:{V['LINE']}}}
  @top-right{{color:{V['MUTED']};border-bottom-color:{V['LINE']}}}
  @top-right-corner{{background-image:url("{tri}")}}
  @bottom-center{{color:{V['MUTED']}}}
}}
@page :right{{
  @bottom-right{{color:{OUT};background-image:url("{hexa}")}}
  @bottom-left{{background-image:url("{dest}")}}
}}
@page :left{{
  @bottom-left{{color:{OUT};background-image:url("{hexa}")}}
  @bottom-right{{background-image:url("{dest}")}}
}}
html,body{{background:{V['PAGE']};color:{V['TEXT']}}}
a{{color:{V['TEXT']};text-decoration-color:{V['LINK']}}}
ul li::marker{{color:{V['MARK']}}}
.cols-2,.cols-3{{column-rule-color:{V['RULE']}}}

/* --- títulos -------------------------------------------------------------------- */
header.capitulo .kicker{{background:{VELA};color:{ABISMO}}}
h1{{color:{V['TEXT']};text-shadow:.9mm .9mm 0 {V['H1SH']}}}
h2{{background-image:linear-gradient({V['H2LINE']},{V['H2LINE']})}}
h3{{color:{V['ACC_TXT']}}}
p.capitular::first-letter{{color:{V['CAP']};text-shadow:.8mm .8mm 0 {V['CAPSH']}}}

/* --- ornamentos ------------------------------------------------------------------- */
.divisor{{background-image:url("{div}")}}
.divisor::after{{background-image:url("{dest}")}}

/* --- figuras -------------------------------------------------------------------------- */
figure img{{border-color:{V['BORDER']};background:{V['SURF']}}}
figcaption{{color:{V['MUTED']};background-image:url("{dest}")}}

/* --- recuadros, epígrafes y citas ------------------------------------------------------ */
aside.recuadro{{background-color:{V['SURF']};background-image:{V['DOTS']};border-color:{V['BORDER']};color:{V['TEXT']}}}
aside.recuadro .etiqueta{{background:{MUSGO};color:{ABISMO};border-color:{OUT};box-shadow:.8mm .8mm 0 {OUT}}}
aside.c-coral .etiqueta{{background:{SANGRE};color:{PERG}}}
aside.c-sol .etiqueta{{background:{VELA};color:{ABISMO}}}
aside.c-tinta{{background-color:{ABISMO};background-image:{DOTS_L};color:{PERG};border-color:{CENIZA if oscuro else OUT}}}
aside.c-tinta .etiqueta{{background:{VELA};color:{ABISMO};border-color:{VELA}}}
.epigrafe::before{{color:{V['EPI']}}}
.epigrafe .autor{{color:{V['MUTED']}}}
blockquote{{border-left-color:{VELA}}}
blockquote.destacada{{background-image:url("{div}"),url("{div}")}}

/* --- leyendas: popular frente a Mundo de Tinieblas ------------------------------------- */
aside.leyenda{{border-color:{V['BORDER']};background:{V['SURF']}}}
aside.leyenda .cabeza{{border-bottom-color:{V['BORDER']};background-color:{VELA};background-image:radial-gradient(rgba(17,13,24,.12) 1.6px, transparent 1.7px);background-size:22px 22px;color:{ABISMO}}}
aside.leyenda.c-turquesa .cabeza{{background-color:{MUSGO}}}
aside.leyenda.c-coral .cabeza{{background-color:{SANGRE};color:{PERG}}}
aside.leyenda .cabeza .etiqueta{{background:{ABISMO};color:{VELA}}}
aside.leyenda .panel.popular{{background-color:{V['SURF']};background-image:{V['DOTS']};color:{V['TEXT']}}}
aside.leyenda .panel.tinieblas{{background-color:{ABISMO};background-image:{DOTS_L};color:{PERG}}}
aside.leyenda .rotulo{{color:{V['EPI'] if oscuro else SANGRE}}}
aside.leyenda .tinieblas .rotulo,aside.leyenda .tinieblas strong{{color:{VELA}}}

/* --- páginas especiales ------------------------------------------------------------------ */
.triangulo{{background-image:url("{tri}")}}
section.sangre{{background-color:{ABISMO}}}
section.sangre .portadilla .kicker{{background:{ABISMO};color:{VELA};border-color:{VELA}}}
section.sangre .portadilla h1{{color:{PERG};text-shadow:calc(2*var(--mm)) calc(2*var(--mm)) 0 {SANGRE}}}
section.sangre figcaption{{background-color:{NOCHE};color:{PERG};border-color:{CENIZA};background-image:url("{dest}")}}
section.apertura .banner{{background:{ABISMO}}}
section.apertura .corte{{background-image:url("{corte}")}}
section.apertura .pie-banner{{background:{NOCHE};color:{PERG};border-color:{CENIZA}}}

/* portada */
section.portada{{color:{PERG};background-color:{NOCHE}}}
section.portada{{background-image:url("{bloque_diagonal(NOCHE, ABISMO)}")!important}}
{chr(10).join(portadas)}
section.portada .puntos{{background:{DOTS_L}}}
section.portada .marca img{{content:url("{sello}")}}
.etiqueta-portada{{background:{ABISMO};color:{VELA};border:calc(.4*var(--mm)) solid {VELA}}}
.titulo-portada{{color:{PERG};text-shadow:calc(2.2*var(--mm)) calc(2.2*var(--mm)) 0 {OUT}}}
.subtitulo-portada{{background:{NOCHE};color:{PERG};border-color:{CENIZA};box-shadow:calc(1.4*var(--mm)) calc(1.4*var(--mm)) 0 {SANGRE}}}
section.portada .creditos{{color:{PERG}}}
section.portada .creditos span{{background:{NOCHE};border-color:{CENIZA}}}

/* contraportada */
section.contraportada{{background:{ABISMO};background-image:{DOTS_L};color:{PERG}}}
section.contraportada .d20{{content:url("{d20}")}}
section.contraportada .texto p:first-child{{color:{VELA}}}
section.contraportada .creditos-final{{color:{LUNA}}}
section.contraportada .cierre{{border-top-color:{CENIZA}}}
section.contraportada .cierre img{{content:url("{logo_inv}")}}
section.contraportada .cierre span{{color:{VELA}}}
section.contraportada .cierre span{{font-size:0}}
section.contraportada .cierre span::after{{content:"JUGAR TAMBIÉN ES ESCUCHAR LO QUE CUENTA LA NIEBLA.";font:500 calc(2.4*var(--mm)) 'DM Mono';letter-spacing:.12em;max-width:calc(70*var(--mm));display:inline-block;text-align:right;line-height:1.5}}

/* --- versión web (--web) -------------------------------------------------------------------- */
@media screen{{
  html{{background:{ABISMO};background-image:{DOTS_L}}}
  body.web{{color:{V['TEXT']}}}
  .barra{{background:{ABISMO};color:{PERG};border-bottom-color:{VELA}}}
  .barra a{{color:{PERG}}} .barra span{{color:{VELA}}}
  .barra img{{content:url("{sello}")}}
  .barra .btn{{background:{VELA};color:{ABISMO};border-color:{OUT}}}
  main.libro{{background:{V['PAGE']};border-color:{CENIZA};box-shadow:10px 10px 0 {SANGRE}}}
  section.portada{{border-bottom-color:{OUT}}}
  nav.indice{{background-color:{V['SURF']};background-image:{V['DOTS']};border-color:{V['BORDER']};box-shadow:6px 6px 0 {SANGRE if oscuro else 'rgba(40,32,59,.22)'}}}
  nav.indice .etiqueta{{background:{VELA};color:{ABISMO}}}
  nav.indice a{{color:{V['TEXT']};border-bottom-color:{V['RULE']}}}
  nav.indice a:hover .t{{text-decoration-color:{VELA}}}
  nav.indice .k{{color:{V['MUTED']}}} nav.indice li.parte .k{{color:{V['EPI']}}}
  .volver{{background:{VELA};color:{ABISMO};border-color:{OUT};box-shadow:3px 3px 0 {OUT}}}
}}
"""
    return css


def build_tema():
    write("tema-tinieblas.css", theme_css("noche") + divisores_css("noche"))
    write("tema-tinieblas-pergamino.css", theme_css("pergamino") + divisores_css("pergamino"))


# ------------------------------------------------------------------ tabla de contraste en index.html
def build_index_tabla():
    p = ROOT / "index.html"
    if not p.exists():
        return
    filas = []
    for f in tabla_contraste():
        clase = {"AAA": "ok", "AA": "ok", "AA grande": "medio", "No": "no"}[f["nivel"]]
        filas.append(f'<tr><td><span class="par" style="background:{f["hex_fondo"]};color:{f["hex_texto"]}">Aa</span></td>'
                     f'<td>{PALETA[f["texto"]][1]} <code>{f["hex_texto"]}</code></td><td>{PALETA[f["fondo"]][1]} <code>{f["hex_fondo"]}</code></td>'
                     f'<td class="num">{f["ratio"]:.2f}</td><td><span class="nivel {clase}">{f["nivel"]}</span></td><td>{f["uso"]}</td></tr>')
    tabla = ('<!--contraste--><table class="contraste"><thead><tr><th></th><th>Texto</th><th>Fondo</th><th>Ratio</th><th>WCAG</th><th>Uso</th></tr></thead><tbody>'
             + "".join(filas) + "</tbody></table><!--/contraste-->")
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"<!--contraste-->.*?<!--/contraste-->", lambda m: tabla, s, flags=re.S)
    p.write_text(s, encoding="utf-8")
    print("   index.html (tabla de contraste)")


if __name__ == "__main__":
    print("Tazón para Dos · Tinieblas")
    build_logos()
    build_elementos()
    nuevos, orig = build_iconos()
    build_tokens()
    build_brand(nuevos, orig)
    build_tema()
    build_index_tabla()
