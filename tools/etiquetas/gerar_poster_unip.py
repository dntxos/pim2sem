#!/usr/bin/env python3
"""Pôster acadêmico no padrão UNIP (modelo do curso): A3 retrato, fundo cinza e caixas escuras.

Mesma disposição do modelo:
  cabeçalho (logo UNIP + instituição/curso/campus) · nome do projeto · descrição ·
  duas telas explicativas (protótipo e controle pelo celular) · resultados ·
  componentes do grupo · logo do projeto · orientador.

O PDF é vetorial (as fotos entram em resolução própria): imprime em A3 ou ampliado para A1/A0;
a versão A4 é a mesma página reduzida (mesma proporção √2), sem perda de qualidade.

Saídas (docs/etiquetas/):
  poster_unip_A3.pdf   297 × 420 mm
  poster_unip_A4.pdf   210 × 297 mm
  poster_unip.png      prévia em 150 dpi

Uso: uv run --with segno --with pymupdf python tools/etiquetas/gerar_poster_unip.py
"""
import pymupdf

from gerar_etiquetas import IP, QR_URL, QR_WIFI, RAIZ, REDE, SAIDA, SENHA, imprimir, qr_svg

L, A = 297, 420  # mm
MIDIA = RAIZ / "docs/imagens_videos_testes_fisicos"
FIG = RAIZ / "docs/relatorio/figuras"
FOTO = (MIDIA / "resultado_final_com_painel1.jpeg").as_uri()
IHM = (FIG / "ihm_captura.png").as_uri()

INTEGRANTES = ["Ana Paula Dias Campos", "Dawid Felipe Fernandes da Silva", "Rafael Kazuo Sato Simião",
               "Samuel Bolfarini Pires", "Talita dos Santos"]
ORIENTADOR = "Prof. Marcelo Bellodi"

# Logo UNIP (desenho vetorial: "UNIP" amarelo em itálico + faixa vermelha "UNIVERSIDADE PAULISTA")
LOGO_UNIP = """<svg viewBox="0 0 340 112" class="unip">
<g transform="skewX(-14)">
 <text x="196" y="62" text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-weight="900"
  font-size="74" letter-spacing="-2" fill="#ffe500" stroke="#c9b000" stroke-width="1.2">UNIP</text>
 <rect x="18" y="70" width="330" height="36" rx="3" fill="#e30613"/>
 <rect x="18" y="70" width="330" height="36" rx="3" fill="none" stroke="#fff" stroke-width="2.5"/>
 <text x="183" y="96" text-anchor="middle" font-family="Arial,sans-serif" font-weight="800" font-size="23"
  font-style="italic" fill="#fff" letter-spacing=".4">UNIVERSIDADE PAULISTA</text>
</g></svg>"""

# Logo do projeto: Sol, placa no poste e o nome (mesmas cores da IHM)
LOGO_PROJ = """<svg viewBox="0 0 100 92" class="emblema">
<circle cx="70" cy="22" r="9" fill="#f5b800"/>
<g stroke="#f5b800" stroke-width="2.2" stroke-linecap="round">
 <path d="M70 6v-3M70 38v3M54 22h-3M86 22h3M58.7 10.7l-2-2M81.3 33.3l2 2M58.7 33.3l-2 2M81.3 10.7l2-2"/></g>
<g transform="rotate(-32 40 44)"><rect x="20" y="40" width="40" height="7" rx="1.2" fill="#16407f" stroke="#c9d3e6" stroke-width="1"/>
 <path d="M30 40v7M40 40v7M50 40v7" stroke="#5b83c7" stroke-width=".7"/></g>
<rect x="37" y="46" width="6" height="22" rx="1" fill="#9aa3b5"/>
<text x="50" y="80" text-anchor="middle" font-family="Open Sans,Helvetica Neue,Arial,sans-serif" font-weight="800"
 font-size="9.4" fill="#fff">Solar Smart</text>
<text x="50" y="90" text-anchor="middle" font-family="Open Sans,Helvetica Neue,Arial,sans-serif" font-weight="800"
 font-size="9.4" fill="#f5b800" letter-spacing="1.5">TOWER</text>
</svg>"""

# Textura de "quadro negro" do modelo: gradiente escuro + ruído leve
RUIDO = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/%3E"
         "%3CfeColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .07 0'/%3E%3C/filter%3E"
         "%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E\")")

CSS = f"""
@page {{ size: {L}mm {A}mm; margin: 0 }}
* {{ box-sizing: border-box; margin: 0; padding: 0 }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact }}
body {{ font-family: "Open Sans", "Helvetica Neue", Arial, sans-serif; color: #111 }}
.pag {{ width: {L}mm; height: {A}mm; background: #b3b3b3; position: relative; overflow: hidden; padding: 0 4mm }}
.quadro {{ color: #fff; background: {RUIDO}, radial-gradient(ellipse at 50% 38%, #3a3a3a 0%, #1b1b1b 45%, #070707 100%) }}

/* Cabeçalho */
header {{ display: flex; align-items: center; height: 58mm; gap: 4mm }}
.unip {{ width: 92mm; flex: none }}
header .inst {{ flex: 1; text-align: center; font-family: Roboto, Arial, sans-serif; font-weight: 700;
  font-size: 7.6mm; line-height: 1.32; color: #161616 }}

.titulo {{ margin: 3mm 26mm 0; height: 28mm; display: flex; align-items: center; justify-content: center }}
.titulo h1 {{ font-size: 18.5mm; font-weight: 800; letter-spacing: -.3mm }}
.sub {{ text-align: center; font-size: 5mm; font-weight: 600; color: #262626; margin: 2.6mm 0 2.4mm }}

.descricao {{ min-height: 62mm; padding: 6mm 12mm; display: flex; flex-direction: column; justify-content: center; gap: 3mm }}
.descricao h2, .tela h2, .grupo-tit {{ font-weight: 800 }}
.descricao h2 {{ font-size: 8.4mm; text-align: center }}
.descricao p {{ font-size: 4.25mm; line-height: 1.5; text-align: justify; color: #e9e9e9 }}
.descricao b {{ color: #ffd23a }}

/* Telas explicativas */
.telas {{ display: flex; gap: 10mm; margin: 8mm 7mm 0; height: 134mm }}
.tela {{ flex: 1; padding: 6mm 6mm 5mm; display: flex; flex-direction: column; gap: 4mm;
  border-top: .9mm solid #e6e6e6 }}
.tela h2 {{ font-size: 8.4mm; text-align: center; line-height: 1 }}
.foto {{ display: flex; gap: 4.5mm; flex: 1; min-height: 0 }}
.foto img:not(.cel) {{ width: 62mm; height: 100%; object-fit: cover; object-position: 50% 40%; border-radius: 2mm;
  border: .6mm solid #e6e6e6 }}
ol.passos {{ list-style: none; display: flex; flex-direction: column; gap: 3.6mm; justify-content: center; counter-reset: p }}
ol.passos li {{ counter-increment: p; font-size: 3.75mm; line-height: 1.4; color: #e9e9e9; padding-left: 8.5mm; position: relative }}
ol.passos li::before {{ content: counter(p); position: absolute; left: 0; top: .2mm; width: 6mm; height: 6mm; border-radius: 50%;
  background: #ffd23a; color: #111; font-weight: 800; font-size: 3.6mm; text-align: center; line-height: 6mm }}
ol.passos b {{ color: #fff }}
img.cel {{ width: 50mm; height: 100%; object-fit: cover; object-position: top; border-radius: 4.5mm;
  border: 1.4mm solid #000; outline: .5mm solid #8a8a8a }}
.qrs {{ flex: 1; display: flex; flex-direction: column; gap: 4mm; justify-content: center }}
.qrc {{ display: flex; flex-direction: column; align-items: center; gap: 1.6mm; text-align: center }}
.qrc .qr {{ width: 31mm; height: 31mm; background: #fff; padding: 2.2mm; border-radius: 1.6mm; display: block }}
.qrc small {{ font-size: 3mm; font-weight: 800; color: #ffd23a; letter-spacing: .25mm; text-transform: uppercase }}
.qrc span {{ font-size: 3.4mm; color: #e9e9e9; line-height: 1.35 }}
.qrc b {{ color: #fff }}

/* Resultados */
.numeros {{ display: flex; justify-content: center; gap: 7mm; margin: 7mm 7mm 0 }}
.num {{ flex: 1; text-align: center; background: rgba(255,255,255,.35); border-radius: 2mm; padding: 2.8mm 2mm }}
.num strong {{ display: block; font-size: 9mm; font-weight: 800; color: #0b0b0b; line-height: 1.05 }}
.num span {{ font-size: 3.2mm; font-weight: 600; color: #222 }}
.nota {{ text-align: center; font-size: 3.2mm; color: #262626; margin-top: 2.2mm; padding: 0 12mm; line-height: 1.4 }}

/* Rodapé: grupo, logo e orientador */
.grupo-tit {{ text-align: center; font-size: 10.5mm; margin-top: 3mm; color: #0b0b0b }}
.rodape {{ position: absolute; left: 4mm; right: 4mm; bottom: 9mm; height: 47mm; display: flex; align-items: flex-end }}
.logo-proj {{ width: 53mm; height: 44mm; display: flex; align-items: center; justify-content: center; padding: 3mm }}
.emblema {{ width: 100%; height: 100% }}
.nomes {{ position: absolute; left: 68mm; right: 68mm; bottom: 0; height: 47mm; display: flex; flex-direction: column;
  justify-content: center; align-items: center; gap: 1.6mm; padding: 3mm }}
.nomes p {{ font-size: 4.3mm; font-weight: 700; text-align: center }}
.orient {{ position: absolute; right: 4mm; bottom: 2.6mm; font-size: 4.2mm; font-weight: 800; color: #0b0b0b }}
.pim {{ position: absolute; right: 4mm; bottom: 26mm; width: 58mm; text-align: right; font-size: 3.6mm; line-height: 1.45;
  font-weight: 700; color: #262626 }}
"""


def poster():
    nomes = "".join(f"<p>{n}</p>" for n in INTEGRANTES)
    return f"""<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@600;700;800&family=Roboto:wght@700&display=block">
<style>{CSS}</style><body><div class="pag">
<header>{LOGO_UNIP}<div class="inst">Universidade Paulista - UNIP<br>Instituto de Ciências Exatas - ICET<br>
Curso Superior de Tecnologia em<br>Automação Industrial | Campus Sorocaba</div></header>

<div class="titulo quadro"><h1>Solar Smart Tower</h1></div>
<p class="sub">Torre solar com rastreamento automático para carga de telefones celulares</p>

<section class="descricao quadro"><h2>Descrição do projeto</h2>
<p>Torre que capta energia com um <b>painel solar de 10 W</b>, guarda a carga em uma <b>bateria de 12 V</b> e
oferece <b>duas saídas USB</b> para carregar celulares. Um rastreador de dois eixos — <b>ESP32</b>, quatro sensores
<b>LDR</b> em cruz e dois servomotores <b>MG996R</b> — mantém o painel voltado para a região de maior luz. A estrutura
foi modelada em CAD e impressa em 3D, e o mesmo programa do ESP32 roda em um <b>simulador 3D</b> que validou o
rastreamento ao longo do ano antes e depois da montagem.</p></section>

<div class="telas">
 <section class="tela quadro"><h2>Como funciona</h2>
  <div class="foto"><img src="{FOTO}" alt="Torre montada">
  <ol class="passos">
   <li><b>Sentir:</b> os 4 LDRs em cruz comparam a luz de cima, de baixo, da esquerda e da direita.</li>
   <li><b>Decidir:</b> a cada 100 ms o ESP32 calcula a diferença; dentro da zona morta, não mexe.</li>
   <li><b>Mover:</b> os 2 servos giram o painel para o lado mais claro, entre 20° e 160°.</li>
   <li><b>Descansar:</b> à noite o painel estaciona em 90°/90° e volta a seguir o Sol de manhã.</li>
  </ol></div></section>
 <section class="tela quadro"><h2>Controle pelo celular</h2>
  <div class="foto"><img class="cel" src="{IHM}" alt="Interface no celular">
  <div class="qrs">
   <div class="qrc"><small>1 · Conecte-se</small>{qr_svg(QR_WIFI).replace('#0b2a5b', '#111')}
    <span>Rede <b>{REDE}</b><br>Senha <b>{SENHA}</b></span></div>
   <div class="qrc"><small>2 · Abra a interface</small>{qr_svg(QR_URL).replace('#0b2a5b', '#111')}
    <span><b>http://{IP}</b></span></div>
  </div></div></section>
</div>

<div class="numeros">
 <div class="num"><strong>2 eixos</strong><span>4 LDRs · 2 servos MG996R</span></div>
 <div class="num"><strong>+47%</strong><span>energia no ano (simulação)*</span></div>
 <div class="num"><strong>2 USB</strong><span>carga de celulares (5 V)</span></div>
 <div class="num"><strong>R$ 442,03</strong><span>custo do protótipo</span></div>
</div>
<p class="nota">* Simulação do ano inteiro em São Paulo, céu limpo, em relação a uma placa fixa voltada ao Norte.
Conclusão: nesse porte, duas placas fixas (Leste e Oeste) rendem mais e custam menos que o rastreador.</p>

<h2 class="grupo-tit">Componentes do Grupo</h2>
<div class="rodape">
 <div class="logo-proj quadro">{LOGO_PROJ}</div>
 <div class="nomes quadro">{nomes}</div>
 <p class="pim">Projeto Integrado<br>Multidisciplinar — PIM II<br>Sorocaba/SP · 2026</p>
</div>
<p class="orient">Orientador: {ORIENTADOR}</p>
</div></body></html>"""


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    pdf = SAIDA / "poster_unip_A3.pdf"
    imprimir(poster(), pdf)
    with pymupdf.open(pdf) as doc:
        print("páginas:", len(doc))
        doc[0].get_pixmap(dpi=150).save(SAIDA / "poster_unip.png")
        a4 = pymupdf.open()
        a4.new_page(width=210 / 25.4 * 72, height=297 / 25.4 * 72).show_pdf_page(pymupdf.Rect(0, 0, 210 / 25.4 * 72, 297 / 25.4 * 72), doc, 0)
        a4.save(SAIDA / "poster_unip_A4.pdf", garbage=3, deflate=True)
    for f in (pdf, SAIDA / "poster_unip_A4.pdf", SAIDA / "poster_unip.png"):
        print(f.relative_to(RAIZ), f"{f.stat().st_size / 1024:.0f} kB")


if __name__ == "__main__":
    main()
