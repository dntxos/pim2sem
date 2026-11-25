#!/usr/bin/env python3
"""Arte grande para colar no poste da torre: faixa vertical de 120 × 400 mm (identidade da IHM).

O tubo tem Ø126 mm (volta de 396 mm): 120 mm de largura cobrem ~109° da volta, então a faixa fica
inteira à vista de quem olha de frente. Conteúdo: título, ilustração do rastreamento, como funciona,
números do projeto e os dois QR codes (rede Wi-Fi e IHM), com os dados do grupo no rodapé.

Saídas (docs/etiquetas/):
  poster_poste.pdf      tamanho exato 120 × 400 mm (para gráfica: adesivo vinil)
  poster_poste_A3.pdf   numa folha A3 com marcas de corte (imprimir em 100%)
  poster_poste.png      prévia em 200 dpi

Uso: uv run --with segno --with pymupdf python tools/etiquetas/gerar_poster.py
"""
import pymupdf

from gerar_etiquetas import CSS, IP, LOGO, QR_URL, QR_WIFI, REDE, REGUA, SAIDA, SENHA, corte, imprimir, pagina, qr_svg

L, A = 120, 400  # mm

# Ilustração: trajetória do Sol de Leste a Oeste e a placa no poste apontada para ele (unidades em mm)
HEROI = """<svg viewBox="0 0 120 96" class="heroi">
<defs>
 <linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dfe7f3"/><stop offset="1" stop-color="#f6f8fb"/></linearGradient>
 <linearGradient id="tubo" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7d8696"/><stop offset=".45" stop-color="#d5dae2"/><stop offset="1" stop-color="#6b7383"/></linearGradient>
 <radialGradient id="brilho"><stop offset="0" stop-color="#f5b800" stop-opacity=".45"/><stop offset="1" stop-color="#f5b800" stop-opacity="0"/></radialGradient>
</defs>
<rect width="120" height="96" fill="url(#ceu)"/>
<path d="M8 84 Q60 -18 112 84" fill="none" stroke="#9fb0cc" stroke-width=".5" stroke-dasharray="1.6 1.4"/>
<circle cx="19" cy="57" r="3.2" fill="#f5b800" opacity=".35"/>
<circle cx="101" cy="57" r="3.2" fill="#f5b800" opacity=".35"/>
<circle cx="60" cy="35" r="3.2" fill="#f5b800" opacity=".35"/>
<circle cx="86" cy="33" r="17" fill="url(#brilho)"/>
<g stroke="#f5b800" stroke-width="1.1" stroke-linecap="round">
 <path d="M86 20.5v-3.5M86 45.5v3.5M73.5 33h-3.5M98.5 33h3.5M77.2 24.2l-2.5-2.5M94.8 41.8l2.5 2.5M77.2 41.8l-2.5 2.5M94.8 24.2l2.5-2.5"/>
</g>
<circle cx="86" cy="33" r="8" fill="#f5b800"/>
<path d="M80 38 L63 49" stroke="#f5b800" stroke-width=".7" stroke-dasharray="1.4 1.2"/>
<path d="M82.5 40.5 L66 52" stroke="#f5b800" stroke-width=".7" stroke-dasharray="1.4 1.2"/>
<text x="8" y="92" font-size="3" font-weight="700" fill="#66728a" letter-spacing=".3">LESTE · manhã</text>
<text x="112" y="92" font-size="3" font-weight="700" fill="#66728a" letter-spacing=".3" text-anchor="end">tarde · OESTE</text>
<rect x="51" y="66" width="10" height="30" fill="url(#tubo)"/>
<rect x="53.5" y="53" width="5" height="14" rx="1" fill="#4a5466"/>
<g transform="translate(0 -8)">
<g transform="rotate(47 56 61)">
 <rect x="38" y="57" width="36" height="5" rx=".8" fill="#0b2a5b" stroke="#c9d3e6" stroke-width=".6"/>
 <path d="M47 57v5M56 57v5M65 57v5" stroke="#3d64a8" stroke-width=".35"/>
 <rect x="54.6" y="54.6" width="2.8" height="2.4" rx=".5" fill="#f5b800"/>
</g>
<circle cx="56" cy="61" r="1.6" fill="#14213d"/></g>
</svg>"""

CSS_POSTER = """
.poster { width: 120mm; height: 400mm; background: #eef1f6; display: flex; flex-direction: column; overflow: hidden }
.p-topo { flex: none; color: #fff; text-align: center; padding: 11mm 6mm 9mm;
  background: linear-gradient(160deg, #0b2a5b, #16407f); border-bottom: 2mm solid #f5b800 }
.p-topo .logo { width: 26mm; height: 26mm; margin: 0 auto 6mm }
.p-topo h1 { font-size: 10.6mm; font-weight: 800; letter-spacing: -.25mm; line-height: 1 }
.p-topo p { font-size: 4.2mm; margin-top: 3mm; opacity: .8 }
.p-topo .selo { display: inline-block; margin-top: 4.5mm; padding: 1.3mm 3.4mm; border-radius: 9mm; font-size: 2.7mm;
  font-weight: 800; letter-spacing: .4mm; color: #0b2a5b; background: #f5b800 }
.heroi { display: block; width: 120mm; height: 96mm; flex: none }
.p-sec { padding: 6mm 7mm 0 }
.p-sec h2 { font-size: 3mm; font-weight: 800; letter-spacing: .5mm; color: #16407f; text-transform: uppercase; margin-bottom: 3mm }
.passos { display: flex; flex-direction: column; gap: 2.2mm }
.pp { display: flex; gap: 3mm; align-items: center; background: #fff; border: .25mm solid #e3e7ee; border-radius: 2.5mm; padding: 2.6mm 3.2mm }
.pp b { flex: none; width: 7mm; height: 7mm; border-radius: 50%; background: #0b2a5b; color: #fff; font-size: 3.6mm;
  display: flex; align-items: center; justify-content: center }
.pp div { font-size: 3.3mm; line-height: 1.3 }
.pp strong { display: block; font-size: 3.8mm; color: #0b2a5b }
.numeros { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.2mm }
.num { background: linear-gradient(160deg, #0b2a5b, #16407f); color: #fff; border-radius: 2.5mm; padding: 3mm 1mm; text-align: center }
.num strong { display: block; font-size: 7mm; font-weight: 800; letter-spacing: -.2mm; color: #f5b800; line-height: 1.05 }
.num span { display: block; font-size: 2.5mm; margin-top: 1mm; opacity: .9 }
.nota { font-size: 2.3mm; color: #66728a; margin-top: 1.6mm }
.qrs { display: grid; grid-template-columns: 1fr 1fr; gap: 2.6mm }
.qc { background: #fff; border: .25mm solid #e3e7ee; border-radius: 2.5mm; padding: 3mm; display: flex; flex-direction: column; align-items: center; text-align: center }
.qc em { font-style: normal; font-size: 2.4mm; font-weight: 800; letter-spacing: .25mm; color: #16407f; text-transform: uppercase; align-self: stretch; text-align: left }
.qc em i { font-style: normal; display: inline-block; width: 4mm; height: 4mm; line-height: 4mm; text-align: center; border-radius: 50%;
  background: #0b2a5b; color: #fff; margin-right: 1.2mm }
.qc .qr { width: 36mm; height: 36mm; margin: 3mm 0 2.5mm }
.qc small { font-size: 2.1mm; font-weight: 800; letter-spacing: .25mm; color: #66728a; text-transform: uppercase }
.qc strong { font-size: 4.4mm; font-weight: 800; line-height: 1.15 }
.qc.ip { background: linear-gradient(160deg, #0b2a5b, #16407f); border: 0; color: #fff }
.qc.ip em { color: #f5b800 } .qc.ip em i { background: #f5b800; color: #0b2a5b }
.qc.ip small { color: #c9d3e6 }
.qc.ip .qrfundo { background: #fff; border-radius: 1.6mm; padding: 2mm; margin: 3mm 0 2.5mm }
.qc.ip .qr { margin: 0; width: 32mm; height: 32mm }
.p-rodape { margin-top: auto; flex: none; color: #fff; text-align: center; padding: 5mm 6mm 6mm;
  background: linear-gradient(160deg, #0b2a5b, #16407f); border-top: 1.4mm solid #f5b800 }
.p-rodape strong { display: block; font-size: 3.4mm; letter-spacing: .1mm }
.p-rodape span { display: block; font-size: 2.5mm; opacity: .8; margin-top: 1.4mm; line-height: 1.45 }
.folha-a3 { width: 297mm; height: 420mm; display: flex; align-items: center; justify-content: center; gap: 22mm; position: relative }
.folha-a3 .info { width: 110mm; font-size: 3.4mm; color: #66728a; line-height: 1.5 }
.folha-a3 .info h2 { font-size: 5.5mm; color: #0b2a5b; margin-bottom: 3mm }
.folha-a3 .info p + p { margin-top: 2.5mm }
.folha-a3 .regua { position: static; margin-top: 8mm }
"""

GRUPO = "Ana Paula Dias Campos · Dawid Felipe Fernandes da Silva · Rafael Kazuo Sato Simião · Samuel Bolfarini Pires · Talita dos Santos"


def poster():
    return f"""<div class="poster">
<div class="p-topo">{LOGO}<h1>Solar Smart Tower</h1><p>Rastreador solar de dois eixos</p>
<span class="selo">A PLACA SEGUE O SOL</span></div>
{HEROI}
<div class="p-sec"><h2>Como funciona</h2><div class="passos">
<div class="pp"><b>1</b><div><strong>4 sensores de luz</strong>Separados por um anteparo, comparam a luz de cada lado da placa.</div></div>
<div class="pp"><b>2</b><div><strong>ESP32 decide</strong>A cada 100 ms calcula para onde girar até a luz ficar equilibrada.</div></div>
<div class="pp"><b>3</b><div><strong>2 servomotores</strong>Giram a base e inclinam a placa; à noite ela estaciona e espera o amanhecer.</div></div>
</div></div>
<div class="p-sec"><div class="numeros">
<div class="num"><strong>10 W</strong><span>placa solar</span></div>
<div class="num"><strong>2 eixos</strong><span>de movimento</span></div>
<div class="num"><strong>+47%</strong><span>energia no ano*</span></div>
</div><p class="nota">* Simulação do ano inteiro, comparada a uma placa fixa voltada ao Norte.</p></div>
<div class="p-sec"><h2>Acompanhe ao vivo pelo celular</h2><div class="qrs">
<div class="qc"><em><i>1</i>Conecte ao Wi-Fi</em>{qr_svg(QR_WIFI)}<small>Rede</small><strong>{REDE}</strong>
<small style="margin-top:1.4mm">Senha</small><strong>{SENHA}</strong></div>
<div class="qc ip"><em><i>2</i>Abra a IHM</em><div class="qrfundo">{qr_svg(QR_URL)}</div><small>No navegador</small>
<strong style="font-size:5.4mm">{IP}</strong><small style="margin-top:1.4mm">funciona sem internet</small></div>
</div></div>
<div class="p-rodape"><strong>UNIP · Automação Industrial · PIM II · 2026</strong><span>{GRUPO}</span></div>
</div>"""


def folha_a3():
    return (f'<div class="folha-a3"><div class="info"><h2>Arte do poste — Solar Smart Tower</h2>'
            f'<p>Faixa de <b>120 × 400 mm</b> para o tubo de Ø126 mm (cobre ~109° da volta, fica inteira à vista '
            f'de frente).</p><p>Imprimir em <b>100% (tamanho real)</b> em vinil adesivo ou papel fotográfico com '
            f'laminação. Cortar pelas marcas. Colar com o topo logo abaixo da cabeça da torre, alinhada com a '
            f'frente (lado dos sensores).</p><p>Para gráfica, use <b>poster_poste.pdf</b> (tamanho exato).</p>'
            f'<div class="regua">{REGUA}régua de conferência: 50 mm</div></div>'
            f'{corte("arte do poste 120 × 400 mm", poster())}</div>')


def main():
    css = CSS + CSS_POSTER
    pag = lambda corpo, larg, alt: pagina(corpo, larg, alt).replace(CSS, css, 1)
    imprimir(pag(poster(), L, A), SAIDA / "poster_poste.pdf")
    imprimir(pag(folha_a3(), 297, 420), SAIDA / "poster_poste_A3.pdf")
    with pymupdf.open(SAIDA / "poster_poste.pdf") as doc:
        doc[0].get_pixmap(dpi=200).save(SAIDA / "poster_poste.png")
    for f in ("poster_poste.pdf", "poster_poste_A3.pdf", "poster_poste.png"):
        with (SAIDA / f).open("rb") as h:
            print(f, f"{len(h.read()) / 1024:.0f} kB")


if __name__ == "__main__":
    main()
