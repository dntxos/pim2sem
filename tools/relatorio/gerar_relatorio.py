"""Gera o relatório do PIM II — versão 4 (docs/relatorio/PIM_Torre_Solar_v4.docx).
v3: correções P10 e P14 aplicadas ao main.c do ESP32. v4: dados do grupo (orientador, custos,
XL4015 em 6 V, peça reimpressa, teste com lanterna).

Uso: python tools/relatorio/gerar_relatorio.py   (requer python-docx)
Antes: tools/relatorio/graficos.py, diagramas.py, fotos.py e tools/render/gerar_figuras_relatorio.sh.
Os resultados numéricos citados no texto são lidos de docs/relatorio/dados/ (simulação).
Limite combinado com o grupo: no máximo 40 páginas (conferir com exportar_pdf.sh).
A versão 1 (fase do Arduino Nano) é gerada por gerar_relatorio_v1.py.
"""
import json
import os
import sys

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm

sys.path.insert(0, os.path.dirname(__file__))
from abnt_docx import Relatorio  # noqa: E402

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FIG = os.path.join(RAIZ, 'docs', 'relatorio', 'figuras')
DADOS = os.path.join(RAIZ, 'docs', 'relatorio', 'dados')
SAIDA = os.path.join(RAIZ, 'docs', 'relatorio', 'PIM_Torre_Solar_v4.docx')
C = WD_ALIGN_PARAGRAPH.CENTER


def f(nome):
    return os.path.join(FIG, nome)


def dados(nome):
    return json.load(open(os.path.join(DADOS, nome)))


def pct(e, fixa):
    return f'{(e / fixa - 1) * 100:+.0f}%'.replace('-', '−')


# ---------------------------------------------------------------- números (simulação)
cen = dados('esp32_cenarios_elev25.json')
COL = cen['cols']
fim = lambda k: cen[k][-1]  # noqa: E731
err = lambda k: round(fim(k)[COL.index('erro')])  # noqa: E731
eng = lambda k: pct(fim(k)[COL.index('eTrack')], fim(k)[COL.index('eFixa')])  # noqa: E731
ATUAL, TOL, TOLP10 = 'esp32', 'esp32:esp32_tol160', 'esp32:esp32_tol160_p10'
nano_p10 = dados('esp32_p10.json')
NANO_SE = round(nano_p10['nano_SE'][-1][3])
NANO_SO = round(nano_p10['nano_SO'][-1][3])
d172, d172e = dados('dia172.json')['novo'], dados('dia172_elev25.json')['novo']
P13_CAD = pct(d172[-1][7], d172[-1][8])
P13_ELEV = pct(d172e[-1][7], d172e[-1][8])
noite = dados('noite_esp32_vs_nano_dez.json')
ESP_ACORDA = next(r[1] for r in noite['esp32'] if r[0] == 'alvorada' and r[6] == 'ATIVO')
NANO_ALINHA = next(r[1] for r in noite['nano'] if r[0] == 'manhã' and r[4] < 20)
NANO_ERRO_INI = round(next(r[4] for r in noite['nano'] if r[0] == 'alvorada'))


def hora(h):
    hh = int(h)
    return f'{hh}h{round((h - hh) * 60):02d}'


TITULO = 'TORRE SOLAR COM RASTREAMENTO AUTOMÁTICO PARA CARGA DE TELEFONES CELULARES'
SUBTITULO = 'projeto, simulação, testes físicos e lições do desenvolvimento de um rastreador solar de dois eixos'
INTEGRANTES = [
    ('Ana Paula Dias Campos', 'H012GA1'),
    ('Dawid Felipe Fernandes da Silva', 'R296HE2'),
    ('Rafael Kazuo Sato Simião', 'H973724'),
    ('Samuel Bolfarini Pires', 'H954HJ-8'),
    ('Talita dos Santos', 'R453AG-6'),
]

r = Relatorio()

# =====================================================================  CAPA
r.p('**UNIVERSIDADE PAULISTA – UNIP**', alin=C, recuo=False)
r.p('**Campus Sorocaba**', alin=C, recuo=False)
r.espaco()
r.p('**Curso Superior de Tecnologia em Automação Industrial**', alin=C, recuo=False)
r.espaco(3)
for nome, ra in INTEGRANTES:
    r.p(f'**{nome} (RA: {ra})**', alin=C, recuo=False)
r.espaco(5)
r.p(f'**{TITULO}:**', alin=C, recuo=False)
r.p(SUBTITULO, alin=C, recuo=False)
r.espaco(9)
r.p('**Sorocaba/SP**', alin=C, recuo=False)
r.p('**2026**', alin=C, recuo=False)

# =====================================================================  FOLHA DE ROSTO
r.quebra()
for nome, _ in INTEGRANTES:
    r.p(f'**{nome}**', alin=C, recuo=False)
r.espaco(6)
r.p(f'**{TITULO}:**', alin=C, recuo=False)
r.p(SUBTITULO, alin=C, recuo=False)
r.espaco(2)
nat = r.p('Trabalho apresentado ao Curso Superior de Tecnologia em Automação Industrial da Universidade '
          'Paulista – UNIP, Campus Sorocaba, como requisito parcial para obtenção de nota na disciplina de '
          'Projeto Integrado Multidisciplinar (PIM II), sob orientação do Prof. Marcelo Bellodi.',
          recuo=False)
nat.paragraph_format.left_indent = Cm(8)
nat.paragraph_format.line_spacing_rule = 0
r.espaco(6)
r.p('**Sorocaba/SP**', alin=C, recuo=False)
r.p('**2026**', alin=C, recuo=False)

# =====================================================================  RESUMO / ABSTRACT
r.titulo_sem_numero('RESUMO')
r.p('Este trabalho apresenta o projeto, a simulação e os testes físicos de uma torre de captação de energia '
    'solar destinada à carga de telefones celulares, com ênfase no subsistema de rastreamento solar de dois '
    'eixos. O protótipo usa um painel fotovoltaico de 10 W, uma bateria de 12 V, conversores *step-down* '
    'XL4015, dois servomotores MG996R e quatro sensores LDR em cruz, sobre uma estrutura modelada em CAD e '
    'impressa em 3D. O controle começou em um Arduino Nano e, na etapa de testes físicos, migrou para um '
    'ESP32, que acrescentou rede Wi-Fi própria e controle pelo celular, além de um repouso noturno '
    'automático. Para validar o sistema antes e depois da montagem, o grupo desenvolveu um simulador '
    'tridimensional que executa o mesmo código-fonte do firmware — primeiro emulando o microcontrolador do '
    'Nano e, depois, compilando o programa do ESP32 para WebAssembly com um núcleo ESP32 simulado — sobre as '
    'peças reais, calculando a luz em cada sensor por *raycasting*. O relatório registra a trajetória do '
    'desenvolvimento, com erros e acertos: uma inversão no algoritmo do eixo horizontal, testes contaminados '
    'por estado interno, o sombreamento dos sensores pelo próprio painel, a quebra de uma peça impressa na '
    'montagem e duas falhas reintroduzidas na migração para o ESP32, detectadas pelo simulador e corrigidas. Nos testes '
    'físicos, a gravação do ESP32, a movimentação dos servos e o controle pelo celular funcionaram. Em '
    f'simulação, com as correções aplicadas, o rastreador capta {eng(TOLP10 + "|jun")} de energia em '
    f'relação a uma placa fixa no inverno e {eng(TOLP10 + "|dez")} no verão.', recuo=False)
r.espaco()
r.p('**Palavras-chave:** energia solar fotovoltaica; rastreador solar; ESP32; sensor LDR; simulação; automação.',
    recuo=False)

r.titulo_sem_numero('ABSTRACT')
r.p('This work presents the design, simulation and physical tests of a solar energy tower for charging '
    'mobile phones, focusing on its dual-axis solar tracking subsystem. The prototype uses a 10 W '
    'photovoltaic panel, a 12 V battery, XL4015 step-down converters, two MG996R servomotors and four LDR '
    'sensors arranged in a cross, on a 3D-printed structure. Control started on an Arduino Nano and, during '
    'the physical tests, moved to an ESP32, which added its own Wi-Fi network, phone control and an automatic '
    'night rest. To validate the system before and after assembly, the team built a three-dimensional '
    'simulator that runs the same firmware source code — first by emulating the Nano microcontroller and '
    'then by compiling the ESP32 program to WebAssembly with a simulated ESP32 core — over the real parts, '
    'computing the light on each sensor by ray casting. The report records the development path, including '
    'an inversion in the horizontal-axis algorithm, tests contaminated by internal state, sensor shading by '
    'the panel itself, a printed part that broke during assembly, and two faults reintroduced in the ESP32 '
    'migration that the simulator detected and that were then fixed. In the physical tests, ESP32 programming, '
    f'servo motion and phone control worked. In simulation, with the fixes applied, the tracker collects {eng(TOLP10 + "|jun")} '
    f'energy relative to a fixed panel in winter and {eng(TOLP10 + "|dez")} in summer.', recuo=False)
r.espaco()
r.p('**Keywords:** photovoltaic solar energy; solar tracker; ESP32; LDR sensor; simulation; automation.', recuo=False)

# =====================================================================  LISTAS
r.lista('LISTA DE ILUSTRAÇÕES', 'Figura')
r.listas('LISTA DE TABELAS E QUADROS', ['Tabela', 'Quadro'])
r.titulo_sem_numero('LISTA DE ABREVIATURAS E SIGLAS')
for s, d in [
    ('ADC', 'Conversor analógico-digital (*Analog-to-Digital Converter*)'),
    ('CAD', 'Desenho assistido por computador (*Computer-Aided Design*)'),
    ('CC', 'Corrente contínua'), ('GPIO', 'Entrada e saída de uso geral (*General Purpose Input/Output*)'),
    ('HTTP', 'Protocolo de transferência de hipertexto (*Hypertext Transfer Protocol*)'),
    ('LDR', 'Resistor dependente de luz (*Light Dependent Resistor*)'), ('PCI', 'Placa de circuito impresso'),
    ('PIM', 'Projeto Integrado Multidisciplinar'), ('PLA', 'Ácido polilático (filamento de impressão 3D)'),
    ('PWM', 'Modulação por largura de pulso (*Pulse Width Modulation*)'),
    ('STL', 'Formato de malha 3D (*Standard Triangle Language*)'), ('USB', 'Barramento serial universal'),
    ('u.r.', 'Unidade relativa (energia simulada, adimensional)'),
]:
    par = r.p(f'**{s}**\t{d}', recuo=False)
    par.paragraph_format.tab_stops.add_tab_stop(Cm(2.2))
r.sumario()

# =====================================================================  1 INTRODUÇÃO
r.iniciar_texto()
r.h1('1 INTRODUÇÃO')
r.ps(
    'A energia solar é a fonte renovável mais abundante no Brasil: a irradiação global horizontal média varia '
    'entre cerca de 4,4 e 6,2 kWh/m² por dia, valores superiores aos de países europeus que lideram o uso da '
    'tecnologia (Pereira *et al.*, 2017). Módulos fotovoltaicos convertem essa energia diretamente em '
    'eletricidade, sem partes móveis, o que os torna adequados a pequenos sistemas isolados da rede '
    '(Villalva; Gazoli, 2015). Um módulo, porém, só entrega sua potência nominal quando a radiação incide '
    'perpendicularmente; em uma instalação fixa a potência cai com o cosseno do ângulo de incidência ao longo '
    'do dia. Os rastreadores solares movimentam o painel para acompanhar o Sol, com ganhos relatados entre 10% '
    'e 100% conforme local, época e tipo de rastreador (Mousazadeh *et al.*, 2009).',
    'O tema do PIM II do Curso Superior de Tecnologia em Automação Industrial é uma torre que capte energia '
    'solar, armazene-a em uma bateria de 12 V e disponibilize duas saídas USB para carregar celulares, com o '
    'painel acompanhando a posição de maior luminosidade. Este relatório descreve o projeto do grupo, com '
    'ênfase no subsistema de rastreamento, e registra deliberadamente a **história do desenvolvimento** — as '
    'hipóteses que se confirmaram, as que estavam erradas e os problemas que só apareceram quando código, '
    'eletrônica e mecânica foram testados juntos, em simulação e na montagem física.',
)
r.h2('1.1 Objetivos')
r.p('**Objetivo geral:** desenvolver uma torre capaz de captar energia solar, armazená-la em bateria de 12 V e '
    'disponibilizá-la por duas portas USB, mantendo o painel orientado por um rastreador automático de dois eixos.')
r.p('**Objetivos específicos:**', recuo=False)
r.itens([
    'estudar a célula fotovoltaica e a influência da orientação do painel na energia captada;',
    'projetar a alimentação por bateria e conversores para servos, controlador e saídas USB;',
    'desenvolver o sensoriamento com LDRs e o firmware de controle, com operação automática e pelo celular;',
    'modelar e imprimir a estrutura em 3D e montar o protótipo;',
    'construir um simulador que execute o firmware real sobre a geometria real;',
    'identificar, documentar e corrigir as falhas, quantificando o efeito de cada correção.',
], marcador='a')
r.h2('1.2 Cronograma')
r.tabela('Cronograma de execução do projeto', ['Etapa', 'Atividade', 'Situação'], [
    ['1', 'Definição do tema e da arquitetura (torre, rastreador, carga USB)', 'Concluída'],
    ['2', 'Modelagem 3D (CAD), circuito e firmware iniciais (Arduino Nano, Tinkercad)', 'Concluída'],
    ['3', 'Compra dos componentes; simulador 3D; correção do algoritmo (P10)', 'Concluída'],
    ['4', 'Simulação de dias completos; diagnóstico do sombreamento (P13)', 'Concluída'],
    ['5', 'Impressão 3D, pré-montagem e testes dos servos', 'Concluída'],
    ['6', 'Migração para ESP32, interface no celular e repouso noturno', 'Concluída'],
    ['7', 'Simulação do firmware ESP32; correção das regressões P10 e P14', 'Concluída'],
    ['8', 'Controlador de carga, saídas USB e PCI', 'Planejada'],
], larguras=[1.5, 11.5, 3.0])

# =====================================================================  2 FUNDAMENTAÇÃO
r.h1('2 FUNDAMENTAÇÃO TEÓRICA')
r.h2('2.1 Energia fotovoltaica, grandezas elétricas e armazenamento')
r.ps(
    'A célula fotovoltaica é uma junção PN de semicondutor, em geral silício. Fótons com energia suficiente '
    'liberam pares elétron-lacuna, que o campo elétrico da junção separa, produzindo corrente contínua — o '
    'efeito fotovoltaico (Villalva; Gazoli, 2015). Uma célula fornece cerca de 0,5 a 0,6 V; um módulo de 36 '
    'células, típico de 10 W para sistemas de 12 V, opera em torno de 17–18 V no ponto de máxima potência e '
    'chega a 21–22 V em aberto. A corrente é aproximadamente proporcional à irradiância (Pinho; Galdino, 2014).',
    'Tensão é a diferença de potencial entre dois pontos; corrente, o fluxo de cargas no tempo. Em corrente '
    'contínua (CC), caso de painéis e baterias, o sentido é constante (Boylestad, 2012). A potência e a energia '
    'são dadas pela Equação 1; para o painel de 10 W em 18 V, I ≈ 0,56 A.',
)
r.equacao('P = V · I          E = P · t', 'em que P é a potência (W), V a tensão (V), I a corrente (A), E a energia (Wh) e t o tempo (h).')
r.p('Como a geração solar varia ao longo do dia, a energia é armazenada em uma bateria selada de chumbo-ácido '
    'de 12 V. A carga a partir do painel exige um **controlador de carga**: sem ele, os ≈ 21 V do painel '
    'sobrecarregariam a bateria durante o dia e, à noite, ela se descarregaria através do painel (Pinho; '
    'Galdino, 2014). Para as saídas USB, de 5 V, um conversor CC-CC chaveado (*buck*) reduz a tensão da '
    'bateria com eficiência da ordem de 90%, muito superior à de um regulador linear (Boylestad, 2012).')
r.h2('2.2 Sensores de luminosidade (LDR)')
r.p('O LDR é um resistor cuja resistência diminui com a iluminância E, aproximadamente segundo R = R₁₀·(E/10)^(−γ), '
    'com R₁₀ entre 10 e 20 kΩ e γ ≈ 0,7. Ligado em divisor de tensão com um resistor fixo de 10 kΩ, a tensão '
    'na entrada analógica cresce com a luz (Equação 2). Com luz muito forte, porém, os divisores se aproximam '
    'da tensão de alimentação e as diferenças entre sensores diminuem (saturação). Quatro LDRs montados em '
    'cruz, separados por anteparos opacos, indicam a **direção** da luz: os anteparos sombreiam os sensores do '
    'lado oposto ao Sol, e o controlador compara as médias de cada lado.')
r.equacao('Vₐ = Vcc · 10 000 / (R + 10 000)', 'em que Vcc é a tensão do divisor (5 V no Arduino Nano; 3,3 V no ESP32).')
r.h2('2.3 Rastreamento solar e a lei do cosseno')
r.p('A potência captada é proporcional à componente da radiação perpendicular ao painel: P(θ) = P₀·cos θ, em '
    'que θ é o ângulo entre o Sol e a normal ao painel (Duffie; Beckman, 2013). Perto do alinhamento a perda é '
    'pequena — 1,5% para 10° e 5% para 18° —, mas cresce rapidamente, chegando a 50% em 60°. Um rastreador, '
    'portanto, não precisa ser perfeito, mas não pode ficar “perdido”. Os rastreadores podem ter um ou dois '
    'eixos e ser **sensoriais**, como este, ou **astronômicos**, que calculam a posição do Sol por data, hora '
    'e coordenadas (Mousazadeh *et al.*, 2009).')
r.h2('2.4 Automação, controle e microcontroladores')
r.ps(
    'Um sistema automatizado executa uma tarefa a partir de sensores processados por um controlador que comanda '
    'atuadores (Bolton, 2010). No rastreador, a orientação do painel altera a própria leitura dos sensores: é um '
    'controle em **malha fechada** (Ogata, 2010), aqui do tipo liga-desliga com zona morta — se a diferença '
    'entre lados excede uma tolerância, o servo avança um passo fixo; senão, permanece parado. A zona morta '
    'evita oscilação por ruído, ao custo de um pequeno erro residual.',
    'O servomotor recebe a cada 20 ms um pulso cuja largura (≈ 0,5 a 2,4 ms) define o ângulo, e mantém a '
    'posição por conta própria (Monk, 2017). O projeto começou com o Arduino Nano (ATmega328P, 8 bits, 16 MHz, '
    'ADC de 10 bits) e migrou para o ESP32, microcontrolador de 32 bits e até 240 MHz com Wi-Fi e Bluetooth '
    'integrados e ADC de 12 bits (0–4095), cujas entradas operam em 3,3 V (Espressif Systems, 2025). O Wi-Fi '
    'permite que o próprio ESP32 crie uma rede e sirva uma página de controle ao celular.',
)

# =====================================================================  3 DESENVOLVIMENTO
r.h1('3 DESENVOLVIMENTO DO PROJETO')
r.h2('3.1 Descrição geral do sistema')
r.p(f'A Figura {r.prox_fig()} apresenta o sistema. Na cadeia de energia, o painel carrega a bateria por um '
    'controlador de carga; da bateria, protegida por fusível, derivam o conversor das saídas USB, o conversor de '
    '6 V dos servos e o da placa de controle. Em paralelo, a malha de rastreamento — LDRs, ESP32 e servos — '
    'orienta o painel, e o celular se conecta ao ESP32 por Wi-Fi. Blocos tracejados indicam partes projetadas '
    'e ainda não montadas.')
r.figura(f('d_blocos.png'), 'Diagrama de blocos da torre solar', largura=16)
r.h2('3.2 Estrutura física')
r.p('O roteiro do PIM sugere uma torre de tubo plástico de 5 polegadas fixada ao solo; o grupo desenvolveu o '
    'mecanismo de rastreamento em CAD, com peças próprias para impressão 3D, cuja base cilíndrica pode ser '
    'montada no topo do tubo, que abriga bateria, conversores e saídas USB. Usar a geometria exata do CAD '
    f'também permitiu simular o sistema. A Figura {r.prox_fig()} mostra uma renderização fotorrealista feita a '
    'partir dos próprios arquivos STL, com os servos na posição calculada pelo simulador para as 10 h do '
    'solstício de inverno. São dois eixos: o prato giratório (azimute), sobre o qual se apoia o segundo servo, '
    'e a trave articulada que inclina o painel (elevação). Com o centro do painel a ≈ 64 mm do eixo de elevação '
    'e massa estimada de 1 kg, o torque exigido é τ = m·g·d ≈ 6,4 kgf·cm, dentro dos 11 kgf·cm do MG996R a 6 V.')
r.figura(f('render_heroi.png'), 'Renderização da montagem a partir das peças do CAD (21 de junho, 10 h)',
         fonte='Elaborado pelos autores no Blender a partir dos arquivos STL do projeto, 2026.', largura=11.5)
r.h2('3.3 Captação e rastreamento')
r.p('O painel é um módulo monocristalino de 10 W; com irradiação de 4,5–5 kWh/m² por dia na região '
    '(Pereira *et al.*, 2017), estima-se uma geração diária ideal de 45 a 50 Wh para o painel fixo, antes das '
    f'perdas. Os quatro LDRs ficam no suporte em cruz preso à borda do painel (Figura {r.prox_fig()}), '
    'identificados como superior esquerdo (SE), superior direito (SD), inferior esquerdo (IE) e inferior '
    'direito (ID). A cada 100 ms o firmware calcula as médias por lado e move 2° o eixo cujo desequilíbrio '
    'excede a tolerância, na direção do lado mais iluminado.')
r.figura(f('render_detalhe_ldr.png'), 'Detalhe do suporte em cruz com os quatro LDRs',
         fonte='Elaborado pelos autores no Blender a partir dos arquivos STL do projeto, 2026.', largura=9.5)
r.h2('3.4 Circuito elétrico e eletrônico')
r.p(f'O circuito foi inicialmente simulado no Tinkercad com Arduino, e o esquemático atual, com o ESP32, está na '
    f'Figura {r.prox_fig()}. Os LDRs ficam nas entradas GPIO 34, 35, 32 e 33, do conversor ADC1 — o ADC2 do '
    'ESP32 não funciona com o Wi-Fi ligado —, e os servos nas saídas 18 e 19. O Quadro 1 relaciona os componentes.')
r.figura(f('d_esquematico.png'), 'Esquemático elétrico do rastreador com ESP32 e da alimentação', largura=15.5)
r.tabela('Componentes do protótipo e suas funções', ['Qtd.', 'Componente', 'Função'], [
    ['1', 'ESP32 + placa de expansão com bornes', 'Lê os LDRs, comanda os servos e serve a página Wi-Fi'],
    ['4', 'LDR 5 mm + resistor 10 kΩ', 'Divisores luz → tensão (GPIO 34, 35, 32, 33)'],
    ['2', 'Servo MG996R (engrenagens metálicas)', 'Azimute (GPIO 18) e elevação (GPIO 19)'],
    ['1', 'Painel monocristalino 10 W', 'Gera a energia do sistema'],
    ['1', 'Bateria selada 12 V', 'Armazena a energia'],
    ['2', 'Conversor *step-down* XL4015 (5 A)', '12 V da bateria → 6 V (servos e placa de controle)'],
    ['—', 'Controlador de carga, conversor USB duplo, fusível (planejados)', 'Carga segura, saídas USB e proteção'],
], larguras=[1.3, 7.2, 7.5], quadro=True)
r.p('Três cuidados merecem destaque: os servos não são alimentados pela placa de controle (cada MG996R pode '
    'exigir ≈ 2,5 A travado); os XL4015 são ajustados com multímetro, sem carga, antes de qualquer ligação; e '
    'os divisores dos LDRs devem usar o **3,3 V** do ESP32, cujas entradas não toleram 5 V.')

r.h2('3.5 Programação e controle')
r.p(f'O firmware é escrito em C++ na plataforma Arduino para o ESP32 e compilado ocupa 949 523 bytes (72% da '
    f'memória de programa). A Figura {r.prox_fig()} mostra seu fluxo. Além do rastreamento, ele cria a rede '
    'Wi-Fi da torre e serve a página de controle (seção 4.5), e implementa o **repouso noturno**: se a média '
    'dos quatro LDRs fica abaixo de 500 por 120 s, o painel vai para a posição inicial (20°/90°) e para; acima '
    'de 700 por 30 s, volta a rastrear. A histerese entre os dois limiares e os tempos de confirmação evitam '
    'que nuvens ou sombras passageiras sejam tomadas por noite.')
r.figura(f('d_fluxograma.png'), 'Fluxograma do firmware do ESP32', largura=8.2)
r.p('O Quadro 2 traz o núcleo do rastreamento automático na versão atual do `main.c`, já com as correções descritas na seção 5.5.')
r.codigo('''void rastrearSol() {
  int se, sd, ie, id;
  lerSensores(se, sd, ie, id);
  int esquerda = (se + ie) / 2;   int direita  = (sd + id) / 2;
  int superior = (se + sd) / 2;   int inferior = (ie + id) / 2;

  // painel do outro lado da vertical: inverte o giro horizontal (P10)
  int sentidoHorizontal = (anguloV >= 90) ? 1 : -1;
  if (esquerda > direita + TOLERANCIA)  anguloH += sentidoHorizontal * PASSO_AUTO;
  else if (direita > esquerda + TOLERANCIA) anguloH -= sentidoHorizontal * PASSO_AUTO;

  if (superior > inferior + TOLERANCIA)      anguloV -= PASSO_AUTO;
  else if (inferior > superior + TOLERANCIA) anguloV += PASSO_AUTO;

  anguloH = constrain(anguloH, LIMITE_H_MIN, LIMITE_H_MAX);
  anguloV = constrain(anguloV, LIMITE_V_MIN, LIMITE_V_MAX);
  aplicarPosicao();
}''', 'Rastreamento automático no firmware do ESP32 (TOLERANCIA = 160)', fonte='Autoria própria, 2026 (trecho de `main.c`).')

r.h2('3.6 Simulação')
r.ps(
    'Além do Tinkercad, o grupo desenvolveu um **simulador 3D** que roda no navegador e responde à pergunta: '
    '*o painel realmente segue o Sol, com esta estrutura e este código?* As peças STL são carregadas na posição '
    'de montagem e agrupadas em parte fixa, parte que gira com o azimute e parte que inclina com a elevação; a '
    'luz em cada LDR é calculada lançando raios do sensor ao Sol e verificando se alguma peça os bloqueia '
    '(*raycasting*), com variação de ±10% entre sensores e ruído.',
    'O ponto central é que o simulador executa **o mesmo código-fonte** do firmware. Na fase do Nano, o binário '
    'compilado rodava em um ATmega328P emulado instrução por instrução. Com o ESP32, cuja arquitetura não é '
    'viável emular no navegador, o próprio `main.c` passou a ser compilado para WebAssembly junto com um '
    '*núcleo ESP32 simulado* que implementa as funções usadas pelo programa — tempo (`millis`), ADC de 12 '
    'bits, servos, Wi-Fi e servidor web. Assim, a página do celular servida pelo firmware aparece dentro do '
    f'simulador e controla a torre virtual (Figura {r.prox_fig()}). Os resultados de energia são expressos em '
    'unidade relativa (u.r.), pois o modelo usa intensidade constante e não considera a atmosfera: servem para '
    '**comparar** alternativas, não para prever a geração em Wh.',
)
r.figura(f('simulador_3d.png'), 'Simulador 3D executando o main.c do ESP32, com a página do celular servida pelo firmware',
         fonte='Elaborado pelos autores (simulador do projeto), 2026.', largura=12.5)

r.h2('3.7 Placa de circuito impresso')
r.p(f'Para substituir a protoboard e os jumpers, foi proposta a PCI da Figura {r.prox_fig()}: o ESP32 encaixado '
    'em barras de pinos (U1), os resistores dos divisores junto às entradas analógicas, conectores para os LDRs '
    '(J1–J4) e para os servos (J5, J6), bornes de alimentação (J7, J8) e o capacitor dos servos (C1), com trilhas '
    'de potência mais largas, em 100 × 70 mm. É uma proposta de leiaute; a versão definitiva deve ser roteada '
    'em software de projeto eletrônico [PREENCHER: software e método de fabricação adotados].')
r.figura(f('d_pci.png'), 'Proposta de leiaute da placa de circuito impresso (face das trilhas)', largura=12.5)

r.h2('3.8 Custos')
r.tabela('Custos dos componentes', ['Item', 'Qtd.', 'Unit. (R$)', 'Total (R$)'], [
    ['Sensor LDR 5 mm', '4', '0,45', '1,80'],
    ['Resistor 10 kΩ 1/4 W', '4', '0,05', '0,20'],
    ['Jumpers Dupont 20 cm (macho-fêmea e macho-macho)', '80', '0,05–0,06', '4,40'],
    ['Servo MG996R', '2', '36,80', '73,60'],
    ['Conversor XL4015', '2', '18,50', '37,00'],
    ['Bateria selada 12 V', '1', '78,80', '78,80'],
    ['Painel solar 10 W', '1', '39,24', '39,24'],
    ['**Subtotal dos itens com valor informado**', '', '', '**235,04**'],
    ['ESP32 + placa de expansão', '1', '[PREENCHER]', '[PREENCHER]'],
    ['Filamento PLA', '—', '[PREENCHER]', '[PREENCHER]'],
], fonte='Orçamento da loja de componentes e notas de compra do grupo, 2026.', larguras=[8.6, 1.6, 2.9, 2.9])

# =====================================================================  4 TESTES FÍSICOS
r.h1('4 MONTAGEM E TESTES FÍSICOS')
r.p('Este capítulo descreve a montagem do protótipo e os testes registrados pelo grupo em fotografias e '
    'vídeos. Só são apresentados como resultados os eventos efetivamente registrados; os testes ainda não '
    'realizados constam como pendentes na Tabela 3.')
r.h2('4.1 Fabricação e pré-montagem')
r.p(f'As peças foram impressas em PLA cinza (Figura {r.prox_fig()}a). Na pré-montagem (Figura {r.prox_fig()}b), '
    'a base, as caixas dos servos, o prato giratório e a trave foram montados com os dois MG996R; o painel '
    'fotovoltaico ainda não estava fixado, e a trave aparece com a placa de apoio impressa.')
r.figura(f('f_fabricacao.png'), 'Peças impressas em 3D (a) e estrutura pré-montada com os dois servos (b)',
         fonte='Acervo do grupo, 2026.', largura=11)
r.h2('4.2 Teste dos servomotores')
r.p(f'Com a estrutura parcialmente montada, os dois eixos foram acionados (Figura {r.prox_fig()}): o servo '
    'vertical inclinou a trave em toda a faixa e o horizontal girou o prato com o conjunto superior, sem '
    'travamentos nem reinícios da placa de controle.')
r.figura(f('f_teste_servos.png'), 'Teste dos servos na pré-montagem: diferentes posições da trave',
         fonte='Quadros extraídos de vídeo do grupo, 2026.', largura=15)
r.h2('4.3 Falha: quebra de peça impressa na montagem')
r.p(f'Durante a montagem da trave, a peça de suporte da placa quebrou no encaixe dos braços (Figura {r.prox_fig()}). '
    'Em (a) vê-se o braço acoplado ao servo pelo *horn* metálico, preso por quatro parafusos, e a fratura junto ao '
    'encaixe; em (b) e (c), o braço livre, do lado oposto ao servo. Peças impressas são mais frágeis entre camadas '
    'e nas regiões com furos e encaixes, justamente onde se concentram o aperto dos parafusos e o momento causado '
    'pelo peso da placa. A peça foi **reimpressa em versão mais resistente** e a montagem prosseguiu.')
r.figura(f('f_quebra.png'), 'Montagem da trave: braço do servo com fratura (a) e braço livre (b, c)',
         fonte='Quadros extraídos de vídeo do grupo, 2026.', largura=15)
r.h2('4.4 Migração para o ESP32')
r.p(f'Na etapa de testes físicos, o controle migrou do Arduino Nano para um ESP32 em placa de expansão com bornes '
    f'(Figura {r.prox_fig()}a), alimentado por um XL4015 (b) ajustado para converter os 12 V da bateria em 6 V. A '
    'gravação pela Arduino IDE terminou com 100% escrito e verificação do *hash* (c) — o tamanho gravado, cerca '
    'de 950 kB, coincide com a compilação do `main.c`. A troca trouxe o Wi-Fi, o ADC de 12 bits e mais memória, '
    'mas exigiu reescrever o firmware — o que, como mostra o capítulo 5, reintroduziu dois problemas.')
r.figura(f('f_esp32.png'), 'ESP32 em operação (a), conversor XL4015 e protoboard (b) e gravação concluída (c)',
         fonte='Quadros extraídos de vídeo do grupo, 2026.', largura=15)
r.h2('4.5 Controle pelo celular')
r.p('O ESP32 cria sua própria rede, sem depender de roteador ou internet. Para controlar a torre:')
r.itens([
    'no celular, conectar à rede Wi-Fi **SOLAR_TOWER**, senha **torre1234**;',
    'abrir no navegador o endereço **http://192.168.4.1**;',
    'escolher **AUTOMÁTICO** (rastreamento pelos LDRs) ou **MANUAL**, que libera os botões ◀ ▶ ▲ ▼ (5° por toque) e **POSIÇÃO INICIAL**;',
    'acompanhar em “Informações” os ângulos, a luminosidade média e o estado (ATIVO ou NOITE – REPOUSO).',
])
r.p(f'No teste (Figura {r.prox_fig()}), o celular conectou-se à rede da torre, a página indicou “Wi-Fi conectado '
    'à torre” e, em modo manual, os botões moveram os dois eixos. Por segurança, o firmware recusa movimentos '
    'manuais em modo automático ou durante o repouso noturno.')
r.figura(f('f_celular.png'), 'Página de controle no celular (a) e teste da torre pela interface (b)',
         fonte='Captura de tela e quadro de vídeo do grupo, 2026.', largura=12.5)
r.h2('4.6 Rastreamento automático com lanterna')
r.p('No teste de rastreamento automático com uma lanterna, a torre reagiu à luz, mas **girou para o lado '
    'contrário**, afastando o painel da lanterna em vez de apontá-lo para ela. O resultado mostra que a cadeia '
    'sensor–controlador–atuador funciona, mas que o sentido da correção está invertido em relação à montagem '
    'real — situação prevista no plano de testes, pois o sinal de cada eixo depende de como o servo e os '
    'sensores foram montados. As causas possíveis, da mais simples à mais trabalhosa, são:')
r.itens([
    '**sentido de montagem do servo:** se o servo foi fixado espelhado em relação ao modelo, o sinal do eixo se inverte; corrige-se trocando `+=` por `-=` naquele eixo do `main.c`;',
    '**divisor dos LDRs invertido:** com o LDR no lado do GND, mais luz produz tensão **menor**, o que inverte os dois eixos de uma vez;',
    '**sensores trocados de posição** entre os pinos 34, 35, 32 e 33, o que inverte um eixo ou cruza os dois;',
    '**P10:** o teste usou a versão anterior às correções; se a inversão ocorreu só no eixo horizontal e com o painel inclinado para um dos lados, é o defeito corrigido na seção 5.5.',
])
r.p('Para identificar a causa, recomenda-se repetir o teste iluminando um lado de cada vez e anotar qual eixo se '
    'move e em que sentido. A migração para o ESP32 retirou do monitor serial as leituras individuais dos LDRs, '
    'que existiam na versão do Nano; reincluí-las facilita esse diagnóstico. No simulador, as opções “inverter '
    'servo” reproduzem cada hipótese.')

r.h2('4.7 Resultados')
r.tabela('Resultados dos testes físicos', ['Teste', 'Resultado', 'Evidência'], [
    ['Impressão e montagem mecânica', 'Aprovado após reimpressão da peça quebrada', 'Fotos e vídeo'],
    ['Movimento dos dois servos', 'Aprovado', 'Vídeo'],
    ['Gravação do firmware no ESP32', 'Aprovado (100%, *hash* verificado)', 'Vídeo'],
    ['Rede Wi-Fi e página no celular', 'Aprovado', 'Captura e vídeo'],
    ['Comando manual pelo celular', 'Aprovado', 'Vídeo'],
    ['Rastreamento automático com lanterna', 'Falha: girou para o lado contrário (seção 4.6)', 'Teste do grupo'],
    ['Repouso noturno', 'Validado em simulação (seção 5.6); físico [PREENCHER]', '—'],
    ['Ajuste do XL4015', 'Aprovado: 12 V → 6 V', 'Teste do grupo'],
    ['Correções P10 e P14 no protótipo', 'Validadas em simulação; físico [PREENCHER]', '—'],
    ['Tensão do painel, carga da bateria e saídas USB', 'Pendente (controlador e módulo USB não adquiridos)', '—'],
], larguras=[6.0, 6.5, 3.5])

# =====================================================================  5 HISTÓRICO
r.h1('5 HISTÓRICO DO DESENVOLVIMENTO: ERROS E ACERTOS')
r.p(f'Este capítulo registra, em ordem cronológica, os problemas encontrados, como foram descobertos, suas causas '
    f'e as soluções. A Figura {r.prox_fig()} resume a trajetória; os códigos (P1, P10...) remetem à lista de '
    'problemas mantida no repositório do projeto.')
r.figura(f('d_linha_do_tempo.png'), 'Linha do tempo do desenvolvimento: erros, acertos e situação de cada item', largura=15.5)

r.h2('5.1 Revisão antes de montar (P1) e medição do laço')
r.ps(
    'A primeira tarefa foi revisar código, diagrama e peças antes de comprar ou montar qualquer coisa. Ela '
    'revelou que o código do Nano lia os LDRs nas entradas A1–A4, enquanto o diagrama do Tinkercad os ligava em '
    'A0–A3: montado como no diagrama, o firmware leria um pino desconectado. A divergência ficou registrada '
    '(P1) e foi encerrada com a migração para o ESP32, que tem pinos próprios.',
    'Também se estimou o período do laço do Nano em 150 ms (50 ms de pausa mais ≈ 100 ms de telemetria a '
    '9 600 baud); no emulador mediu-se 98 ms, porque a porta serial transmite em segundo plano durante a '
    'pausa. **Lição:** medir em vez de estimar.',
)
r.h2('5.2 A inversão do eixo horizontal (P10)')
r.p('No simulador, com o Sol a Nordeste o painel o seguia, mas com o Sol a Sudeste ou Sudoeste o servo '
    'horizontal girava **para longe** do Sol até o fim de curso. Como os LDRs giram com o painel, “esquerda” e '
    '“direita” são medidas no referencial do painel; quando o servo vertical passa de 90°, o painel fica '
    'voltado para o outro lado do céu e a mesma rotação do prato desloca o Sol no sentido contrário em relação '
    'aos sensores. A correção tornou o sentido do giro horizontal dependente do lado do painel '
    f'(`sentidoHorizontal`), reduzindo o erro final, no firmware do Nano, para {NANO_SE}° com o Sol a Sudeste e '
    f'{NANO_SO}° a Sudoeste.')
r.h2('5.3 Um erro de método: testes contaminados')
r.p('Ao validar o P10, os cenários eram encadeados sem reiniciar o microcontrolador simulado. Como o firmware '
    'guarda os próprios ângulos na memória, cada teste começava onde o anterior terminara. O erro foi notado '
    'porque cenários diferentes deram resultados idênticos; criou-se a função de *reset* e todos os testes '
    'foram refeitos. O mesmo tipo de erro reapareceu na fase do ESP32: um cenário “Nano” deixou o Nano como '
    'firmware ativo, e as rodadas seguintes, supostamente do ESP32, rodaram o Nano. Desde então, cada teste '
    'confirma qual firmware está ativo antes de valer. **Lição:** em sistemas com estado interno, um teste só é '
    'válido com condição inicial conhecida.')
r.h2('5.4 A sombra que o próprio painel projeta (P13)')
r.p(f'Simulando **dias inteiros**, o rastreador do Nano captou {P13_CAD} de energia em relação à placa fixa no '
    'solstício de inverno: ao amanhecer, inclinou-se para o lado errado e ficou voltado ao Sul o dia todo. Uma '
    'função de diagnóstico, que informa qual peça bloqueia o raio de cada LDR, mostrou que, no CAD, o suporte '
    'dos sensores fica cerca de 13 mm **abaixo** do plano do painel: com luz rasante, o próprio painel '
    'sombreia os sensores inferiores, e o firmware inclina o painel no sentido contrário. A primeira simulação '
    'com o suporte elevado não mostrou melhora — o navegador havia usado a versão antiga do código, em *cache*. '
    f'Corrigido isso, a elevação de 25 mm transformou o resultado em {P13_ELEV} (Figura {r.prox_fig()}). A '
    'solução proposta é um espaçador de 25 mm no suporte dos LDRs, a confirmar no protótipo.')
r.figura(f('g_dia_junho.png'), 'Simulação de 21 de junho: geometria do CAD × LDRs elevados 25 mm (firmware do Nano)', largura=15.5)

r.h2('5.5 A migração para o ESP32 e duas regressões (P10 e P14)')
r.p('Com o firmware do ESP32 pronto e testado fisicamente, o simulador foi adaptado para compilar o mesmo '
    '`main.c` (seção 3.6). Os testes revelaram dois problemas introduzidos na reescrita:')
r.itens([
    f'**P10 regrediu:** a variável `sentidoHorizontal` não foi levada para a versão usada nos testes físicos. Com o Sol a '
    f'Sudeste ou Sudoeste o servo horizontal volta a travar no fim de curso, com erro de {err(ATUAL + "|SE")}° e '
    f'{err(ATUAL + "|SO")}°;',
    f'**P14 — tolerância não reescalonada:** a `TOLERANCIA = 40` foi herdada do Nano, em que valia ≈ 4% da '
    'escala de 10 bits; no ADC de 12 bits do ESP32 ela vale ≈ 1%, e a diferença natural entre os LDRs passa a '
    f'comandar o painel com pouca luz. Em 21 de junho o painel foge do Sol ao amanhecer ({eng(ATUAL + "|jun")}). '
    'Sem variação entre LDRs o rastreamento funciona — o que confirmou a causa.',
])
r.p(f'Para medir as correções sem alterar o `main.c` dos testes, foram compiladas duas variantes: tolerância '
    f'160 (40 × 4) e tolerância 160 com o P10 restaurado. A Figura {r.prox_fig()} compara as três versões: só '
    f'a segunda variante acerta todas as posições (erro de {err(TOLP10 + "|SE")}°, {err(TOLP10 + "|SO")}° e '
    f'{err(TOLP10 + "|NE")}°) e capta {eng(TOLP10 + "|jun")} em junho e {eng(TOLP10 + "|dez")} em dezembro em '
    'relação à placa fixa. Confirmado o efeito, as duas correções foram incorporadas ao `main.c` (Quadro 2), '
    'que compila para o ESP32 e reproduz exatamente os resultados da variante; o repouso noturno e a '
    'interface web foram conferidos novamente. Falta a validação no protótipo físico.')
r.figura(f('g_esp32.png'), 'Firmware do ESP32 em simulação: versão dos testes físicos e versões com as correções', largura=16)
r.h2('5.6 A noite e o retorno ao Leste (P7) — resolvido')
r.p('O firmware do Nano não tratava a noite: o painel parava voltado ao Oeste e amanhecia de costas para o Sol. '
    f'O ESP32 implementou o repouso noturno. Em simulação de uma noite de dezembro (Figura {r.prox_fig()}), o '
    f'ESP32 estaciona após 120 s de escuro e volta a rastrear às {hora(ESP_ACORDA)}, já alinhado; sem o repouso, '
    f'o painel amanhece com {NANO_ERRO_INI}° de erro e só se alinha por volta das {hora(NANO_ALINHA)} — mais de '
    'três horas de manhã aproveitadas.')
r.figura(f('g_noite_esp32.png'), 'Amanhecer de 21 de dezembro com e sem repouso noturno (simulação)', largura=13)
r.h2('5.7 Lições aprendidas')
r.tabela('Síntese dos problemas, soluções e lições', ['Problema', 'Como foi encontrado', 'Situação', 'Lição'], [
    ['P1 – Pinos do código × diagrama', 'Revisão cruzada', 'Encerrado', 'Conferir documentos entre si'],
    ['Período do laço', 'Medição no emulador', 'Corrigido', 'Medir em vez de estimar'],
    ['P10 – Inversão horizontal', 'Simulador, Sol ao Sul', 'Regrediu e restaurado', 'Testar de novo após reescrever'],
    ['Testes contaminados', 'Resultados idênticos', 'Corrigido', 'Condição inicial conhecida'],
    ['P13 – Sombra do painel', 'Simulação de dias', 'Proposta', 'Integrar mecânica e eletrônica'],
    ['Quebra da peça impressa', 'Montagem física', 'Reimpressa', 'Reforçar regiões de esforço'],
    ['Lanterna: sentido invertido', 'Teste físico', 'Em diagnóstico', 'Validar o sentido de cada eixo'],
    ['P7 – Noite', 'Simulação da madrugada', 'Resolvido (ESP32)', 'Prever todos os estados'],
    ['P14 – Tolerância 12 bits', 'Simulação do ESP32', 'Corrigido', 'Revisar unidades ao trocar de hardware'],
], larguras=[4.6, 3.9, 3.0, 4.5], quadro=True)

# =====================================================================  6 APLICAÇÕES
r.h1('6 APLICAÇÕES DO PROJETO')
r.p('A torre atende a uma necessidade cotidiana — o celular descarregado longe de uma tomada — com fonte '
    'renovável e sem ligação à rede. Destacam-se como aplicações, algumas exigindo adequações:')
r.itens([
    '**parques e praças**, onde não há tomadas e a instalação elétrica seria cara;',
    '**escolas e universidades**, em áreas de convivência, também como recurso didático;',
    '**pontos de ônibus, filas e salas de espera**;',
    '**eventos ao ar livre, áreas rurais e situações de emergência**, como apoio à comunicação.',
])
r.p('O controle por Wi-Fi do ESP32 abre outra possibilidade: a página da torre pode exibir, para o público, a '
    'energia gerada e o estado do sistema, ou permitir a manutenção sem abrir o equipamento. Para uso público '
    'seriam necessários estrutura resistente a intempéries e vandalismo, painel de 50 a 100 W, bateria maior e '
    'saídas USB com proteção individual.')
r.tabela('Vantagens e limitações da torre solar', ['Vantagens', 'Limitações'], [
    ['Energia renovável, sem custo de operação', 'Depende da luminosidade e do clima'],
    ['Independe da rede elétrica', 'Capacidade limitada pela bateria'],
    ['Rastreamento aumenta a energia captada', 'Partes móveis exigem manutenção'],
    ['Monitoramento e controle pelo celular', 'Custo de implantação maior que uma tomada'],
], larguras=[8, 8], quadro=True)
r.p('Uma estimativa ilustra a capacidade: um celular com bateria de 4 000 mAh a 3,85 V armazena ≈ 15,4 Wh; com '
    '15% de perdas, cada recarga consome ≈ 18 Wh. Com ≈ 45 Wh por dia (seção 3.3), o painel de 10 W sustentaria '
    'cerca de duas recargas diárias — número que o rastreamento pode elevar.')

# =====================================================================  7 DISCIPLINAS / 8 SUSTENTABILIDADE
r.h1('7 RELAÇÃO COM AS DISCIPLINAS DO CURSO')
r.tabela('Contribuição das disciplinas para o projeto', ['Disciplina', 'Aplicação no projeto'], [
    ['Instalações Elétricas Industriais', 'Alimentação, fusível, interligação de terras, bitola dos cabos dos servos'],
    ['Circuitos Elétricos', 'Divisor de tensão dos LDRs, potência do painel, conversores CC-CC'],
    ['Física', 'Efeito fotovoltaico, lei do cosseno, torque no eixo de elevação, movimento aparente do Sol'],
    ['Cálculo II', 'Funções trigonométricas e de potência nos modelos; energia como integral da potência no tempo'],
    ['Linguagem de Programação Aplicada', 'Firmware em C++, servidor web no ESP32, simulador e análise dos dados'],
    ['Metodologia Científica', 'Hipóteses e testes (capítulo 5), registro de resultados, citações e referências'],
], larguras=[5.2, 10.8], quadro=True)
r.h1('8 SUSTENTABILIDADE E EFICIÊNCIA ENERGÉTICA')
r.ps(
    'O projeto usa fonte renovável e reduz a dependência da rede para uma demanda pequena, mas permanente, e tem '
    'valor demonstrativo em espaço público. A eficiência foi considerada em cada etapa: o rastreamento aumenta a '
    'energia captada pelo mesmo painel; os conversores chaveados evitam o desperdício dos reguladores lineares; '
    'a zona morta reduz os movimentos dos servos; e o repouso noturno elimina movimentos inúteis à noite. O '
    'consumo do próprio rastreador deve ser sempre pequeno diante do ganho que proporciona.',
    'Pontos a melhorar: o consumo do ESP32 com Wi-Fi ativo, que justifica desligar o ponto de acesso quando '
    'ninguém está conectado; a vida útil e o descarte correto da bateria de chumbo-ácido; e o uso de filamentos '
    'mais resistentes ao sol, como o PETG.',
)

# =====================================================================  9 CONCLUSÃO
r.h1('9 CONCLUSÃO')
r.ps(
    'O objetivo foi atendido nos níveis de projeto e simulação e parcialmente no protótipo físico. A estrutura '
    'foi impressa e montada — com a reimpressão de uma peça que quebrou —, os servos foram testados, o ESP32 '
    'foi programado e a torre é controlada pelo celular por sua própria rede Wi-Fi. No teste com lanterna, o '
    'rastreamento reagiu à luz, mas no sentido contrário, o que indica um sinal de eixo invertido a corrigir. A captação com controlador de carga, as saídas USB e a PCI estão '
    'projetadas, mas ainda não foram construídas nem testadas.',
    'O principal resultado, contudo, foi o método. A combinação de revisão, simulação do mesmo código e testes '
    'físicos permitiu encontrar uma inversão no algoritmo, erros de método nos testes, o sombreamento dos '
    'sensores pelo próprio painel e, depois da migração para o ESP32, duas regressões que o comportamento em '
    'bancada dificilmente revelaria — ambas já corrigidas no código. O episódio mostra que trocar de plataforma exige revisar não só o código, '
    'mas as unidades e as correções acumuladas.',
    'Como próximos passos, recomenda-se:',
)
r.itens([
    'diagnosticar o sentido invertido observado com a lanterna (seção 4.6), iluminando um lado de cada vez, e ajustar o sinal do eixo correspondente;',
    'validar no protótipo as correções P10 e P14, já aplicadas ao `main.c` e verificadas em simulação;'
    'elevar o suporte dos LDRs em ≈ 25 mm (P13) e validar com lanterna rasante;',
    'reforçar ou reimprimir as peças da trave sujeitas a esforço;',
    'adquirir controlador de carga, fusível e módulo USB, fabricar a PCI e medir a energia real com e sem rastreamento.',
], marcador='a')

# =====================================================================  REFERÊNCIAS
r.titulo_sem_numero('REFERÊNCIAS')
for ref in [
    'BOLTON, W. **Mecatrônica**: uma abordagem multidisciplinar. 4. ed. Porto Alegre: Bookman, 2010.',
    'BOYLESTAD, R. L. **Introdução à análise de circuitos**. 12. ed. São Paulo: Pearson Prentice Hall, 2012.',
    'DUFFIE, J. A.; BECKMAN, W. A. **Solar engineering of thermal processes**. 4. ed. Hoboken: Wiley, 2013.',
    'ESPRESSIF SYSTEMS. **ESP32 series datasheet**. Xangai: Espressif, 2025. Disponível em: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf. Acesso em: 10 nov. 2026.',
    'MONK, S. **Programação com Arduino**: começando com sketches. 2. ed. Porto Alegre: Bookman, 2017.',
    'MOUSAZADEH, H.; KEYHANI, A.; JAVADI, A.; MOBLI, H.; ABRINIA, K.; SHARIFI, A. A review of principle and sun-tracking methods for maximizing solar systems output. **Renewable and Sustainable Energy Reviews**, v. 13, n. 8, p. 1800-1818, 2009. DOI: https://doi.org/10.1016/j.rser.2009.01.022.',
    'OGATA, K. **Engenharia de controle moderno**. 5. ed. São Paulo: Pearson Prentice Hall, 2010.',
    'PEREIRA, E. B.; MARTINS, F. R.; GONÇALVES, A. R.; COSTA, R. S.; LIMA, F. J. L.; RÜTHER, R.; ABREU, S. L.; TIEPOLO, G. M.; PEREIRA, S. V.; SOUZA, J. G. **Atlas brasileiro de energia solar**. 2. ed. São José dos Campos: INPE, 2017.',
    'PINHO, J. T.; GALDINO, M. A. (org.). **Manual de engenharia para sistemas fotovoltaicos**. Rio de Janeiro: CEPEL – CRESESB, 2014.',
    'VILLALVA, M. G.; GAZOLI, J. R. **Energia solar fotovoltaica**: conceitos e aplicações. 2. ed. São Paulo: Érica, 2015.',
]:
    r.p(ref, estilo='Referencia', recuo=False)

r.salvar(SAIDA)
print('OK', SAIDA)
