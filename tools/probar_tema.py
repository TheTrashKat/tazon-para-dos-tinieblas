"""Prueba el tema Tinieblas sobre pdf-historias SIN modificar la herramienta.

Hace a mano lo que haría la opción --tema propuesta en el README:
  1. llama a maquetar.py --solo-html (salida en una carpeta temporal en D:),
  2. añade el CSS del tema como <style> justo antes de </head>,
  3. imprime a PDF con Edge headless (perfil y temporales en D:),
  4. guarda una vista PNG por página (necesita PyMuPDF) y, con --web, la versión web tematizada.

Uso:
  python -I tools/probar_tema.py                                  # ejemplo de la herramienta, tema noche
  python -I tools/probar_tema.py --tema tema-tinieblas-pergamino.css --prefijo pergamino
  python -I tools/probar_tema.py --md D:\\historias\\...\\historia.md --vistas D:\\capturas-claude\\vistas
"""
import argparse, os, pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
HERRAMIENTA = pathlib.Path(os.environ.get("PDF_HISTORIAS", r"D:\herramientas\pdf-historias"))
TEMPORAL = pathlib.Path(os.environ.get("TINIEBLAS_TMP", r"D:\capturas-claude\tinieblas"))
EDGE = os.environ.get("PDF_HISTORIAS_NAVEGADOR", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def imprimir(html, pdf):
    perfil, tmp = TEMPORAL / "perfil-edge", TEMPORAL / "tmp"
    perfil.mkdir(parents=True, exist_ok=True); tmp.mkdir(parents=True, exist_ok=True)
    if pdf.exists():
        pdf.unlink()
    env = dict(os.environ, TMP=str(tmp), TEMP=str(tmp))
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", f"--user-data-dir={perfil}", f"--disk-cache-dir={tmp / 'cache'}",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=15000",
                    f"--print-to-pdf={pdf}", html.as_uri()], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    t0, ultimo = time.time(), -1
    while time.time() - t0 < 120:
        if pdf.exists() and pdf.stat().st_size > 0 and pdf.stat().st_size == ultimo:
            return
        ultimo = pdf.stat().st_size if pdf.exists() else -1
        time.sleep(0.8)
    sys.exit("No se generó el PDF.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default=str(HERRAMIENTA / "ejemplo" / "ejemplo.md"))
    ap.add_argument("--tema", default=str(ROOT / "tema-tinieblas.css"))
    ap.add_argument("--vistas", default=str(ROOT / "tema" / "vistas"))
    ap.add_argument("--prefijo", default="noche")
    ap.add_argument("--dpi", type=int, default=50)
    ap.add_argument("--web", action="store_true", help="genera también la versión web tematizada")
    a = ap.parse_args()

    md = pathlib.Path(a.md).resolve()
    tema = pathlib.Path(a.tema).resolve().read_text(encoding="utf-8")
    trabajo = TEMPORAL / "prueba" / a.prefijo
    trabajo.mkdir(parents=True, exist_ok=True)
    pdf = trabajo / (md.stem + ".pdf")
    subprocess.run([sys.executable, "-I", str(HERRAMIENTA / "maquetar.py"), str(md), "--solo-html", "-o", str(pdf)],
                   check=True, cwd=str(trabajo))
    html = pdf.with_suffix(".html")
    s = html.read_text(encoding="utf-8")
    s = s.replace("</head>", f"<style>/* tema */\n{tema}</style></head>", 1)
    html.write_text(s, encoding="utf-8")
    imprimir(html, pdf)
    print("PDF:", pdf)

    try:
        import fitz
    except ImportError:
        print("(sin PyMuPDF no hay vistas PNG)")
        return
    vistas = pathlib.Path(a.vistas)
    vistas.mkdir(parents=True, exist_ok=True)
    with fitz.open(pdf) as doc:
        for i, pag in enumerate(doc, 1):
            pag.get_pixmap(dpi=a.dpi).save(vistas / f"{a.prefijo}-{i:02d}.png")
        print(f"{doc.page_count} vistas en {vistas}")

    if a.web:
        web = trabajo / "web"
        subprocess.run([sys.executable, "-I", str(HERRAMIENTA / "maquetar.py"), str(md), "--web", str(web), "--solo-web"],
                       check=True, cwd=str(trabajo))
        css = web / "estilo.css"
        css.write_text(css.read_text(encoding="utf-8") + "\n/* tema */\n" + tema, encoding="utf-8")
        print("Web:", web / "index.html")


if __name__ == "__main__":
    main()
