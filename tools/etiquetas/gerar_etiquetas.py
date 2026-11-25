#!/usr/bin/env python3
"""Gera as etiquetas adesivas da torre (identidade visual da IHM do main.c), em tamanho real.

  1. Título .......... 90 × 32 mm — mesmo cabeçalho da IHM (logo UNIP + "Solar Smart Tower")
  2. Conexão Wi-Fi ... 90 × 60 mm — em 2 passos, cada um com seu QR code:
       1) rede e senha + QR que conecta o celular à rede
       2) endereço da IHM + QR que abre http://192.168.4.1 no navegador

Cores e logo: os mesmos da IHM (main.c: --azul #0b2a5b, --azul2 #16407f, --ouro #f5b800).
O QR do passo 1 usa o formato padrão de Wi-Fi (WIFI:T:WPA;S:...;P:...;;); o do passo 2 é a URL.
Ambos são lidos pela câmera do Android e do iPhone.

Saídas (docs/etiquetas/):
  etiquetas_A4.pdf    folha A4 com 2 jogos, marcas de corte e régua de conferência (imprimir em 100%)
  etiqueta_titulo.pdf / etiqueta_wifi.pdf   cada etiqueta isolada, no tamanho exato (para gráfica)
  etiqueta_titulo.png / etiqueta_wifi.png   prévias em 600 dpi

Uso: uv run --with segno --with pymupdf python tools/etiquetas/gerar_etiquetas.py
"""
import io
import os
import subprocess
import tempfile
from pathlib import Path

import pymupdf as fitz
import segno

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "docs/etiquetas"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

REDE, SENHA, IP = "SOLAR_TOWER", "torre1234", "192.168.4.1"
QR_WIFI = f"WIFI:T:WPA;S:{REDE};P:{SENHA};;"
QR_URL = f"http://{IP}"

# Logo da IHM (main.c), mesmo desenho em SVG
# (fundo branco arredondado feito em CSS: o <rect rx> saía cortado no PDF do Chrome)
LOGO = """<div class="logo"><svg viewBox="0 0 46 46"><text x="23" y="27" text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-weight="900"
 font-size="15" fill="#0b2a5b" letter-spacing="-.5">UNIP</text>
<rect x="9" y="32" width="28" height="4" rx="2" fill="#f5b800"/></svg></div>"""


# Régua de 50 mm (traços a cada 10 mm), em unidades de 0,1 mm
REGUA = ('<svg viewBox="0 0 502 30"><path d="M1 29H501' + "".join(f"M{1 + i * 100} 29V{0 if i % 5 == 0 else 12}"
         for i in range(6)) + '" stroke="#14213d" stroke-width="2" fill="none"/></svg>')


def qr_svg(dados):
    buf = io.BytesIO()
    segno.make(dados, error="m").save(buf, kind="svg", border=0, dark="#0b2a5b", xmldecl=False,
                                         svgns=True, omitsize=True)
    return buf.getvalue().decode().replace("<svg ", '<svg class="qr" ', 1)


CSS = """
@page { margin: 0 }
* { box-sizing: border-box; margin: 0; padding: 0 }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact }
body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; color: #14213d }
.et { position: relative; overflow: hidden; border-radius: 3mm }
.logo { background: #fff; border-radius: 21.7% }
.logo svg { display: block; width: 100%; height: 100% }

/* 1. Título 90 × 32 */
.titulo { width: 90mm; height: 32mm; color: #fff; display: flex; align-items: center; gap: 4.5mm;
  padding: 0 5mm 1.4mm; background: linear-gradient(135deg, #0b2a5b, #16407f); border-bottom: 1.4mm solid #f5b800 }
.titulo .logo { width: 20mm; height: 20mm; flex: none }
.titulo h1 { font-size: 6.3mm; font-weight: 750; letter-spacing: -.1mm; line-height: 1.05; white-space: nowrap }
.titulo p { font-size: 3.1mm; opacity: .78; margin-top: 1.3mm; white-space: nowrap }

/* 2. Wi-Fi 90 × 60 */
.wifi { width: 90mm; height: 60mm; background: #eef1f6; display: flex; flex-direction: column }
.wifi header { height: 10.5mm; flex: none; display: flex; align-items: center; justify-content: space-between;
  padding: 0 4mm; color: #fff; background: linear-gradient(135deg, #0b2a5b, #16407f); border-bottom: .9mm solid #f5b800 }
.wifi header b { font-size: 4mm; font-weight: 750; letter-spacing: -.05mm }
.wifi header span { font-size: 2.2mm; font-weight: 800; letter-spacing: .35mm; color: #f5b800 }
.wifi main { flex: 1; display: flex; flex-direction: column; gap: 2mm; padding: 2.4mm 3mm 3mm }
.passo { flex: 1; display: flex; align-items: center; gap: 2.5mm; border-radius: 2mm; padding: 1.6mm 2mm 1.6mm 3mm;
  background: #fff; border: .25mm solid #e3e7ee }
.passo .txt { flex: 1; display: flex; flex-direction: column; gap: .9mm; min-width: 0 }
.passo em { font-style: normal; font-size: 1.8mm; font-weight: 800; letter-spacing: .25mm; color: #16407f; text-transform: uppercase }
.passo em b { display: inline-block; width: 3.1mm; height: 3.1mm; line-height: 3.1mm; border-radius: 50%; text-align: center;
  background: #0b2a5b; color: #fff; margin-right: 1mm; letter-spacing: 0 }
.campos { display: flex; gap: 3.5mm }
.passo small { display: block; font-size: 1.6mm; font-weight: 800; letter-spacing: .25mm; color: #66728a; text-transform: uppercase }
.passo strong { display: block; font-size: 4.3mm; font-weight: 800; letter-spacing: -.05mm; line-height: 1.1; white-space: nowrap }
.passo.ip { background: linear-gradient(135deg, #0b2a5b, #16407f); border: 0; color: #fff }
.passo.ip em { color: #f5b800 }
.passo.ip em b { background: #f5b800; color: #0b2a5b }
.passo.ip strong { font-size: 6.4mm }
.passo.ip small { color: #c9d3e6; margin-top: .2mm }
.qrbox { flex: none; background: #fff; border-radius: 1.4mm; padding: 1.2mm }
.qr { width: 16.5mm; height: 16.5mm; display: block }
.passo.ip .qr { width: 15mm; height: 15mm }
.passo.ip .qrbox { padding: 2mm }

/* Folha A4 */
.folha { width: 210mm; height: 297mm; padding: 14mm 10mm; position: relative }
.folha h2 { font-size: 5mm; color: #0b2a5b }
.folha .nota { font-size: 3mm; color: #66728a; margin-top: 1.5mm; line-height: 1.45 }
.jogos { display: flex; flex-direction: column; gap: 12mm; margin-top: 12mm; align-items: flex-start }
.jogo { display: flex; gap: 10mm; align-items: flex-start }
.corte { position: relative; padding: 0 }
.corte i { position: absolute; width: 4mm; height: 4mm; border-color: #9aa3b5; border-style: solid; border-width: 0 }
.corte .a { left: -5mm; top: -5mm; border-right-width: .15mm; border-bottom-width: .15mm }
.corte .b { right: -5mm; top: -5mm; border-left-width: .15mm; border-bottom-width: .15mm }
.corte .c { left: -5mm; bottom: -5mm; border-right-width: .15mm; border-top-width: .15mm }
.corte .d { right: -5mm; bottom: -5mm; border-left-width: .15mm; border-top-width: .15mm }
.corte em { position: absolute; left: 0; top: -4.2mm; font: 600 2.2mm system-ui, sans-serif; color: #9aa3b5; font-style: normal }
.regua { position: absolute; left: 10mm; bottom: 14mm; font-size: 2.6mm; color: #66728a }
.regua svg { display: block; width: 50.2mm; height: 3mm; margin-bottom: 1.2mm }
"""


def titulo():
    return f'<div class="et titulo">{LOGO}<div><h1>Solar Smart Tower</h1><p>IHM do rastreador solar</p></div></div>'


def wifi():
    return f"""<div class="et wifi"><header><b>Solar Smart Tower</b><span>CONEXÃO WI-FI</span></header><main>
<div class="passo"><div class="txt"><em><b>1</b>Conecte-se à rede</em><div class="campos">
<div><small>Rede (login)</small><strong>{REDE}</strong></div><div><small>Senha</small><strong>{SENHA}</strong></div></div></div>
<div class="qrbox">{qr_svg(QR_WIFI)}</div></div>
<div class="passo ip"><div class="txt"><em><b>2</b>Abra a IHM no navegador</em><strong>{IP}</strong>
<small>ou escaneie o QR ao lado</small></div><div class="qrbox">{qr_svg(QR_URL)}</div></div></main></div>"""


def corte(rotulo, html):
    return f'<div class="corte"><em>{rotulo}</em>{html}<i class="a"></i><i class="b"></i><i class="c"></i><i class="d"></i></div>'


def pagina(corpo, larg, alt):
    return (f'<!doctype html><html lang="pt-BR"><meta charset="utf-8"><style>{CSS}'
            f'@page {{ size: {larg}mm {alt}mm }}</style><body>{corpo}</body></html>')


def folha_a4():
    jogo = lambda: (f'<div class="jogo">{corte("1 · título 90 × 32 mm", titulo())}'
                    f'{corte("2 · Wi-Fi 90 × 60 mm", wifi())}</div>')
    return (f'<div class="folha"><h2>Etiquetas da torre — Solar Smart Tower</h2>'
            f'<p class="nota">Imprimir em <b>100% (tamanho real)</b>, sem "ajustar à página", em papel adesivo '
            f'(vinil ou fotográfico). Cortar pelas marcas e arredondar os cantos. Colar o título a cerca de 12 cm '
            f'da ponta de cima do tubo e a etiqueta de Wi-Fi logo abaixo. Confira a régua: deve medir 50&nbsp;mm.</p>'
            f'<div class="jogos">{jogo()}{jogo()}</div>'
            f'<div class="regua">{REGUA}régua de conferência: 50 mm</div></div>')


def imprimir(html, pdf):
    with tempfile.TemporaryDirectory() as tmp:
        arq = Path(tmp) / "p.html"
        arq.write_text(html, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={tmp}/perfil", f"--print-to-pdf={pdf}", arq.as_uri()],
                       check=True, capture_output=True)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    imprimir(pagina(folha_a4(), 210, 297), SAIDA / "etiquetas_A4.pdf")
    for nome, html, alt in (("titulo", titulo(), 32), ("wifi", wifi(), 60)):
        pdf = SAIDA / f"etiqueta_{nome}.pdf"
        imprimir(pagina(html, 90, alt), pdf)
        with fitz.open(pdf) as doc:
            doc[0].get_pixmap(dpi=600).save(SAIDA / f"etiqueta_{nome}.png")
    for f in sorted(SAIDA.iterdir()):
        print(f.relative_to(RAIZ), f"{f.stat().st_size / 1024:.0f} kB")


if __name__ == "__main__":
    main()
