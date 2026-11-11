"""Gera os gráficos do relatório a partir dos dados do simulador (docs/relatorio/dados/*.json).

Uso: python tools/relatorio/graficos.py   (requer matplotlib e numpy)
Todos os resultados são de SIMULAÇÃO (firmware real emulado + modelo óptico dos LDRs).
"""
import json
import math
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DADOS = os.path.join(RAIZ, 'docs', 'relatorio', 'dados')
FIG = os.path.join(RAIZ, 'docs', 'relatorio', 'figuras')

AZUL = '#1f4e8c'
LARANJA = '#d9822b'
VERDE = '#2e7d4f'
VERMELHO = '#b23a3a'
CINZA = '#6b7280'

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.color': '#e5e7eb',
    'grid.linewidth': 0.8,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'legend.frameon': False,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})


def carregar(nome):
    d = json.load(open(os.path.join(DADOS, nome)))
    cols = d.pop('cols')
    return {k: {c: np.array([r[i] for r in v]) for i, c in enumerate(cols)} for k, v in d.items()}


def salvar(fig, nome):
    fig.savefig(os.path.join(FIG, nome))
    plt.close(fig)
    print('ok', nome)


def g_p10():
    d = carregar('p10_se.json')
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    for k, cor, rot in (('antigo', VERMELHO, 'Firmware original'), ('novo', AZUL, 'Firmware corrigido')):
        ax[0].plot(d[k]['t'], d[k]['erro'], color=cor, lw=2, label=rot)
        ax[1].plot(d[k]['t'], d[k]['H'], color=cor, lw=2, label=f'{rot} – horizontal')
        ax[1].plot(d[k]['t'], d[k]['V'], color=cor, lw=1.4, ls='--', label=f'{rot} – vertical')
    ax[0].set(xlabel='Tempo (s)', ylabel='Erro de apontamento (°)', title='Erro de apontamento', ylim=(0, 100))
    ax[1].set(xlabel='Tempo (s)', ylabel='Ângulo do servo (°)', title='Ângulos comandados', ylim=(0, 180))
    ax[1].axhline(160, color=CINZA, lw=0.8, ls=':')
    ax[1].axhline(20, color=CINZA, lw=0.8, ls=':')
    ax[0].legend()
    ax[1].legend(fontsize=8, loc='lower left')
    fig.tight_layout()
    salvar(fig, 'g_p10_inversao.png')


def g_dia(nome_cad, nome_elev, titulo, arquivo):
    cad = carregar(nome_cad)['novo']
    elev = carregar(nome_elev)['novo']
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    ax[0].plot(cad['hora'], cad['erro'], color=VERMELHO, lw=2, label='Geometria do CAD')
    ax[0].plot(elev['hora'], elev['erro'], color=AZUL, lw=2, label='LDRs elevados 25 mm')
    ax[0].set(xlabel='Hora solar (h)', ylabel='Erro de apontamento (°)', title='Erro ao longo do dia', ylim=(0, 120))
    ax[0].legend()
    ax[1].plot(cad['hora'], cad['eFixa'], color=CINZA, lw=2, label='Placa fixa (Norte, 23,5°)')
    ax[1].plot(cad['hora'], cad['eTrack'], color=VERMELHO, lw=2, label='Rastreador – CAD')
    ax[1].plot(elev['hora'], elev['eTrack'], color=AZUL, lw=2, label='Rastreador – LDRs elevados')
    ax[1].set(xlabel='Hora solar (h)', ylabel='Energia acumulada (u.r.)', title='Energia captada')
    ax[1].legend(fontsize=9)
    fig.suptitle(titulo, fontsize=11, y=1.02)
    fig.tight_layout()
    salvar(fig, arquivo)


def g_noite():
    d = carregar('noite_elev25.json')
    c, r = d['continuo'], d['reset']
    manha = c['hora'] < 12
    manha &= c['hora'] > 6.5
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.plot(c['hora'][manha], c['erro'][manha], color=VERMELHO, lw=2, label='Sem retorno noturno (placa amanhece voltada a Oeste)')
    ax.plot(r['hora'], r['erro'], color=AZUL, lw=2, label='Com retorno à posição inicial (90°/90°)')
    ax.set(xlabel='Hora solar (h)', ylabel='Erro de apontamento (°)', ylim=(0, 120), xlim=(6.5, 11.2),
           title='Manhã de 21 de junho')
    ax.legend(fontsize=9)
    salvar(fig, 'g_noite.png')


def g_fiacao():
    d = carregar('fiacao.json')
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.plot(d['codigo']['t'], d['codigo']['erro'], color=AZUL, lw=2, label='LDRs em A1–A4 (como o código espera)')
    ax.plot(d['diagrama']['t'], d['diagrama']['erro'], color=VERMELHO, lw=2, label='LDRs em A0–A3 (como no diagrama)')
    ax.set(xlabel='Tempo após ligar (s)', ylabel='Erro de apontamento (°)', ylim=(0, 100))
    ax.legend(fontsize=9)
    salvar(fig, 'g_fiacao.png')


def g_ldr():
    lux = np.logspace(0, 5, 300)
    r = np.minimum(1e6, 15000 * (lux / 10) ** -0.7)
    v = 5 * 10000 / (r + 10000)
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.loglog(lux, r / 1000, color=LARANJA, lw=2)
    ax.set(xlabel='Iluminância (lux)', ylabel='Resistência do LDR (kΩ)')
    ax2 = ax.twinx()
    ax2.semilogx(lux, v, color=AZUL, lw=2)
    ax2.set_ylabel('Tensão na entrada analógica (V)', color=AZUL)
    ax2.spines['right'].set_visible(True)
    ax2.grid(False)
    ax.text(2, 300, 'R (LDR)', color=LARANJA)
    ax2.text(2000, 3.4, 'V no pino Ax', color=AZUL)
    ax2.axvspan(5000, 1e5, color=CINZA, alpha=0.12)
    ax2.text(7000, 1.0, 'saturação\n(sol pleno)', color=CINZA, fontsize=9)
    salvar(fig, 'g_ldr.png')


def g_cos():
    th = np.linspace(0, 90, 200)
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.plot(th, 100 * np.cos(np.radians(th)), color=AZUL, lw=2)
    for a in (10, 18, 30, 60):
        y = 100 * math.cos(math.radians(a))
        ax.plot([a], [y], 'o', color=LARANJA)
        ax.annotate(f'{a}° → {y:.0f} %', (a, y), textcoords='offset points', xytext=(6, 4), fontsize=9)
    ax.set(xlabel='Ângulo entre o sol e a normal do painel θ (°)', ylabel='Potência relativa (%)', ylim=(0, 105))
    salvar(fig, 'g_cos.png')


def g_resumo_energia():
    casos = [
        ('Jun – CAD', carregar('dia172.json')['novo']),
        ('Jun – LDRs\nelevados', carregar('dia172_elev25.json')['novo']),
        ('Dez – CAD', carregar('dia355.json')['novo']),
        ('Dez – LDRs\nelevados', carregar('dia355_elev25.json')['novo']),
    ]
    nomes = [c[0] for c in casos]
    fixa = [c[1]['eFixa'][-1] for c in casos]
    track = [c[1]['eTrack'][-1] for c in casos]
    x = np.arange(len(casos))
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.bar(x - 0.2, fixa, 0.38, color=CINZA, label='Placa fixa')
    ax.bar(x + 0.2, track, 0.38, color=AZUL, label='Rastreador')
    for i, (f, t) in enumerate(zip(fixa, track)):
        g = (t / f - 1) * 100
        ax.text(i + 0.2, t + 0.15, f'{g:+.0f} %', ha='center', fontsize=9, color=VERDE if g > 0 else VERMELHO)
    ax.set_xticks(x, nomes)
    ax.set(ylabel='Energia no dia (u.r.)')
    ax.legend()
    salvar(fig, 'g_energia_resumo.png')
    return {n.replace('\n', ' '): (f, t) for n, f, t in zip(nomes, fixa, track)}


if __name__ == '__main__':
    os.makedirs(FIG, exist_ok=True)
    g_p10()
    g_dia('dia172.json', 'dia172_elev25.json', '21 de junho (solstício de inverno), latitude −23,55°', 'g_dia_junho.png')
    g_dia('dia355.json', 'dia355_elev25.json', '21 de dezembro (solstício de verão), latitude −23,55°', 'g_dia_dezembro.png')
    g_noite()
    g_fiacao()
    g_ldr()
    g_cos()
    print(g_resumo_energia())


# ============================================================ ESP32 (main.c atual e variantes)
ROTULOS_FW = {
    'esp32': 'main.c dos testes físicos',
    'esp32:esp32_tol160': '+ tolerância 160',
    'esp32:esp32_tol160_p10': '+ tolerância 160 + P10 (main.c atual)',
}
CORES_FW = {'esp32': VERMELHO, 'esp32:esp32_tol160': LARANJA, 'esp32:esp32_tol160_p10': AZUL}


def g_esp32():
    d = json.load(open(os.path.join(DADOS, 'esp32_cenarios_elev25.json')))
    cols = d.pop('cols')
    fws = list(ROTULOS_FW)
    fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.5))
    cen = [('SE', 'Sol a SE\n40°'), ('SO', 'Sol a SO\n35°'), ('NE', 'Sol a NE\n30°')]
    x = np.arange(len(cen))
    for k, fw in enumerate(fws):
        v = [d[f'{fw}|{c}'][-1][cols.index('erro')] for c, _ in cen]
        b = ax[0].bar(x + (k - 1) * 0.26, v, 0.25, color=CORES_FW[fw], label=ROTULOS_FW[fw])
        ax[0].bar_label(b, fmt='%.0f°', fontsize=8, padding=1)
    ax[0].set_xticks(x, [r for _, r in cen])
    ax[0].set(ylabel='Erro de apontamento final (°)', title='Posições fixas do Sol (8 s)', ylim=(0, 72))
    ax[0].legend(fontsize=8, loc='upper right')
    dias = [('jun', '21 de junho'), ('dez', '21 de dezembro')]
    x = np.arange(len(dias))
    fixa = [d[f'esp32|{c}'][-1][cols.index('eFixa')] for c, _ in dias]
    ax[1].bar(x - 0.39, fixa, 0.19, color=CINZA, label='Placa fixa')
    for k, fw in enumerate(fws):
        v = [d[f'{fw}|{c}'][-1][cols.index('eTrack')] for c, _ in dias]
        b = ax[1].bar(x + (k - 1) * 0.2 + 0.0, v, 0.19, color=CORES_FW[fw])
        ganhos = [f'{(e / f - 1) * 100:+.0f}%' for e, f in zip(v, fixa)]
        ax[1].bar_label(b, labels=ganhos, fontsize=7.5, padding=1)
    ax[1].set_xticks(x, [r for _, r in dias])
    ax[1].set(ylabel='Energia no dia (u.r.)', title='Dias completos (latitude −23,55°)', ylim=(0, 13))
    ax[1].legend(fontsize=8, loc='upper left')
    fig.tight_layout()
    salvar(fig, 'g_esp32.png')


def g_noite_esp32():
    d = json.load(open(os.path.join(DADOS, 'noite_esp32_vs_nano_dez.json')))
    cols = d.pop('cols')
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    for k, cor, rot in (('nano', VERMELHO, 'Nano (sem repouso noturno): amanhece voltado a Oeste'),
                        ('esp32', AZUL, 'ESP32 (com repouso noturno em 20°/90°)')):
        s = [r for r in d[k] if r[0] != 'tarde' and r[0] != 'noite (140 s)']
        ax.plot([r[1] for r in s], [r[4] for r in s], color=cor, lw=2, marker='o', ms=3, label=rot)
    ax.set(xlabel='Hora solar (h)', ylabel='Erro de apontamento (°)', ylim=(0, 140), xlim=(5.2, 10.9),
           title='Amanhecer de 21 de dezembro após uma noite')
    ax.legend(fontsize=8.5)
    salvar(fig, 'g_noite_esp32.png')


if __name__ == '__main__':
    g_esp32()
    g_noite_esp32()
