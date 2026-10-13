# Tazón para Dos · Tinieblas

> **Jugar también es escuchar lo que cuenta la niebla.** Sub-marca oscura de [Tazón para Dos](https://thetrashkat.github.io/tazon-para-dos-marca/) para historias del Mundo de Tinieblas (*Mago*, *Hombre Lobo*, *Changeling*) y leyendas urbanas de Bogotá y Engativá.

Página de marca: **https://thetrashkat.github.io/tazon-para-dos-tinieblas/**

Se conserva todo lo esencial del kit original: el tazón, Space Grotesk, DM Sans y DM Mono, la sombra dura, los puntos de 22 px, las diagonales que suben hacia la derecha con su franja y el triángulo de esquina. Lo que cambia es la luz. Los fondos son de noche, los acentos se apagan (musgo de humedal, sangre seca, oro de vela) y aparecen luna, niebla, humedal, geometría muisca y un d20 agrietado.

¿Por qué «Tinieblas»? Porque nombra a la vez el Mundo de Tinieblas y la hora de las leyendas. Va siempre después del nombre madre, nunca solo.

## Paleta

| Rol | Nombre | Hex | Variable | Viene de |
|---|---|---|---|---|
| Fondo | Abismo | `#110D18` | `--abismo` | tinta `#28203B` |
| Fondo | Noche | `#1C1629` | `--noche` | tinta |
| Fondo | Niebla | `#2B2340` | `--niebla` | tinta |
| Fondo / texto | Pergamino | `#E9DDC1` | `--pergamino` | crema `#F7F2E8` |
| Fondo | Pergamino viejo | `#D9C9A3` | `--pergamino-viejo` | crema |
| Acento | Musgo de humedal | `#7FA68C` | `--musgo` | turquesa `#55C4BF` |
| Acento | Musgo profundo | `#3E5E50` | `--musgo-profundo` | turquesa |
| Acento | Sangre seca | `#9E3A48` | `--sangre` | coral `#EA6077` |
| Texto acento | Coral ceniza | `#E07D84` | `--coral-ceniza` | coral |
| Acento | Oro de vela | `#E3B35C` | `--vela` | sol `#F8CB67` |
| Texto acento | Ámbar | `#7E5A1E` | `--ambar` | sol |
| Texto | Luna | `#CFCADF` | `--luna` | — |
| Texto | Ceniza | `#A39AB0` | `--ceniza` | gris cálido |
| Texto | Tinta / tinta suave | `#28203B` / `#5A4E66` | `--tinta` / `--tinta-suave` | tinta |

Contraste WCAG 2.1 (lo calcula `tools/build.py` y la tabla completa está en `brand/brand.json` y en la página):

- Pergamino sobre noche da 13,0:1, sobre abismo 14,2:1 y sobre niebla 11,0:1.
- Luna sobre noche da 11,0:1, y ceniza sobre noche 6,5:1.
- Oro de vela sobre noche da 9,1:1, musgo sobre noche 6,5:1 y coral ceniza sobre noche 6,2:1.
- Abismo sobre vela (botones) da 9,9:1. Pergamino sobre sangre da 4,9:1 y sobre musgo profundo, 5,3:1.
- En impresión, tinta sobre pergamino da 11,5:1, sangre 4,9:1, ámbar 4,6:1 y tinta suave 5,7:1.
- **No pasan:** oro de vela sobre pergamino (1,4:1), sangre como texto sobre noche (2,6:1) y pergamino sobre musgo (2,0:1; solo en un titular grande con sombra, igual que en el kit original).

## Contenido

```
index.html                     página de marca (paleta, contraste, logos, tipografía, sistema, ornamentos, íconos, tema, usos)
brand/tokens.css               variables CSS (+ alias --ink/--teal/--coral/--sun/--cream/--paper con sus versiones nocturnas)
brand/tokens.json              tokens legibles por máquina
brand/brand.json               perfil de la sub-marca: identidad, paleta, contraste, reglas, archivos
assets/logo/                   logotipo horizontal (transparente, con fondo, pergamino), apilado (oscuro, pergamino),
                               sello (oscuro, pergamino), sello de luna, mascota, favicon
assets/elementos/              d20 agrietado (vela, musgo, pifia), luna, luna llena, niebla, humedal, Chía, greca muisca,
                               zarpazo, espiral, anillo de hongos, vela, destello, tazón en la niebla, esquina, divisor
assets/iconos/                 13 íconos nuevos + sprite.svg (nuevos + los 21 del kit original)
tema-tinieblas.css             tema «noche» para pdf-historias (PDF y web)
tema-tinieblas-pergamino.css   variante para imprimir: páginas pergamino, portada y contraportada oscuras
tema/vistas/                   PNG del ejemplo de pdf-historias con cada tema
tools/build.py                 genera todo lo anterior desde la paleta (python -I tools/build.py)
tools/probar_tema.py           aplica el tema al ejemplo de pdf-historias sin modificar la herramienta
tools/origen/                  copia de los SVG originales de los que se derivan los logos
tools/fonts/                   Barlow (OFL), solo para convertir en contornos el texto «TINIEBLAS» de los logos
```

Los logos **no se redibujan**. `build.py` lee los SVG originales de `tools/origen/`, cambia sus colores en orden y añade «☾ TINIEBLAS» en la fila del descriptor, en Barlow convertida a contornos como el resto del logotipo.

## Regenerar

```bash
pip install fonttools pymupdf pillow
python -I tools/build.py                                     # SVG, tokens, brand.json, temas y tabla de contraste
python -I tools/probar_tema.py                               # vistas tema/vistas/noche-*.png
python -I tools/probar_tema.py --tema tema-tinieblas-pergamino.css --prefijo pergamino
```

`probar_tema.py` deja los temporales y el perfil de Edge en `D:\capturas-claude\tinieblas` (variable `TINIEBLAS_TMP`), nunca en C:.

## Tema para pdf-historias

`tema-tinieblas.css` es un **override**: va después del CSS que genera `D:\herramientas\pdf-historias\maquetar.py`, en el mismo documento. No cambia el Markdown ni las directivas. Cubre:

- **Página:** fondo, cabecera, pie, hexágono del número (ahora un d20 agrietado en oro) y triángulo de esquina sangre + vela.
- **Títulos:** píldora del capítulo, sombra del h1 en sangre y capitular en oro de vela.
- **Bloques:** divisores y citas (musgo + vela), figuras, recuadros (`turquesa`/`coral`/`sol`/`tinta` → musgo, sangre, vela, abismo) y leyendas (panel popular en niebla, panel tinieblas en abismo).
- **Portada:** el `color:` del front matter se traduce a su versión nocturna (turquesa → musgo profundo, coral → sangre, sol → vela, tinta → abismo, crema → pergamino viejo) con un selector sobre el estilo en línea. También cambia el sello.
- **Contraportada:** usa el d20 agrietado, el logotipo Tinieblas y el lema nuevo.
- **Web (`--web`):** barra, libro, índice y botón de volver.

Las imágenes de marca que la herramienta inserta con `<img>` (sello, d20, logotipo inverso) se sustituyen con `content: url(data:…)`, que Edge y Chrome admiten en `<img>`. El CSS no depende de ninguna ruta: todos los SVG van en línea.

### Conexión propuesta: opción `--tema`

La herramienta la está editando otra persona, así que este repo **no la modifica**. El cambio que se propone es mínimo:

```python
# main(): nueva opción
ap.add_argument("--tema", help="CSS que se aplica encima del estilo base (p. ej. tema-tinieblas.css)")
...
tema = Path(a.tema).read_text(encoding="utf-8") if a.tema else ""
m = Maquetador(md, tema=tema)            # y lo mismo para Maquetador(md, web=web, tema=tema)

# Maquetador.html(), versión PDF: añadir el tema después del CSS base
f"<title>{titulo}</title><style>{css}</style><style>{self.tema}</style></head>"

# versión web: añadirlo al final de estilo.css
(self.web / "estilo.css").write_text(css + WEB_CSS.format(...) + "\n" + self.tema, encoding="utf-8")
```

Uso:

```bash
python -I maquetar.py historia.md --tema D:\tazon-para-dos-tinieblas\tema-tinieblas.css --png vistas
python -I maquetar.py historia.md --web web --solo-web --tema D:\tazon-para-dos-tinieblas\tema-tinieblas.css
python -I maquetar.py historia.md --tema D:\tazon-para-dos-tinieblas\tema-tinieblas-pergamino.css   # para imprimir
```

Otra opción es una clave `tema: tinieblas` en el front matter que busque `tema-<nombre>.css` en una carpeta `temas/` de la herramienta. Mientras tanto, `python -I tools/probar_tema.py --md historia.md --web` hace lo mismo por fuera: llama a `--solo-html`, inyecta el tema e imprime con Edge.

Si la herramienta añade clases o colores nuevos, regenera el tema con `build.py` (función `theme_css`). La portada se detecta por el color del primer `<rect>` de `bloque_diagonal()`, y si esa función cambia hay que revisar ese selector.

## Reglas rápidas

- **Sí:** las piezas del kit con la luz cambiada; oro de vela para lo que brilla; texto largo en pergamino sobre noche o en tinta sobre pergamino; motivos muiscas como geometría y con respeto; nombrar el territorio (Engativá, el humedal Jaboque).
- **No:** rostros de personas reales sin consentimiento; gore o calaveras (el miedo se sugiere); oro o sangre como texto pequeño; degradados y sombras difusas; fuentes góticas; «Tinieblas» sin el nombre madre o el tazón redibujado.

## Licencias

- Marca, mascota y textos: © Tazón para Dos. Todos los derechos reservados.
- Fuentes Barlow: SIL Open Font License (`tools/fonts/OFL.txt`). Space Grotesk, DM Sans y DM Mono se cargan desde Google Fonts (OFL).
- *Mago: La Ascensión*, *Hombre Lobo: El Apocalipsis*, *Changeling: El Ensueño* y *Mundo de Tinieblas* son marcas de sus titulares. Esta es una identidad visual de fan para una comunidad de juego, sin afiliación con ellos.
