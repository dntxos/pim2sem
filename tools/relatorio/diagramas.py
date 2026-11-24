"""Diagramas do relatório: blocos do sistema, fluxograma do firmware, linha do tempo do
desenvolvimento, esquemático elétrico e proposta de leiaute da PCI.

Uso: python tools/relatorio/diagramas.py   (requer graphviz `dot`, matplotlib, schemdraw)
"""
import os
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FIG = os.path.join(RAIZ, 'docs', 'relatorio', 'figuras')
FONTE = 'Times New Roman'


def dot(nome, fonte):
    caminho = os.path.join(FIG, nome)
    subprocess.run(['dot', '-Tpng', '-Gdpi=300', '-o', caminho], input=fonte.encode(), check=True)
    print('ok', nome)


def blocos():
    dot('d_blocos.png', f'''
digraph G {{
  rankdir=LR; splines=ortho; nodesep=0.35; ranksep=0.55;
  node [shape=box, style="rounded,filled", fontname="{FONTE}", fontsize=13, penwidth=1.3, color="#1f4e8c", fillcolor="#eef3fa", margin="0.18,0.10"];
  edge [color="#374151", penwidth=1.4, fontname="{FONTE}", fontsize=11, arrowsize=0.8];
  subgraph cluster_e {{ label="Captação e armazenamento"; fontname="{FONTE}"; fontsize=14; color="#9ca3af"; style="rounded,dashed";
    painel [label="Painel fotovoltaico\\n10 W (≈18 V)", fillcolor="#fff7e6", color="#d9822b"];
    ctrl [label="Controlador de carga\\nPWM 12 V\\n(planejado)", style="rounded,dashed,filled", fillcolor="#ffffff"];
    bat [label="Bateria selada\\n12 V", fillcolor="#e7f3ec", color="#2e7d4f"];
    fus [label="Fusível\\n(planejado)", style="rounded,dashed,filled", fillcolor="#ffffff"];
  }}
  subgraph cluster_u {{ label="Carga de celulares"; fontname="{FONTE}"; fontsize=14; color="#9ca3af"; style="rounded,dashed";
    usbc [label="Conversor 12 V → 5 V\\n(planejado)", style="rounded,dashed,filled", fillcolor="#ffffff"];
    usb1 [label="Saída USB 1", style="rounded,dashed,filled", fillcolor="#ffffff"];
    usb2 [label="Saída USB 2", style="rounded,dashed,filled", fillcolor="#ffffff"];
  }}
  subgraph cluster_r {{ label="Rastreamento solar"; fontname="{FONTE}"; fontsize=14; color="#9ca3af"; style="rounded,dashed";
    x2 [label="XL4015 #2\\n6 V"]; x1 [label="XL4015 #1\\n6,0 V"];
    nano [label="ESP32\\n(Wi-Fi + ADC 12 bits)", fillcolor="#1f4e8c", fontcolor="white"];
    cel [label="Celular\\nrede SOLAR_TOWER\\n192.168.4.1", fillcolor="#fff7e6", color="#d9822b"];
    ldr [label="4 × LDR + 10 kΩ\\n(cruz de sombra)"];
    sh [label="Servo MG996R\\nhorizontal (GPIO 18)"]; sv [label="Servo MG996R\\nvertical (GPIO 19)"];
  }}
  painel -> ctrl -> bat -> fus;
  fus -> usbc; usbc -> usb1; usbc -> usb2;
  fus -> x2; x2 -> nano [xlabel="6 V"];
  cel -> nano [dir=both, style=dashed, color="#d9822b", xlabel="Wi-Fi"];
  fus -> x1; x1 -> sh; x1 -> sv;
  ldr -> nano [xlabel="GPIO 32–35"];
  nano -> sh [xlabel="PWM"]; nano -> sv;
  sh -> painel [style=dashed, color="#d9822b", xlabel="orienta"];
}}''')


def fluxograma():
    dot('d_fluxograma.png', f'''
digraph F {{
  node [fontname="{FONTE}", fontsize=12, style=filled, fillcolor="#eef3fa", color="#1f4e8c", penwidth=1.2];
  edge [fontname="{FONTE}", fontsize=11, color="#374151", arrowsize=0.8];
  ini [label="Início", shape=oval, fillcolor="#1f4e8c", fontcolor=white];
  set [label="setup(): ADC 12 bits, servos GPIO 18/19 em 90°/90°\\nWi-Fi SOLAR_TOWER (192.168.4.1) + servidor web", shape=box];
  web [label="server.handleClient()\\n(comandos do celular: modo, mover, posição inicial)", shape=box, fillcolor="#fff7e6", color="#d9822b"];
  t100 [label="Passaram 100 ms?", shape=diamond];
  noite [label="Lê LDRs; média < 500 por 120 s → repouso (20°/90°)\\nmédia > 700 por 30 s → sai do repouso", shape=box];
  auto [label="Modo automático\\ne fora do repouso?", shape=diamond];
  med [label="esquerda, direita, superior, inferior\\n(médias dos 4 LDRs)", shape=box];
  dh [label="diferença > TOLERANCIA?", shape=diamond];
  mov [label="move 2° na direção do lado mais claro\\n(cada eixo), limita a 20°–160°, servo.write()", shape=box];
  fim [label="fim do ciclo\\n(volta ao loop)", shape=box, style="rounded,filled", fillcolor="#f3f4f6", color="#9ca3af"];
  ini -> set -> web -> t100;
  t100 -> noite [label=" sim"]; t100 -> fim [label=" não"];
  noite -> auto; auto -> med [label=" sim"]; auto -> fim [label=" não"];
  med -> dh; dh -> mov [label=" sim"]; dh -> fim [label=" não"];
  mov -> fim; fim -> web [constraint=false, color="#9ca3af"];
}}''')


def linha_do_tempo():
    eventos = [
        ('Análise do código (Nano)', 'Pinos A1–A4 no código × A0–A3 no diagrama (P1)', 'encerrado'),
        ('Estimativa × medição', 'Laço estimado em 150 ms; medido no emulador: ~100 ms', 'corrigido'),
        ('Simulador 3D', 'Firmware real sobre as peças do CAD', 'acerto'),
        ('Simulador 3D', 'Inversão do eixo horizontal abaixo de 90° (P10)', 'corrigido'),
        ('Método de teste', 'Testes contaminados: firmware não reiniciado entre cenários', 'corrigido'),
        ('Simulação de 1 dia', 'Sombra do painel nos LDRs: placa foge do Sol em junho (P13)', 'proposta'),
        ('Simulação noturna', 'Placa amanhecia voltada a Oeste (P7)', 'corrigido'),
        ('Montagem física', 'Encaixe dos braços na peça da placa quebrou — reimpressa', 'corrigido'),
        ('Testes físicos', 'Migração para ESP32: Wi-Fi e controle pelo celular', 'acerto'),
        ('Simulador × ESP32', 'Correção P10 perdida na migração — restaurada no main.c', 'corrigido'),
        ('Simulador × ESP32', 'TOLERANCIA não escalada para ADC de 12 bits (P14) — 40 → 160', 'corrigido'),
        ('Teste com lanterna', 'Rastreamento reage, mas gira para o lado contrário', 'registrado'),
        ('IHM no celular', 'Nova IHM: 4 LDRs, diferença entre lados, gráfico e controle', 'acerto'),
        ('Simulação do ano', 'Preso em H = 20° nas manhãs de inverno (P15) — repouso em 90°', 'corrigido'),
        ('Consulta ao mercado', 'Duas placas fixas Leste/Oeste compensam mais que o rastreador', 'conclusao'),
    ]
    cores = {'corrigido': '#2e7d4f', 'registrado': '#b23a3a', 'conclusao': '#0b2a5b', 'proposta': '#d9822b', 'acerto': '#1f4e8c', 'encerrado': '#6b7280'}
    rot = {'corrigido': 'Corrigido', 'registrado': 'Registrado', 'conclusao': 'Conclusão', 'proposta': 'Solução proposta', 'acerto': 'Acerto', 'encerrado': 'Encerrado'}
    fig, ax = plt.subplots(figsize=(10.5, 8.6))
    plt.rcParams['font.family'] = 'serif'
    n = len(eventos)
    ax.plot([0.08, 0.08], [0.3, n + 0.2], color='#9ca3af', lw=2, zorder=0)
    for i, (etapa, txt, st) in enumerate(eventos):
        y = n - i
        ax.add_patch(Circle((0.08, y), 0.16, color=cores[st], zorder=2))
        ax.text(0.08, y, str(i + 1), color='white', ha='center', va='center', fontsize=9, fontweight='bold', zorder=3, family='serif')
        ax.text(0.32, y + 0.17, etapa.upper(), fontsize=8.5, color='#6b7280', va='center', family='serif')
        ax.text(0.32, y - 0.17, txt, fontsize=11, va='center', family='serif')
        ax.add_patch(FancyBboxPatch((9.05, y - 0.2), 1.35, 0.4, boxstyle='round,pad=0.02,rounding_size=0.15', color=cores[st]))
        ax.text(9.725, y, rot[st], color='white', fontsize=8.5, ha='center', va='center', family='serif')
    ax.set_xlim(-0.2, 10.5)
    ax.set_ylim(0.2, n + 0.7)
    ax.axis('off')
    fig.savefig(os.path.join(FIG, 'd_linha_do_tempo.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print('ok d_linha_do_tempo.png')


def esquematico():
    import schemdraw
    import schemdraw.elements as elm
    schemdraw.config(fontsize=11, font='serif', lw=1.3)
    V = '#b23a3a'

    def rede(d, ponto, nome, direcao='right', cor='black'):
        d += elm.Line().at(ponto).length(0.9).theta({'right': 0, 'left': 180, 'down': 270, 'up': 90}[direcao])
        d += elm.Dot(open=True)
        d += elm.Label().label(nome, loc={'right': 'right', 'left': 'left', 'down': 'bottom', 'up': 'top'}[direcao], color=cor)

    with schemdraw.Drawing(file=os.path.join(FIG, 'd_esquematico.png'), dpi=300, show=False) as d:
        # --- controlador
        nano = elm.Ic(pins=[
            elm.IcPin(name='5V', side='left', slot='3/3'), elm.IcPin(name='3V3', side='left', slot='2/3'),
            elm.IcPin(name='GND', side='left', slot='1/3'),
            elm.IcPin(name='IO34', side='right', slot='6/6'), elm.IcPin(name='IO35', side='right', slot='5/6'),
            elm.IcPin(name='IO32', side='right', slot='4/6'), elm.IcPin(name='IO33', side='right', slot='3/6'),
            elm.IcPin(name='IO18', side='right', slot='2/6'), elm.IcPin(name='IO19', side='right', slot='1/6'),
        ], size=(3.2, 5.4)).theta(0).at((0, 0))
        d += nano
        d += elm.Label().at((1.6, 5.9)).label('U1 — ESP32 (placa de desenvolvimento)', fontsize=11)
        rede(d, nano['5V'], '+6 V placa', 'left', V)
        rede(d, nano['3V3'], '+3,3 V', 'left', V)
        rede(d, nano.GND, 'GND', 'left')
        for p in ('IO34', 'IO35', 'IO32', 'IO33', 'IO18', 'IO19'):
            rede(d, nano[p], p)

        # --- divisores dos LDRs
        for i, (nome, net) in enumerate((('SE', 'IO34'), ('SD', 'IO35'), ('IE', 'IO32'), ('ID', 'IO33'))):
            x = 7.5 + i * 2.6
            d += elm.Vdd().at((x, 6.2)).label('+3,3 V', color=V)
            d += elm.Photoresistor().down().label(f'LDR\n{nome}', loc='bottom', ofst=0.2)
            no = d.here
            d += elm.Dot()
            d += elm.Line().right(0.7)
            d += elm.Dot(open=True)
            d += elm.Label().label(net, loc='right')
            d += elm.Resistor().at(no).down().label(f'R{i + 1}\n10 kΩ', loc='bottom', ofst=0.2)
            d += elm.Ground()
        d += elm.Label().at((11.4, 7.6)).label('Sensores: divisor LDR + 10 kΩ (mais luz → tensão maior)', fontsize=10)

        # --- servos
        for i, (nome, net) in enumerate((('M1 — servo horizontal (azimute)', 'IO18'), ('M2 — servo vertical (elevação)', 'IO19'))):
            y = -3.6 - i * 2.4
            sv = elm.Ic(pins=[elm.IcPin(name='S', side='left', slot='3/3'), elm.IcPin(name='+', side='left', slot='2/3'),
                              elm.IcPin(name='−', side='left', slot='1/3')],
                        size=(1.8, 1.8), label='MG996R', lblsize=10).theta(0).at((10.5, y))
            d += sv
            rede(d, sv.S, net, 'left')
            rede(d, sv['+'], '+6 V', 'left', V)
            rede(d, sv['−'], 'GND', 'left')
            d += elm.Label().at((12.8, y + 1.3)).label(nome, halign='left', fontsize=10)

        # --- alimentação
        d += elm.Battery().at((-9, -8)).up().label('BT1\n12 V', loc='bottom', ofst=0.3)
        topo = d.here
        d += elm.Fuse().right().at(topo).label('F1 3 A', loc='top')
        no12 = d.here
        d += elm.Dot()
        for j, (nome, saida) in enumerate((('XL4015 #1', '+6 V'), ('XL4015 #2', '+6 V placa'))):
            y = topo[1] - 0.8 - j * 3.2
            conv = elm.Ic(pins=[elm.IcPin(name='IN+', side='left', slot='2/2'), elm.IcPin(name='IN−', side='left', slot='1/2'),
                                elm.IcPin(name='OUT+', side='right', slot='2/2'), elm.IcPin(name='OUT−', side='right', slot='1/2')],
                          size=(3.4, 1.6)).theta(0).at((no12[0] + 1.6, y))
            d += elm.Label().at((no12[0] + 3.3, y + 2.0)).label(nome, fontsize=10)
            d += conv
            d += elm.Line().at(conv['IN+']).left().tox(no12[0])
            d += elm.Line().up().toy(no12[1])
            rede(d, conv['OUT+'], saida, 'right', V)
            rede(d, conv['IN−'], 'GND', 'left')
            rede(d, conv['OUT−'], 'GND', 'right')
        d += elm.Capacitor(polar=True).at((6.5, -9.0)).down().label('C1\n1000 µF', loc='bottom', ofst=0.25)
        d += elm.Ground()
        d += elm.Vdd().at((6.5, -9.0)).label('+6 V', color=V)
        d += elm.Line().at((-9, -8)).down(0.6)
        d += elm.Ground()
        d += elm.Label().at((-2.0, -13.4)).label('Todos os GND interligados. Divisores dos LDRs em 3,3 V (entradas do ESP32 não toleram 5 V). Ajustar os XL4015 antes de ligar.', fontsize=10)
    print('ok d_esquematico.png')


def pci():
    fig, ax = plt.subplots(figsize=(8, 6))
    W, H = 100, 70
    ax.add_patch(FancyBboxPatch((0, 0), W, H, boxstyle='round,pad=0,rounding_size=3', color='#1d5c3a'))
    for x, y in ((3.5, 3.5), (W - 3.5, 3.5), (3.5, H - 3.5), (W - 3.5, H - 3.5)):
        ax.add_patch(Circle((x, y), 1.6, color='#d9d9d9'))
        ax.add_patch(Circle((x, y), 0.9, color='#1d5c3a'))
    cobre = '#c99a3c'
    tela = 'white'

    def trilha(pts, larg=1.2, cor=cobre):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=cor, lw=larg * 3.2, solid_capstyle='round', solid_joinstyle='round', zorder=2)

    def pad(x, y, r=0.9, quad=False):
        if quad:
            ax.add_patch(Rectangle((x - r, y - r), 2 * r, 2 * r, color=cobre, zorder=3))
        else:
            ax.add_patch(Circle((x, y), r, color=cobre, zorder=3))
        ax.add_patch(Circle((x, y), r * 0.42, color='#1d5c3a', zorder=4))

    # ESP32 DevKit (2 x 15 pinos, passo 2,54, fileiras a 25,4 mm)
    nx, ny = 16, 16
    LARG = 25.4
    ax.add_patch(Rectangle((nx - 2.5, ny - 2.5), LARG + 5, 14 * 2.54 + 5, fill=False, ec=tela, lw=1.2, zorder=5))
    ax.text(nx + LARG / 2, ny + 17.8, 'U1\nESP32\nDEVKIT', color=tela, ha='center', va='center', fontsize=10, family='serif', zorder=5)
    for i in range(15):
        pad(nx, ny + i * 2.54, quad=(i == 0))
        pad(nx + LARG, ny + i * 2.54, quad=(i == 0))
    # resistores 10 kΩ (R1–R4) e conectores dos LDRs (J1–J4)
    for i in range(4):
        y = ny + 6 + i * 6.5
        pad(54, y); pad(64.16, y)
        ax.add_patch(Rectangle((56, y - 1.1), 6.2, 2.2, fill=False, ec=tela, lw=1, zorder=5))
        ax.text(59.1, y + 2.0, f'R{i + 1} 10k', color=tela, ha='center', fontsize=7.5, family='serif', zorder=5)
        pad(76, y, quad=True); pad(78.54, y)
        ax.add_patch(Rectangle((74.4, y - 1.6), 5.8, 3.2, fill=False, ec=tela, lw=1, zorder=5))
        ax.text(82, y, f'J{i + 1} LDR {["SE", "SD", "IE", "ID"][i]}', color=tela, va='center', fontsize=7.5, family='serif', zorder=5)
        trilha([(nx + LARG, ny + (11 - i) * 2.54), (50, ny + (11 - i) * 2.54), (50, y), (54, y)], 0.5)
        trilha([(64.16, y), (76, y)], 0.5)
    # servos (J5, J6): sinal, +6 V, GND
    for j, (x, nome, pino) in enumerate(((10, 'J5 SERVO H', 12), (10, 'J6 SERVO V', 13))):
        y = 53 + j * 7
        for k in range(3):
            pad(x - 6 + k * 2.54, y, quad=(k == 0))
        ax.text(x - 6, y + 2.4, nome, color=tela, fontsize=7.5, family='serif', zorder=5)
        trilha([(x - 6, y), (x - 6, y - 3), (nx, y - 3), (nx, ny + pino * 2.54)], 0.5)
    # bornes de alimentação
    for x, nome in ((10, 'J7 +6V SERVOS'), (26, 'J8 +6V ESP32')):
        ax.add_patch(Rectangle((x - 3, 2.5), 10, 6, fill=False, ec=tela, lw=1.2, zorder=5))
        pad(x, 5.5, 1.3, quad=True); pad(x + 5, 5.5, 1.3)
        ax.text(x + 2.5, 10, nome, color=tela, ha='center', fontsize=7.5, family='serif', zorder=5)
    trilha([(10, 5.5), (4.5, 5.5), (4.5, 50), (6.54, 50), (6.54, 53)], 1.6)
    trilha([(26, 5.5), (26, 10), (nx, 10), (nx, ny)], 1.0)
    # capacitor dos servos
    ax.add_patch(Circle((46, 7), 4, fill=False, ec=tela, lw=1.2, zorder=5))
    ax.text(46, 7, 'C1\n1000 µF', color=tela, ha='center', va='center', fontsize=7, family='serif', zorder=5)
    pad(44, 7); pad(48, 7)
    # plano de terra (contorno)
    ax.text(W / 2, H - 4.5, 'PCI DO RASTREADOR — PROPOSTA DE LEIAUTE (FACE INFERIOR)', color=tela, ha='center', fontsize=9, family='serif', zorder=5)
    ax.text(W - 4, 2, '100 × 70 mm', color=tela, ha='right', fontsize=7.5, family='serif', zorder=5)
    ax.set_xlim(-2, W + 2)
    ax.set_ylim(-2, H + 2)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.savefig(os.path.join(FIG, 'd_pci.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('ok d_pci.png')


if __name__ == '__main__':
    os.makedirs(FIG, exist_ok=True)
    blocos()
    fluxograma()
    linha_do_tempo()
    pci()
    esquematico()
