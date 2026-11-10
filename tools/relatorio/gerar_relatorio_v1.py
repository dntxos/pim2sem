"""Gera o relatório do PIM II (docs/relatorio/PIM_Torre_Solar_v1.docx).

Uso: python tools/relatorio/gerar_relatorio.py   (requer python-docx)
Antes: tools/relatorio/graficos.py, tools/relatorio/diagramas.py e tools/render/gerar_figuras_relatorio.sh.
Resultados numéricos vêm de docs/relatorio/dados/ (simulação) — não alterar à mão.
"""
import os
import sys

from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.path.insert(0, os.path.dirname(__file__))
from abnt_docx import ESTILO_FIG, ESTILO_TAB, Relatorio  # noqa: E402

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FIG = os.path.join(RAIZ, 'docs', 'relatorio', 'figuras')
SAIDA = os.path.join(RAIZ, 'docs', 'relatorio', 'PIM_Torre_Solar_v1.docx')
C = WD_ALIGN_PARAGRAPH.CENTER


def f(nome):
    return os.path.join(FIG, nome)


TITULO = 'TORRE SOLAR COM RASTREAMENTO AUTOMÁTICO PARA CARGA DE TELEFONES CELULARES'
SUBTITULO = 'projeto, simulação e lições do desenvolvimento de um rastreador solar de dois eixos'
INTEGRANTES = [
    '[PREENCHER: Nome completo do integrante 1] (RA: [PREENCHER])',
    '[PREENCHER: Nome completo do integrante 2] (RA: [PREENCHER])',
    '[PREENCHER: Nome completo do integrante 3] (RA: [PREENCHER])',
    '[PREENCHER: Nome completo do integrante 4] (RA: [PREENCHER])',
]

r = Relatorio()

# =====================================================================  CAPA
r.p('**UNIVERSIDADE PAULISTA – UNIP**', alin=C, recuo=False)
r.p('**Campus Sorocaba**', alin=C, recuo=False)
r.espaco()
r.p('**Curso Superior de Tecnologia em Automação Industrial**', alin=C, recuo=False)
r.espaco(3)
for n in INTEGRANTES:
    r.p(f'**{n}**', alin=C, recuo=False)
r.espaco(5)
r.p(f'**{TITULO}:**', alin=C, recuo=False)
r.p(SUBTITULO, alin=C, recuo=False)
r.espaco(10)
r.p('**Sorocaba/SP**', alin=C, recuo=False)
r.p('**2026**', alin=C, recuo=False)

# =====================================================================  FOLHA DE ROSTO
r.quebra()
for n in INTEGRANTES:
    r.p(f'**{n.split(" (RA")[0]}**', alin=C, recuo=False)
r.espaco(6)
r.p(f'**{TITULO}:**', alin=C, recuo=False)
r.p(SUBTITULO, alin=C, recuo=False)
r.espaco(2)
nat = r.p('Trabalho apresentado ao Curso Superior de Tecnologia em Automação Industrial da Universidade '
          'Paulista – UNIP, Campus Sorocaba, como requisito parcial para obtenção de nota na disciplina de '
          'Projeto Integrado Multidisciplinar (PIM II), sob orientação do Prof. [PREENCHER: nome do orientador].',
          recuo=False, tamanho=12)
nat.paragraph_format.left_indent = __import__('docx.shared', fromlist=['Cm']).Cm(8)
nat.paragraph_format.line_spacing_rule = 0
r.espaco(6)
r.p('**Sorocaba/SP**', alin=C, recuo=False)
r.p('**2026**', alin=C, recuo=False)

# =====================================================================  RESUMO / ABSTRACT
r.titulo_sem_numero('RESUMO')
r.p('Este trabalho apresenta o projeto de uma torre de captação de energia solar destinada à carga de '
    'telefones celulares, com ênfase no subsistema de rastreamento solar de dois eixos. O protótipo utiliza '
    'um painel fotovoltaico de 10 W, uma bateria selada de 12 V, conversores de tensão do tipo *step-down* '
    'XL4015, um Arduino Nano e dois servomotores MG996R, orientados por quatro sensores LDR dispostos em cruz. '
    'A estrutura foi modelada em CAD e preparada para impressão 3D. Para validar o projeto antes da montagem, '
    'o grupo desenvolveu um simulador tridimensional que executa o firmware compilado em um microcontrolador '
    'ATmega328P emulado, sobre as peças reais da montagem, calculando por *raycasting* a luz recebida por cada '
    'sensor. O trabalho documenta também a trajetória do desenvolvimento, com seus erros e acertos: a '
    'divergência de pinos entre o código e o diagrama, uma inversão no algoritmo do eixo horizontal que '
    'levava o painel ao fim de curso, um erro de método nos testes que contaminava resultados, a saturação '
    'dos sensores e, por fim, a descoberta de que a posição do suporte dos LDRs no CAD permite que o próprio '
    'painel sombreie os sensores. Em simulação, a correção do algoritmo reduziu o erro de apontamento de 53° '
    'para 18°, e a elevação do suporte dos sensores em 25 mm transformou um rendimento 74% inferior ao de '
    'uma placa fixa em um ganho de 33% no solstício de inverno. São apresentados ainda o circuito elétrico, '
    'a proposta de placa de circuito impresso, as aplicações do projeto e a relação com as disciplinas do curso.',
    recuo=False)
r.espaco()
r.p('**Palavras-chave:** energia solar fotovoltaica; rastreador solar; Arduino; sensor LDR; simulação; automação.', recuo=False)

r.titulo_sem_numero('ABSTRACT')
r.p('This work presents the design of a solar energy tower for charging mobile phones, focusing on its '
    'dual-axis solar tracking subsystem. The prototype uses a 10 W photovoltaic panel, a 12 V sealed battery, '
    'XL4015 step-down converters, an Arduino Nano and two MG996R servomotors, steered by four light-dependent '
    'resistors arranged in a cross. The structure was modeled in CAD for 3D printing. To validate the design '
    'before assembly, the team built a three-dimensional simulator that runs the compiled firmware on an '
    'emulated ATmega328P microcontroller over the real assembly parts, computing the light received by each '
    'sensor through ray casting. The report also documents the development path, including mistakes and '
    'successes: a pin mismatch between code and wiring diagram, an inversion in the horizontal-axis algorithm '
    'that drove the panel to its end stop, a test-method error that contaminated results, sensor saturation and, '
    'finally, the finding that the sensor holder position in the CAD allows the panel itself to shade the '
    'sensors. In simulation, the algorithm fix reduced the pointing error from 53° to 18°, and raising the '
    'sensor holder by 25 mm turned a yield 74% lower than a fixed panel into a 33% gain at the winter '
    'solstice. The electrical circuit, a printed circuit board proposal, applications and the relationship '
    'with the course subjects are also presented.', recuo=False)
r.espaco()
r.p('**Keywords:** photovoltaic solar energy; solar tracker; Arduino; LDR sensor; simulation; automation.', recuo=False)

# =====================================================================  LISTAS
r.lista('LISTA DE ILUSTRAÇÕES', 'Figura')
r.lista('LISTA DE QUADROS', 'Quadro')
r.lista('LISTA DE TABELAS', 'Tabela')
r.titulo_sem_numero('LISTA DE ABREVIATURAS E SIGLAS')
siglas = [
    ('ABNT', 'Associação Brasileira de Normas Técnicas'), ('ADC', 'Conversor analógico-digital (*Analog-to-Digital Converter*)'),
    ('CAD', 'Desenho assistido por computador (*Computer-Aided Design*)'), ('CC', 'Corrente contínua'),
    ('GND', 'Terra, referência de 0 V (*ground*)'), ('LDR', 'Resistor dependente de luz (*Light Dependent Resistor*)'),
    ('MPPT', 'Rastreamento do ponto de máxima potência (*Maximum Power Point Tracking*)'),
    ('PCI', 'Placa de circuito impresso'), ('PIM', 'Projeto Integrado Multidisciplinar'),
    ('PLA', 'Ácido polilático (filamento de impressão 3D)'), ('PWM', 'Modulação por largura de pulso (*Pulse Width Modulation*)'),
    ('STL', 'Formato de arquivo de malha 3D (*Standard Triangle Language*)'), ('USB', 'Barramento serial universal (*Universal Serial Bus*)'),
    ('u.r.', 'Unidade relativa (energia simulada, adimensional)'),
]
for s, d in siglas:
    par = r.p(f'**{s}**\t{d}', recuo=False)
    par.paragraph_format.tab_stops.add_tab_stop(__import__('docx.shared', fromlist=['Cm']).Cm(2.2))

r.sumario()

# =====================================================================  1 INTRODUÇÃO
r.iniciar_texto()
r.h1('1 INTRODUÇÃO')
r.ps(
    'A energia solar é a fonte renovável mais abundante disponível no território brasileiro. Segundo o '
    '*Atlas Brasileiro de Energia Solar*, a irradiação global horizontal média no país varia entre cerca de '
    '4,4 e 6,2 kWh/m² por dia, valores superiores aos de muitos países europeus que lideram o uso da '
    'tecnologia (Pereira *et al.*, 2017). A conversão direta dessa energia em eletricidade por meio de '
    'módulos fotovoltaicos é silenciosa, modular e dispensa partes móveis, o que a torna adequada tanto a '
    'usinas quanto a pequenos sistemas isolados da rede (Villalva; Gazoli, 2015).',
    'Um módulo fotovoltaico, entretanto, só entrega sua potência nominal quando a radiação incide '
    'perpendicularmente à sua superfície. Em uma instalação fixa, o ângulo entre o Sol e o painel muda ao '
    'longo do dia e do ano, e a potência captada cai aproximadamente com o cosseno desse ângulo. Os '
    'rastreadores solares resolvem esse problema movimentando o painel para acompanhar o Sol; a literatura '
    'relata aumentos de energia coletada entre 10% e 100%, conforme o local, a época e o tipo de rastreador '
    '(Mousazadeh *et al.*, 2009).',
    'O tema proposto para o PIM II do Curso Superior de Tecnologia em Automação Industrial é o projeto de '
    'uma torre que capte energia solar, armazene-a em uma bateria de 12 V e disponibilize duas saídas USB '
    'para a carga de telefones celulares, com o painel acompanhando a posição de maior incidência de luz. '
    'O tema reúne, em um único produto, conteúdos de circuitos elétricos, física, instalações elétricas, '
    'programação e controle — o que o torna um exercício completo de automação.',
    'Este relatório descreve o projeto desenvolvido pelo grupo, com ênfase no subsistema de rastreamento, que '
    'concentra a maior parte do trabalho de engenharia. Além do resultado final, o texto registra '
    'deliberadamente a **história do desenvolvimento**: as hipóteses que se confirmaram, as que se mostraram '
    'erradas e os problemas que só apareceram quando o sistema foi posto à prova em simulação. Entende-se '
    'que esse registro é parte essencial da formação em automação, em que a capacidade de diagnosticar e '
    'corrigir falhas vale tanto quanto a de projetar.',
)
r.h2('1.1 Cronograma de execução')
r.p('A Tabela 1 resume as etapas do projeto e sua situação na data desta versão do relatório.')
r.tabela('Cronograma de execução do projeto', ['Etapa', 'Atividade', 'Período', 'Situação'], [
    ['1', 'Definição do tema e da arquitetura (torre, rastreador, carga USB)', '[PREENCHER]', 'Concluída'],
    ['2', 'Modelagem 3D da estrutura (CAD) e exportação das peças', '[PREENCHER]', 'Concluída'],
    ['3', 'Circuito e firmware iniciais; simulação no Tinkercad', '[PREENCHER]', 'Concluída'],
    ['4', 'Compra dos componentes (Nano, servos, bateria, painel, conversores)', '[PREENCHER]', 'Concluída'],
    ['5', 'Simulador 3D com firmware emulado; correção do algoritmo (P10)', '[PREENCHER]', 'Concluída'],
    ['6', 'Simulação de dias completos; diagnóstico do sombreamento (P13)', '[PREENCHER]', 'Concluída'],
    ['7', 'Impressão 3D e montagem mecânica', '[PREENCHER]', '[PREENCHER]'],
    ['8', 'Montagem elétrica, PCI e testes físicos', '[PREENCHER]', 'Planejada'],
    ['9', 'Controlador de carga e saídas USB', '[PREENCHER]', 'Planejada'],
    ['10', 'Revisão final, formatação e apresentação', '[PREENCHER]', 'Em andamento'],
], larguras=[1.3, 9.0, 2.6, 3.0])

# =====================================================================  2 OBJETIVOS
r.h1('2 OBJETIVOS')
r.h2('2.1 Objetivo geral')
r.p('Desenvolver uma torre capaz de captar energia solar, armazená-la em uma bateria de 12 V e '
    'disponibilizá-la para a carga de telefones celulares por meio de duas portas USB, mantendo o painel '
    'fotovoltaico orientado para a região de maior luminosidade por meio de um rastreador automático de dois eixos.')
r.h2('2.2 Objetivos específicos')
r.itens([
    'estudar o funcionamento da célula fotovoltaica e a influência da orientação do painel na energia captada;',
    'projetar o armazenamento em bateria de 12 V e a adequação de tensão para os servomotores, o controlador e as saídas USB;',
    'desenvolver o circuito de sensoriamento com quatro LDRs e o firmware de controle em Arduino;',
    'modelar a estrutura mecânica em CAD para fabricação por impressão 3D;',
    'construir um simulador que execute o firmware real sobre a geometria real, permitindo testar o sistema antes da montagem;',
    'identificar, documentar e corrigir as falhas encontradas, quantificando o efeito de cada correção;',
    'propor a placa de circuito impresso e o plano de testes do protótipo físico;',
    'relacionar o projeto às disciplinas do semestre e discutir suas aplicações e sua sustentabilidade.',
], marcador='a')

# =====================================================================  3 FUNDAMENTAÇÃO
r.h1('3 FUNDAMENTAÇÃO TEÓRICA')
r.h2('3.1 Energia solar fotovoltaica')
r.ps(
    'A célula fotovoltaica é um dispositivo semicondutor, em geral de silício, formado por uma junção PN. '
    'Quando um fóton com energia suficiente é absorvido, ele libera um par elétron-lacuna; o campo elétrico '
    'interno da junção separa essas cargas e, com um circuito externo fechado, surge uma corrente contínua. '
    'Esse é o efeito fotovoltaico (Villalva; Gazoli, 2015).',
    'Uma célula isolada produz cerca de 0,5 a 0,6 V; por isso as células são associadas em série e em '
    'paralelo para formar um módulo. Um módulo de 36 células, como os de 10 W usados em sistemas de 12 V, '
    'opera tipicamente em torno de 17 a 18 V no ponto de máxima potência e chega a 21–22 V em circuito '
    'aberto. A corrente produzida é aproximadamente proporcional à irradiância incidente, enquanto a tensão '
    'varia pouco com ela e diminui com o aumento da temperatura (Pinho; Galdino, 2014).',
)
r.h2('3.2 Tensão, corrente e potência elétrica')
r.ps(
    'Tensão é a diferença de potencial elétrico entre dois pontos e mede a energia disponível por unidade '
    'de carga; corrente é o fluxo ordenado de cargas por unidade de tempo. Em corrente contínua (CC), como '
    'a de painéis e baterias, o sentido da corrente é constante; em corrente alternada (CA), como a da rede '
    'elétrica, o sentido se inverte periodicamente (Boylestad, 2012). Todo o projeto opera em CC. A potência '
    'elétrica é dada pela Equação 1:',
)
r.equacao('P = V · I', 'em que P é a potência (W), V a tensão (V) e I a corrente (A).')
r.p('Aplicada ao painel de 10 W operando em cerca de 18 V, a Equação 1 indica uma corrente da ordem de '
    'I = 10 / 18 ≈ 0,56 A em condições ideais. A energia é a potência acumulada no tempo (E = P · t) e é '
    'medida em watt-hora (Wh); é essa grandeza que importa para dimensionar a bateria e estimar quantos '
    'celulares podem ser carregados.')
r.h2('3.3 Baterias e armazenamento de energia')
r.ps(
    'Como a geração solar ocorre apenas durante o dia e varia com o tempo, a energia precisa ser armazenada '
    'para ser usada quando o usuário precisar. O projeto utiliza uma bateria selada de chumbo-ácido de 12 V, '
    'do tipo usado em alarmes e cercas elétricas, robusta e de baixo custo. A energia armazenada é o produto '
    'da tensão nominal pela capacidade: uma bateria de 12 V e [PREENCHER: capacidade, ex. 7] Ah armazena '
    'cerca de 12 × [PREENCHER] Wh, dos quais apenas parte deve ser utilizada para preservar a vida útil.',
    'A carga de uma bateria de chumbo-ácido a partir de um painel exige um **controlador de carga**. Sem ele, '
    'a tensão de circuito aberto do painel (≈ 21 V) sobrecarregaria a bateria durante o dia, causando '
    'gaseificação e perda de eletrólito, e à noite a bateria se descarregaria através do painel. O '
    'controlador limita a tensão de carga, interrompe a carga quando a bateria está cheia e desconecta a '
    'carga quando ela está excessivamente descarregada (Pinho; Galdino, 2014). Controladores do tipo PWM são '
    'simples e baratos; os do tipo MPPT extraem mais energia do painel, a um custo maior.',
)
r.h2('3.4 Sensores de luminosidade (LDR)')
r.p('O LDR é um resistor cuja resistência diminui quando a iluminância aumenta. Para um LDR comum de sulfeto '
    'de cádmio, a relação é aproximadamente uma lei de potência, apresentada na Equação 2:')
r.equacao('R = R₁₀ · (E / 10)^(−γ)', 'em que R é a resistência (Ω), E a iluminância (lux), R₁₀ a resistência a '
          '10 lux (tipicamente 10–20 kΩ) e γ ≈ 0,7 um coeficiente do material.')
r.p('Como o Arduino mede tensões e não resistências, cada LDR é ligado em um divisor de tensão com um '
    'resistor fixo de 10 kΩ. Com o LDR do lado do 5 V, a tensão na entrada analógica é dada pela Equação 3 e '
    '**aumenta com a luz**, convenção assumida pelo firmware:')
r.equacao('Vₐ = 5 · 10 000 / (R + 10 000)')
r.p(f'A Figura {r.prox_fig()} mostra as duas curvas. Note-se a faixa de saturação: acima de alguns milhares '
    'de lux a tensão se aproxima de 5 V e as diferenças entre sensores ficam muito pequenas — característica '
    'que se mostrou relevante no desenvolvimento (seção 5.7). O conversor analógico-digital do ATmega328P tem '
    '10 bits; com referência de 5 V, cada passo vale 5 / 1024 ≈ 4,9 mV.')
r.figura(f('g_ldr.png'), 'Resistência do LDR e tensão no divisor em função da iluminância (modelo da Equação 2, R₁₀ = 15 kΩ)',
         largura=13.5)
r.p('Para identificar a **direção** da luz, os quatro LDRs são montados em cruz, separados por anteparos '
    'opacos. Quando a luz vem obliquamente, os anteparos sombreiam os sensores do lado oposto; comparando as '
    'médias de cada lado (esquerda × direita e superior × inferior), o controlador sabe para onde girar.')

r.h2('3.5 Rastreamento solar e a lei do cosseno')
r.p('A potência captada por um painel é proporcional à componente da radiação perpendicular à sua superfície, '
    'conforme a Equação 4 (Duffie; Beckman, 2013):')
r.equacao('P(θ) = P₀ · cos θ', 'em que θ é o ângulo entre a direção do Sol e a normal ao painel e P₀ a potência com incidência perpendicular.')
r.p(f'A Figura {r.prox_fig()} evidencia uma propriedade importante: perto do alinhamento, a perda é pequena — '
    'um erro de 10° custa apenas 1,5%, e um erro de 18° custa 5% —, mas ela cresce rapidamente para ângulos '
    'grandes, chegando a 50% em 60°. Por isso um rastreador não precisa ser perfeito, mas não pode ficar '
    '“perdido”: um erro grosseiro de orientação é muito mais grave que um erro residual pequeno.')
r.figura(f('g_cos.png'), 'Potência relativa em função do ângulo de incidência (lei do cosseno)', largura=13)
r.p('Os rastreadores classificam-se pelo número de eixos (um eixo ou dois eixos) e pela forma de '
    'determinar a posição do Sol: os **sensoriais**, como este, usam sensores de luz em malha fechada; os '
    '**astronômicos** calculam a posição do Sol a partir de data, hora e coordenadas geográficas '
    '(Mousazadeh *et al.*, 2009). O projeto adota dois eixos — azimute (giro horizontal) e elevação '
    '(inclinação) — com rastreamento sensorial.')

r.h2('3.6 Automação e controle')
r.ps(
    'Um sistema automatizado executa uma tarefa sem intervenção humana contínua, com base em informações de '
    'sensores processadas por um controlador que comanda atuadores (Bolton, 2010). No rastreador, os sensores '
    'são os LDRs, o controlador é o microcontrolador e os atuadores são os servomotores. Como o resultado da '
    'ação (a orientação do painel) altera a própria medição (a luz nos sensores), trata-se de um controle em '
    '**malha fechada** (Ogata, 2010).',
    'A estratégia adotada é a de controle liga-desliga com zona morta (*bang-bang* com histerese): se a '
    'diferença entre os lados excede uma tolerância, o servo dá um pequeno passo fixo na direção da luz; caso '
    'contrário, permanece parado. A zona morta evita que o painel oscile indefinidamente em torno do ponto de '
    'equilíbrio por causa de ruído, ao custo de um pequeno erro residual.',
    'O servomotor é um conjunto de motor CC, redução por engrenagens, potenciômetro e circuito de controle '
    'internos. Ele recebe um pulso a cada 20 ms (50 Hz) cuja largura define o ângulo — na biblioteca Servo do '
    'Arduino, de 544 µs (0°) a 2 400 µs (180°) — e mantém essa posição por conta própria (Monk, 2017).',
    'O Arduino Nano é uma placa compacta baseada no microcontrolador ATmega328P, de 8 bits e 16 MHz, com '
    '32 KB de memória de programa, 2 KB de RAM, oito entradas analógicas e saídas PWM (Microchip Technology, '
    '2018). É programado em C/C++ por meio da plataforma Arduino, cuja simplicidade e grande comunidade o '
    'tornam adequado a protótipos acadêmicos (Monk, 2017).',
)
r.h2('3.7 Circuito de carregamento USB')
r.p('A porta USB fornece 5 V nominais. A especificação de carga de baterias da USB (*Battery Charging '
    'Specification*) define como um carregador dedicado sinaliza ao celular que pode fornecer correntes '
    'acima dos 500 mA do padrão básico, até 1,5 A, por meio das linhas de dados (USB Implementers Forum, '
    '2010). Como a bateria do projeto fornece 12 V, é necessário um conversor CC-CC abaixador (*buck*) para '
    '5 V. Conversores chaveados como o XL4015 alcançam eficiências da ordem de 90%, muito superiores às dos '
    'reguladores lineares, que dissipariam em calor mais da metade da energia nessa conversão (Boylestad, 2012). '
    'Para a segurança do usuário e do equipamento, a saída deve ter limitação de corrente e proteção contra '
    'curto-circuito, e a entrada deve ser protegida por fusível.')

# =====================================================================  4 DESENVOLVIMENTO
r.h1('4 DESENVOLVIMENTO DO PROJETO')
r.h2('4.1 Descrição geral do sistema')
r.p(f'A Figura {r.prox_fig()} apresenta o diagrama de blocos do sistema. Na cadeia de energia, o painel '
    'fotovoltaico carrega a bateria de 12 V por meio de um controlador de carga; a partir da bateria, '
    'protegida por fusível, derivam três ramos: o conversor de 5 V das saídas USB, o conversor de 6 V que '
    'alimenta os servomotores e o conversor de 7,5 V que alimenta o Arduino. Em paralelo, a malha de '
    'rastreamento — LDRs, Arduino e servos — orienta o próprio painel. Blocos tracejados indicam partes '
    'ainda em fase de projeto, sem componentes adquiridos.')
r.figura(f('d_blocos.png'), 'Diagrama de blocos da torre solar', largura=16)
r.h2('4.2 Estrutura física')
r.ps(
    'O roteiro do PIM sugere uma torre feita com tubo plástico de 5 polegadas fixado ao solo. O grupo optou '
    'por desenvolver a estrutura do mecanismo de rastreamento em CAD, com peças próprias para impressão 3D, '
    'o que permitiu acomodar os servomotores com precisão e, sobretudo, obter a geometria exata usada no '
    'simulador. A base cilíndrica do mecanismo pode ser montada no topo de um tubo de 5 polegadas, que '
    'abrigaria a bateria, os conversores e as saídas USB [PREENCHER: confirmar a solução de torre adotada pelo grupo].',
    f'A Figura {r.prox_fig()} mostra uma renderização fotorrealista da montagem, produzida a partir dos próprios '
    'arquivos STL das peças, com os servos na posição calculada pelo simulador para as 10 h do solstício de '
    'inverno em Sorocaba. O Quadro 1 descreve as peças.',
)
r.figura(f('render_heroi.png'), 'Renderização da montagem do rastreador a partir das peças do CAD (21 de junho, 10 h)',
         fonte='Elaborado pelos autores no Blender a partir dos arquivos STL do projeto, 2026.', largura=14.5)
r.tabela('Peças da estrutura impressa em 3D', ['Peça (arquivo STL)', 'Função'], [
    ['BASE_FECHAMENTO, COLUNA_INTERNA', 'Base cilíndrica e coluna que sustentam o conjunto e abrigam o servo horizontal'],
    ['PAREDE_ESTRUTURAL_01 (2×), PAREDE_APOIO_MOTOR_01', 'Caixa fixa do servo de azimute'],
    ['PRATO_GIRATORIO', 'Prato acoplado ao servo horizontal (giro de azimute)'],
    ['PAREDE_ESTRUTURAL_02 e 03, PAREDE_APOIO_MOTOR_02', 'Suportes do servo vertical, que giram com o prato'],
    ['TRAVE', 'Braço acoplado ao servo vertical, que inclina o painel (elevação)'],
    ['SUPORTE_DO_SUPORTE_LDR e SUPORTE_LDR', 'Fixação e cruz de sombra dos quatro LDRs'],
], larguras=[6.5, 9.5], quadro=True)
r.p(f'A Figura {r.prox_fig()} mostra a vista lateral, em que se distinguem os dois eixos: o prato giratório '
    '(azimute), sobre o qual se apoiam os suportes do segundo servo, e a trave articulada que inclina o painel '
    '(elevação). Os servos MG996R foram escolhidos pelo torque: com o centro do painel a cerca de 64 mm do '
    'eixo de elevação e uma massa estimada de 1 kg [PREENCHER: pesar o painel], o torque máximo exigido é '
    'dado pela Equação 5.')
r.figura(f('render_lateral.png'), 'Vista lateral: eixos de azimute (prato) e elevação (trave)',
         fonte='Elaborado pelos autores no Blender a partir dos arquivos STL do projeto, 2026.', largura=12.5)
r.equacao('τ = m · g · d = 1,0 × 9,81 × 0,064 ≈ 0,63 N·m ≈ 6,4 kgf·cm')
r.p('O MG996R fornece cerca de 9,4 kgf·cm a 4,8 V e 11 kgf·cm a 6 V; por isso o conversor dos servos foi '
    'ajustado para 6 V, garantindo margem de segurança da ordem de 70%.')
r.h2('4.3 Captação de energia')
r.p('O painel adotado é um módulo monocristalino de 10 W. Suas características elétricas de placa são: '
    'potência máxima de 10 W, tensão de máxima potência de [PREENCHER: Vmp] V, corrente de máxima potência de '
    '[PREENCHER: Imp] A e tensão de circuito aberto de [PREENCHER: Voc] V. A energia gerada será encaminhada '
    'à bateria por um controlador de carga PWM de 12 V, ainda não adquirido (seção 5.9). Com irradiação média '
    'da ordem de 4,5 a 5 kWh/m² por dia na região de Sorocaba (Pereira *et al.*, 2017), equivalente a 4,5–5 '
    'horas de sol pleno, estima-se para o painel fixo uma geração diária ideal de 45 a 50 Wh, antes das '
    'perdas do controlador e da bateria.')
r.h2('4.4 Sistema de rastreamento')
r.p(f'Os quatro LDRs ficam no suporte em cruz preso à borda superior do painel (Figura {r.prox_fig()}), '
    'identificados como superior esquerdo (SE), superior direito (SD), inferior esquerdo (IE) e inferior '
    'direito (ID). A cada ciclo, o Arduino lê os quatro sensores e calcula as médias por lado; se a diferença '
    'entre lados opostos excede a tolerância, o servo correspondente avança 2° na direção do lado mais '
    'iluminado. Quando os quatro sensores recebem a mesma luz, a cruz não produz sombra e o painel está '
    'alinhado com o Sol.')
r.figura(f('render_detalhe_ldr.png'), 'Detalhe do suporte em cruz com os quatro LDRs',
         fonte='Elaborado pelos autores no Blender a partir dos arquivos STL do projeto, 2026.', largura=12.5)

r.h2('4.5 Circuito elétrico e eletrônico')
r.p(f'O circuito foi inicialmente montado e simulado no Tinkercad Circuits (Figura {r.prox_fig()}). Como o '
    'Tinkercad não oferece o Arduino Nano, a simulação utiliza um Arduino UNO, que tem o mesmo microcontrolador '
    '(ATmega328P) e a mesma nomenclatura de pinos; o circuito e o código são, portanto, equivalentes.')
r.figura(f('diagrama_tinkercad.png'), 'Circuito de referência simulado no Tinkercad', fonte='Elaborado pelos autores no Tinkercad, 2026.', largura=15)
r.p(f'O esquemático completo do protótipo físico, com o Nano e o sistema de alimentação por bateria, está na '
    f'Figura {r.prox_fig()}; o Quadro 2 relaciona os componentes e suas funções.')
r.figura(f('d_esquematico.png'), 'Esquemático elétrico do rastreador e da alimentação', largura=16)
r.tabela('Componentes do protótipo e suas funções', ['Qtd.', 'Componente', 'Função'], [
    ['1', 'Arduino Nano (ATmega328P)', 'Lê os LDRs e comanda os servos'],
    ['4', 'LDR 5 mm + resistor 10 kΩ', 'Divisores que convertem luz em tensão (A1–A4)'],
    ['2', 'Servo MG996R (engrenagens metálicas)', 'Movimentam os eixos de azimute (D9) e elevação (D10)'],
    ['1', 'Painel monocristalino 10 W', 'Gera a energia do sistema'],
    ['1', 'Bateria selada 12 V', 'Armazena a energia'],
    ['2', 'Conversor *step-down* XL4015 (5 A)', '6,0 V para os servos; 7,5 V para o VIN do Nano'],
    ['1', 'Controlador de carga PWM 12 V (planejado)', 'Carga segura da bateria a partir do painel'],
    ['1', 'Conversor 12 V → 5 V com 2 USB (planejado)', 'Saídas de carga dos celulares'],
    ['1', 'Fusível 3 A + porta-fusível (planejado)', 'Proteção contra curto-circuito na saída da bateria'],
    ['1', 'Capacitor eletrolítico 1 000 µF / 16 V', 'Absorve os picos de corrente dos servos'],
], larguras=[1.4, 6.6, 8.0], quadro=True)
r.p('Três cuidados de projeto merecem destaque. Primeiro, os servos **não** são alimentados pelo 5 V do '
    'Arduino, como no diagrama do Tinkercad: cada MG996R pode exigir até cerca de 2,5 A quando travado, o que '
    'reiniciaria o microcontrolador. Segundo, os XL4015 devem ser ajustados com multímetro, **sem carga**, '
    'antes de qualquer ligação, pois saem de fábrica em tensão arbitrária. Terceiro, todos os terminais de '
    'referência (GND) — bateria, conversores, servos e Arduino — precisam ser interligados.')

r.h2('4.6 Programação e controle')
r.p(f'O firmware foi escrito em C++ na plataforma Arduino e usa apenas a biblioteca padrão Servo, o que '
    f'garante compatibilidade com o Tinkercad. Compilado para o Nano, ocupa 4 122 bytes de memória de '
    f'programa (13%) e 318 bytes de RAM (15%). A Figura {r.prox_fig()} apresenta o fluxograma e o Quadro 3 os '
    f'parâmetros de ajuste.')
r.figura(f('d_fluxograma.png'), 'Fluxograma do firmware de rastreamento', largura=7.8)
r.tabela('Parâmetros do firmware', ['Parâmetro', 'Valor', 'Significado'], [
    ['TOLERANCIA', '40 (≈ 0,2 V)', 'Zona morta: diferença mínima entre lados para mover'],
    ['PASSO', '2°', 'Deslocamento por ciclo quando há desequilíbrio'],
    ['Limites dos servos', '20° a 160°', 'Protegem a estrutura impressa contra colisões'],
    ['Posição inicial', '90° / 90°', 'Painel na horizontal ao ligar'],
    ['Período do laço', '≈ 100 ms', 'Dominado pela telemetria serial a 9 600 baud (seção 5.3)'],
    ['Velocidade máxima', '≈ 20°/s por eixo', '2° a cada 100 ms'],
], larguras=[4.2, 3.4, 8.4], quadro=True)
r.p('O Quadro 4 mostra o núcleo da lógica. A leitura dos sensores é convertida em médias por lado, e cada '
    'eixo é corrigido de forma independente; a variável `sentidoHorizontal` é resultado de uma das correções '
    'descritas na seção 5.5.')
r.codigo('''// Médias por lado
int esquerda = (supEsq + infEsq) / 2;
int direita  = (supDir + infDir) / 2;
int superior = (supEsq + supDir) / 2;
int inferior = (infEsq + infDir) / 2;

// Sentido do giro horizontal: inverte quando o painel
// passa da vertical (correção P10)
int sentidoHorizontal = (anguloVertical >= 90) ? 1 : -1;

if (esquerda > direita + TOLERANCIA)
  anguloHorizontal += sentidoHorizontal * PASSO;
else if (direita > esquerda + TOLERANCIA)
  anguloHorizontal -= sentidoHorizontal * PASSO;

if (superior > inferior + TOLERANCIA)
  anguloVertical -= PASSO;
else if (inferior > superior + TOLERANCIA)
  anguloVertical += PASSO;

anguloHorizontal = constrain(anguloHorizontal, 20, 160);
anguloVertical   = constrain(anguloVertical, 20, 160);''', 'Núcleo do algoritmo de rastreamento')
r.p('A cada ciclo, o firmware também envia pelo monitor serial uma linha com as médias e os ângulos, por '
    'exemplo `Esquerda: 921 | Direita: 614 | Superior: 767 | Inferior: 767 | Horizontal: 92 | Vertical: 90`. '
    'Essa telemetria é a principal ferramenta de calibração e foi usada em todas as análises deste trabalho.')

r.h2('4.7 Simulação')
r.ps(
    'Além do Tinkercad, que valida a lógica elétrica, o grupo desenvolveu um **simulador 3D** próprio, '
    'executado no navegador, para responder a uma pergunta que o Tinkercad não responde: *o painel realmente '
    'segue o Sol, com esta estrutura e este código?* O simulador tem três partes:',
)
r.itens([
    '**cérebro**: o arquivo `.hex` gerado pela compilação do `main.c` é executado instrução por instrução em um ATmega328P emulado a 16 MHz (biblioteca avr8js), com temporizadores, conversor A/D e porta serial; os ângulos dos servos são obtidos medindo a largura dos pulsos nos pinos D9 e D10, exatamente como o servo real faria;',
    '**corpo**: as peças STL do CAD são carregadas na posição de montagem e agrupadas em parte fixa, parte que gira com o azimute e parte que inclina com a elevação;',
    '**olhos**: a luz em cada LDR é calculada lançando raios do sensor em direção ao Sol e verificando se alguma peça os bloqueia (*raycasting*); a iluminância é convertida em tensão pelas Equações 2 e 3 e entregue ao conversor A/D emulado, com variação entre sensores (±10%) e ruído (5 mV).',
])
r.p(f'A Figura {r.prox_fig()} mostra a interface: o Sol pode ser arrastado com o mouse ou seguir a trajetória '
    'real de um dia, calculada para qualquer data e latitude; o painel lateral exibe as leituras, os ângulos, '
    'o monitor serial e a energia acumulada em comparação com uma placa fixa voltada ao Norte e inclinada na '
    'latitude local. Os resultados de energia são expressos em unidade relativa (u.r.), pois o modelo usa '
    'intensidade de luz direta constante (1 000 lux) e não considera a atenuação atmosférica nem a '
    'temperatura; servem para **comparar** alternativas, não para prever a geração real em Wh.')
r.figura(f('simulador_3d.png'), 'Simulador 3D: firmware real emulado sobre as peças do CAD',
         fonte='Elaborado pelos autores (simulador do projeto), 2026.', largura=16)

r.h2('4.8 Placa de circuito impresso')
r.p(f'Para substituir a protoboard e os jumpers, que não suportam a corrente dos servos nem a vibração da '
    f'estrutura, foi proposta a PCI da Figura {r.prox_fig()}. O Arduino Nano é encaixado em barras de pinos '
    f'(U1); os quatro resistores de 10 kΩ ficam próximos às entradas analógicas, e os LDRs são ligados por '
    f'conectores (J1–J4), pois ficam no alto da estrutura. Os servos usam conectores de três vias (J5, J6), e a '
    f'alimentação entra por bornes parafusáveis (J7: 6 V dos servos; J8: 7,5 V do Nano). As trilhas de potência '
    f'dos servos são mais largas, e o capacitor C1 fica junto aos conectores dos servos. A placa de 90 × 65 mm '
    f'cabe na base da estrutura e é fixada por quatro furos de 3 mm.')
r.figura(f('d_pci.png'), 'Proposta de leiaute da placa de circuito impresso (face das trilhas)', largura=14)
r.p('O desenho é uma proposta de leiaute para orientar a fabricação; a versão definitiva deve ser roteada em '
    'software de projeto eletrônico, com verificação de regras elétricas e geração dos arquivos de fabricação '
    '[PREENCHER: software adotado pelo grupo e forma de fabricação — corrosão, fresagem ou serviço externo].')

r.h2('4.9 Montagem e testes')
r.p('Os testes previstos para o protótipo físico estão na Tabela 2. Até esta versão do relatório, os '
    'testes físicos **não foram realizados**; os resultados apresentados neste trabalho são de simulação e '
    'estão identificados como tal.')
r.tabela('Plano de testes do protótipo físico', ['ID', 'Teste', 'Critério de aceitação', 'Resultado'], [
    ['F-00', 'Ajuste dos XL4015 sem carga, com multímetro', '6,0 V (servos) e 7,5 V (Nano) ± 0,1 V', '[PREENCHER]'],
    ['F-01', 'Tensão do painel ao sol (aberto e com carga)', 'Voc ≈ 21 V; ≈ 17–18 V com carga', '[PREENCHER]'],
    ['F-02', 'Carga da bateria com controlador', 'Tensão sobe ao sol e se estabiliza em ≈ 13,8–14,4 V', '[PREENCHER]'],
    ['F-03', 'Movimento com lanterna em arco', 'Painel acompanha a lanterna nos dois eixos', '[PREENCHER]'],
    ['F-04', 'Lanterna parada', 'Painel estabiliza sem oscilar', '[PREENCHER]'],
    ['F-05', 'Torque na elevação', 'Servo segura o painel em 20° e 160° sem ceder', '[PREENCHER]'],
    ['F-06', 'Arduino não reinicia ao mover os servos', 'Sem reinícios em 10 min de operação', '[PREENCHER]'],
    ['F-07', 'Tensão nas duas saídas USB, com e sem carga', '5,0 V ± 5% até 1 A em cada saída', '[PREENCHER]'],
    ['F-08', 'Carga simultânea de dois celulares', 'Ambos indicam carregamento', '[PREENCHER]'],
    ['F-09', 'Rastreamento ao sol real por algumas horas', 'Erro visual pequeno; ganho sobre placa fixa', '[PREENCHER]'],
], larguras=[1.4, 5.6, 5.9, 3.1])

r.h2('4.10 Custos')
r.p('A Tabela 3 apresenta os custos dos componentes. Os valores dos itens eletrônicos de pequeno porte '
    'foram obtidos no orçamento da loja de componentes; os demais devem ser completados com os valores '
    'efetivamente pagos.')
r.tabela('Custos dos componentes', ['Item', 'Qtd.', 'Valor unit. (R$)', 'Total (R$)'], [
    ['Sensor LDR 5 mm', '4', '0,45', '1,80'],
    ['Resistor 10 kΩ 1/4 W', '4', '0,05', '0,20'],
    ['Jumper Dupont macho-fêmea 20 cm', '40', '0,05', '2,00'],
    ['Jumper Dupont macho-macho 20 cm', '40', '0,06', '2,40'],
    ['Arduino Nano', '1', '[PREENCHER]', '[PREENCHER]'],
    ['Servo MG996R', '2', '[PREENCHER]', '[PREENCHER]'],
    ['Conversor XL4015', '2', '[PREENCHER]', '[PREENCHER]'],
    ['Bateria selada 12 V', '1', '[PREENCHER]', '[PREENCHER]'],
    ['Painel solar 10 W', '1', '[PREENCHER]', '[PREENCHER]'],
    ['Filamento para impressão 3D', '[PREENCHER]', '[PREENCHER]', '[PREENCHER]'],
    ['Controlador de carga, módulo USB, fusível (a adquirir)', '—', '[PREENCHER]', '[PREENCHER]'],
    ['**Total**', '', '', '**[PREENCHER]**'],
], fonte='Orçamento da loja de componentes e notas de compra do grupo, 2026.', larguras=[8.0, 1.8, 3.1, 3.1])

# =====================================================================  5 HISTÓRICO
r.h1('5 HISTÓRICO DO DESENVOLVIMENTO: ERROS E ACERTOS')
r.ps(
    'Este capítulo registra, em ordem cronológica, os problemas encontrados durante o desenvolvimento, a '
    'forma como cada um foi descoberto, sua causa e a solução adotada ou proposta. O objetivo é mostrar que '
    'o projeto não seguiu uma linha reta: várias hipóteses iniciais estavam erradas, e algumas falhas só '
    'apareceram quando o sistema completo — código, eletrônica e mecânica — foi testado em conjunto.',
    f'A Figura {r.prox_fig()} resume a trajetória. Os códigos entre parênteses (P1, P10...) correspondem à '
    'lista de problemas conhecidos mantida no repositório do projeto.',
)
r.figura(f('d_linha_do_tempo.png'), 'Linha do tempo do desenvolvimento: erros, acertos e situação de cada item', largura=15.5)

r.h2('5.1 O ponto de partida')
r.p('O projeto começou com o circuito no Tinkercad, o modelo 3D da estrutura e um firmware simples, que '
    'compilava sem erros e se comportava bem na simulação elétrica. A primeira tarefa foi uma revisão '
    'cuidadosa de tudo o que existia — código, diagrama e peças —, antes de comprar ou montar qualquer coisa. '
    'Essa decisão se mostrou acertada: a maior parte dos problemas a seguir teria sido muito mais difícil de '
    'diagnosticar no protótipo físico.')

r.h2('5.2 Divergência de pinos entre código e diagrama (P1)')
r.ps(
    '**Como foi descoberto:** na revisão, notou-se que o código lê os LDRs nas entradas **A1 a A4**, enquanto '
    'no diagrama do Tinkercad os fios saem de **A0 a A3**. A diferença é sutil — um deslocamento de um pino — '
    'e passa despercebida em uma leitura rápida.',
    '**Consequência:** montado como no diagrama, o firmware leria em A4 um pino sem nada ligado, cuja tensão '
    f'“flutua” de forma imprevisível, e deixaria de ler o sensor ligado em A0. A Figura {r.prox_fig()} mostra o '
    'efeito em simulação: com a fiação esperada pelo código, o erro de apontamento cai para 18° em poucos '
    'segundos; com a fiação do diagrama, o painel vagueia e termina a 90° do Sol.',
)
r.figura(f('g_fiacao.png'), 'Efeito da fiação dos LDRs no erro de apontamento (simulação, 21 de junho, 10 h)', largura=13)
r.p('**Situação:** pendente de decisão do grupo. A correção é trivial — alterar o código para A0–A3 ou '
    'religar os fios —, mas depende de qual das duas versões reflete a montagem física. Optou-se por não '
    'alterar nenhum dos lados sem essa confirmação. **Lição:** o diagrama e o código são documentos do mesmo '
    'sistema e precisam ser conferidos um contra o outro.')

r.h2('5.3 Estimativa versus medição: o período do laço')
r.ps(
    'Na primeira análise do código, estimou-se o período do laço de controle em cerca de 150 ms: 50 ms do '
    '`delay` mais aproximadamente 100 ms para transmitir os cerca de 95 caracteres da telemetria a 9 600 baud. '
    'Quando o firmware passou a ser executado no emulador, porém, mediu-se um período de **0,098 s**.',
    'A explicação está no funcionamento da porta serial: o Arduino possui um *buffer* de transmissão de 64 '
    'bytes. O comando de impressão só bloqueia até sobrar espaço no *buffer*; o restante da linha continua '
    'sendo transmitido *em segundo plano* durante o `delay`. A estimativa somava duas coisas que, na verdade, '
    'acontecem ao mesmo tempo. **Lição:** sempre que possível, medir em vez de estimar — a documentação do '
    'projeto foi corrigida para ≈ 100 ms e velocidade máxima de ≈ 20°/s por eixo.',
)

r.h2('5.4 Um acerto: testar antes de montar')
r.p('A decisão mais produtiva do projeto foi construir o simulador descrito na seção 4.7, executando o '
    'binário real e não uma reimplementação do algoritmo. Isso significa que qualquer erro do código — de '
    'lógica, de temporização ou de pinos — aparece no simulador exatamente como apareceria no Arduino. '
    'Combinado com a geometria real das peças, o simulador revelou três falhas que dificilmente seriam '
    'percebidas por inspeção do código, descritas a seguir.')

r.h2('5.5 A inversão do eixo horizontal (P10)')
r.ps(
    '**Como foi descoberto:** com o Sol posicionado a Nordeste ou a Noroeste, o painel o seguia corretamente. '
    'Com o Sol a Sudeste ou a Sudoeste, porém, o servo horizontal girava continuamente *para longe* do Sol até '
    'parar no fim de curso, enquanto o erro de apontamento crescia.',
    '**Causa:** os LDRs giram junto com o painel, de modo que “esquerda” e “direita” são medidas no '
    'referencial do próprio painel. Quando o servo vertical passa de 90°, o painel fica voltado para o lado '
    'oposto do céu — e, vista desse lado, a mesma rotação do prato desloca o Sol no sentido contrário em '
    'relação aos sensores. O firmware original aplicava sempre o mesmo sentido de correção; em metade da '
    'faixa de elevação, portanto, ele corrigia o erro na direção errada. O defeito independe do sentido de '
    'montagem dos servos: inverter um servo apenas troca qual metade da faixa falha.',
    '**Solução:** tornar o sentido da correção horizontal dependente do lado em que o painel está, por meio da '
    f'variável `sentidoHorizontal` (Quadro 4). A Figura {r.prox_fig()} compara os dois firmwares em simulação, '
    'com o Sol a Sudeste e 40° de altura: o original leva o servo horizontal a 160° (fim de curso) e termina '
    'com 53° de erro; o corrigido converge em menos de três segundos para 18°.',
)
r.figura(f('g_p10_inversao.png'), 'Firmware original × corrigido com o Sol a Sudeste, 40° de altura (simulação)', largura=16)
r.tabela('Erro de apontamento final antes e depois da correção P10 (simulação, 6 s após ligar)',
         ['Posição do Sol', 'Firmware original', 'Firmware corrigido'], [
    ['Sudeste, 40° de altura', '53° (horizontal travado em 160°)', '18°'],
    ['Sudoeste, 35° de altura', '58° (horizontal travado em 20°)', '17°'],
    ['Nordeste, 30° / Noroeste, 35°', '17–18°', '17–18° (sem alteração)'],
    ['Leste, 55° / Oeste, 50° (vertical cruza 90°)', '—', '18°, sem oscilação na transição'],
], larguras=[6.0, 5.4, 4.6])

r.h2('5.6 Um erro de método: os testes contaminados')
r.ps(
    'Ao validar a correção P10, cometeu-se um erro de método que merece registro. Para testar vários cenários '
    'rapidamente, a posição dos servos no simulador era “reposicionada” entre um teste e outro, sem '
    'reiniciar o Arduino emulado. O problema é que o firmware guarda os próprios ângulos nas variáveis '
    '`anguloHorizontal` e `anguloVertical`; no ciclo seguinte, ele simplesmente reescrevia nos servos os '
    'ângulos que tinha na memória, desfazendo o reposicionamento. Cada teste, portanto, começava de onde o '
    'anterior havia terminado, e não da condição declarada.',
    'O erro foi percebido porque dois cenários diferentes produziram resultados idênticos. A solução foi '
    'criar no simulador a função `reiniciar()`, que equivale a pressionar o botão *reset* do Arduino: o '
    'firmware volta ao `setup()` e os servos a 90°/90°. Todos os testes foram refeitos a partir do '
    '*reset*, e os resultados das seções 5.2 e 5.5 já são os corrigidos. **Lição:** em sistemas com memória '
    '(estado interno), um teste só é válido se a condição inicial for conhecida — exatamente o que o *reset* '
    'garante no equipamento real.',
)

r.h2('5.7 O erro residual: saturação dos LDRs e zona morta (P11)')
r.p('Mesmo com o algoritmo corrigido, o painel estabiliza com 12° a 18° de erro em vez de 0°. A causa é a '
    'combinação de dois fatores: com luz forte, os quatro divisores ficam próximos de 5 V (Figura 1, seção 3.4), e a '
    'diferença entre lados cai abaixo da tolerância de 40 unidades antes de o alinhamento ser perfeito. '
    'Pela lei do cosseno, um erro de 18° custa cerca de 5% da potência — aceitável. Sob sol pleno (≈ 100 000 '
    'lux), porém, os LDRs saturam quase completamente. As melhorias propostas são reduzir o resistor fixo para '
    '1–2,2 kΩ, aumentar a altura dos anteparos e usar uma tolerância relativa, proporcional à soma das '
    'leituras, em vez de um valor absoluto. **Situação:** pendente, a ser ajustado com medições ao sol real.')

r.h2('5.8 Versionamento: o arquivo que não estava lá')
r.p('O projeto é mantido em um repositório Git, com histórico de todas as alterações. Ao versionar o '
    'simulador, descobriu-se que a regra que ignora arquivos `.hex` — correta para resultados de compilação '
    'temporários — também excluía o firmware compilado que o simulador precisa. Qualquer pessoa que baixasse '
    'o projeto veria o simulador falhar por falta do arquivo. A regra foi refinada para permitir esse arquivo '
    'específico. **Lição:** configurações “sensatas” também precisam ser testadas a partir de uma cópia limpa.')

r.h2('5.9 Do protótipo de simulação ao hardware real (P12)')
r.ps(
    'O circuito do Tinkercad usava um Arduino UNO alimentado pela porta USB, com os servos ligados ao 5 V da '
    'própria placa — solução que funciona em simulação, mas não com servos de alto torque. Na compra dos '
    'componentes, o grupo adotou o Arduino Nano (menor, mesmo microcontrolador), servos MG996R de engrenagens '
    'metálicas, uma bateria de 12 V e dois conversores XL4015, compondo um sistema autônomo. A documentação do '
    'projeto foi revisada para refletir o material efetivamente adquirido.',
    'Na revisão da lista de compras, identificou-se a ausência do **controlador de carga** (P12). Ligar o '
    'painel diretamente à bateria a sobrecarregaria durante o dia e a descarregaria à noite (seção 3.3). '
    'Também não constam fusível, capacitor dos servos e cabos de bitola adequada. **Situação:** pendente de '
    'aquisição [PREENCHER: confirmar se o grupo já possui algum desses itens].',
)

r.h2('5.10 A sombra que o próprio painel projeta (P13)')
r.ps(
    'A descoberta mais importante surgiu quando o sistema foi simulado ao longo de **dias inteiros**, e não '
    'apenas em posições fixas do Sol. No solstício de verão (21 de dezembro), o rastreador captou 48% mais '
    'energia que a placa fixa. No solstício de inverno (21 de junho), entretanto, o resultado foi o oposto: '
    'partindo da posição horizontal ao amanhecer, o painel inclinou-se para o lado errado e permaneceu '
    'voltado para o Sul durante todo o dia, captando **74% menos** energia que a placa fixa.',
    '**Primeira hipótese:** para investigar, foi criada no simulador uma função de diagnóstico que informa, '
    'para cada LDR, qual peça bloqueia o raio em direção ao Sol. Com o Sol baixo vindo do lado “inferior” do '
    'painel, os sensores inferiores — justamente os que deveriam estar iluminados — apareciam no escuro. A '
    'análise da geometria mostrou que, no CAD, o suporte dos LDRs fica preso à borda da trave cerca de 13 mm '
    '**abaixo** do plano do painel. Com luz rasante vinda desse lado, o próprio painel e a trave sombreiam os '
    'sensores inferiores; o firmware interpreta que há mais luz “em cima” e inclina o painel no sentido '
    'contrário ao Sol — e quanto mais se afasta, mais a sombra se mantém.',
    '**Um falso negativo:** a primeira simulação com o suporte elevado não mostrou melhora. Antes de '
    'descartar a hipótese, verificou-se que o navegador havia usado uma versão antiga, em *cache*, do código '
    'da montagem — a simulação, na verdade, ainda usava a geometria original. Com os arquivos atualizados, o '
    'resultado mudou completamente. O episódio reforçou a lição da seção 5.6: antes de concluir, confirmar '
    'que o experimento testou o que se pretendia testar.',
    f'**Confirmação:** com o suporte dos LDRs elevado 25 mm, de modo que os sensores fiquem acima do plano do '
    f'painel, o rastreador passa a seguir o Sol durante todo o dia de junho, com erro abaixo de 20° das 8h40 '
    f'às 17h e ganho de **33%** sobre a placa fixa (Figura {r.prox_fig()}). Em dezembro, quando o Sol passa '
    f'pelo outro lado do painel, as duas geometrias têm o mesmo desempenho (Figura {r.prox_fig(2)}).',
)
r.figura(f('g_dia_junho.png'), 'Simulação de 21 de junho: geometria do CAD × LDRs elevados 25 mm', largura=16)
r.figura(f('g_dia_dezembro.png'), 'Simulação de 21 de dezembro: geometria do CAD × LDRs elevados 25 mm', largura=16)
r.p(f'A Figura {r.prox_fig()} resume a energia diária nos quatro cenários. **Solução proposta:** acrescentar '
    'um espaçador de 25 mm (ou reimprimir o `SUPORTE_DO_SUPORTE_LDR` com essa altura) para que os sensores '
    'fiquem acima do painel. **Ressalva:** a posição exata do painel sobre a trave e a espessura da moldura '
    'do painel real foram estimadas; a hipótese deve ser confirmada no protótipo, por exemplo iluminando o '
    'painel com uma lanterna rasante vinda de baixo.')
r.figura(f('g_energia_resumo.png'), 'Energia diária simulada: placa fixa × rastreador (latitude −23,55°)', largura=13)

r.h2('5.11 A noite e o retorno ao Leste (P7)')
r.ps(
    'O firmware não tem tratamento para a noite: quando o Sol se põe, os quatro LDRs ficam escuros, nenhum '
    'lado prevalece e o painel simplesmente para onde estava — voltado para o Oeste. Para medir o efeito, '
    'simulou-se a passagem de um dia para o outro **sem reiniciar o Arduino** e comparou-se com o caso em que '
    'o sistema é ligado de manhã, partindo da posição inicial de 90°/90°.',
    f'O resultado está na Figura {r.prox_fig()}. Partindo da posição de repouso, o painel encontra o Sol em '
    'torno das 8h50 e às 9h50 o erro é de apenas 2°. Sem o retorno, o painel amanhece de costas para o Sol '
    '(erro de 110° às 7h), recebe pouca luz nos sensores e só se realinha perto das 10h45: perde-se mais de '
    'uma hora e meia de rastreamento eficiente justamente na parte da manhã.',
)
r.figura(f('g_noite.png'), 'Manhã de 21 de junho com e sem retorno noturno à posição inicial (simulação, LDRs elevados)', largura=13.5)
r.p('**Solução proposta:** detectar a noite pela soma das quatro leituras abaixo de um limiar durante alguns '
    'minutos e, então, levar o painel a uma posição de espera voltada ao nascente (ou simplesmente '
    'reiniciar o controle na posição 90°/90°, que já se mostrou eficaz). A implementação é simples e fica '
    'como próxima melhoria do firmware.')

r.h2('5.12 Lições aprendidas')
r.tabela('Síntese dos problemas, soluções e lições', ['Problema', 'Como foi encontrado', 'Situação', 'Lição'], [
    ['P1 – Pinos A1–A4 × A0–A3', 'Revisão de código × diagrama', 'Pendente', 'Conferir documentos entre si'],
    ['Período do laço', 'Medição no emulador', 'Corrigido', 'Medir em vez de estimar'],
    ['P10 – Inversão horizontal', 'Simulador, Sol ao Sul', 'Corrigido', 'Pensar no referencial do sensor'],
    ['Testes contaminados', 'Resultados idênticos suspeitos', 'Corrigido', 'Condição inicial conhecida (*reset*)'],
    ['P11 – Erro residual', 'Simulador', 'Pendente', 'Sensores têm faixa útil'],
    ['Firmware fora do Git', 'Cópia limpa do projeto', 'Corrigido', 'Testar a partir do zero'],
    ['P12 – Controlador de carga', 'Revisão da lista de compras', 'Pendente', 'Projeto completo antes de comprar'],
    ['P13 – Sombra do painel', 'Simulação de dias inteiros', 'Proposta', 'Integrar mecânica e eletrônica'],
    ['P7 – Retorno noturno', 'Simulação da madrugada', 'Proposta', 'Prever todos os estados do sistema'],
], larguras=[4.4, 4.4, 2.4, 4.8], quadro=True)

# =====================================================================  6 APLICAÇÕES
r.h1('6 APLICAÇÕES DO PROJETO')
r.p('A torre solar para carga de celulares atende a uma necessidade cotidiana — o celular descarregado '
    'longe de uma tomada — com uma fonte renovável e sem ligação à rede elétrica. Entre as aplicações '
    'possíveis, algumas exigindo adequações técnicas, destacam-se:')
r.itens([
    '**parques e praças públicas**, onde não há tomadas disponíveis e a instalação elétrica teria custo elevado;',
    '**universidades e escolas**, em áreas de convivência, como ponto de carga e também como recurso didático sobre energia renovável;',
    '**pontos de ônibus, filas e salas de espera**, onde as pessoas permanecem por algum tempo;',
    '**eventos ao ar livre e áreas rurais**, como solução temporária ou isolada da rede;',
    '**situações de emergência**, como apoio à comunicação após desastres que interrompam o fornecimento de energia.',
])
r.p('Para uso público, seriam necessárias adequações: estrutura metálica ou de tubo plástico resistente a '
    'intempéries e vandalismo, painel de maior potência (50 a 100 W), bateria de maior capacidade, saídas USB '
    f'com proteção individual e grau de proteção contra água e poeira adequado. O Quadro {r.prox_tab(quadro=True)} resume vantagens e limitações.')
r.tabela('Vantagens e limitações da torre solar', ['Vantagens', 'Limitações'], [
    ['Energia renovável, sem custo de operação', 'Depende da luminosidade e do clima'],
    ['Independe da rede elétrica', 'Capacidade limitada pela bateria'],
    ['Rastreamento aumenta a energia captada', 'Partes móveis exigem manutenção (servos, articulações)'],
    ['Recurso educativo e visível', 'Custo de implantação maior que o de uma tomada comum'],
    ['Instalação simples, modular', 'Exige proteção contra vandalismo e intempéries'],
], larguras=[8, 8], quadro=True)
r.p('Uma estimativa ilustra a capacidade do protótipo. Um celular com bateria de 4 000 mAh a 3,85 V armazena '
    'cerca de 15,4 Wh; considerando perdas de 15% na conversão para USB e na carga, cada recarga completa '
    'consome cerca de 18 Wh da bateria. Com geração diária da ordem de 45 Wh (seção 4.3), o painel de 10 W '
    'sustentaria aproximadamente duas recargas completas por dia — número que o rastreamento pode elevar.')

# =====================================================================  7 DISCIPLINAS
r.h1('7 RELAÇÃO COM AS DISCIPLINAS DO CURSO')
r.p(f'O Quadro {r.prox_tab(quadro=True)} relaciona as disciplinas do semestre às partes do projeto em que foram efetivamente aplicadas.')
r.tabela('Contribuição das disciplinas para o projeto', ['Disciplina', 'Aplicação no projeto'], [
    ['Instalações Elétricas Industriais', 'Dimensionamento da alimentação, fusível, interligação de terras, cabos adequados à corrente dos servos (seção 4.5)'],
    ['Circuitos Elétricos', 'Divisor de tensão dos LDRs (Equação 3), potência do painel (Equação 1), conversores CC-CC, análise de correntes'],
    ['Física', 'Efeito fotovoltaico, lei do cosseno (Equação 4), torque no eixo de elevação (Equação 5), movimento aparente do Sol'],
    ['Cálculo II', 'Funções trigonométricas e potência na modelagem do LDR e da incidência; energia como integral da potência no tempo (simulação de dias)'],
    ['Linguagem de Programação Aplicada', 'Firmware em C++, leitura analógica, controle dos servos, telemetria serial; scripts de simulação e análise'],
    ['Metodologia Científica', 'Formulação e teste de hipóteses (seções 5.6 e 5.10), registro de resultados, citações e referências'],
], larguras=[5.2, 10.8], quadro=True)

# =====================================================================  8 SUSTENTABILIDADE
r.h1('8 SUSTENTABILIDADE E EFICIÊNCIA ENERGÉTICA')
r.ps(
    'O projeto utiliza uma fonte renovável e reduz a dependência da rede elétrica para uma demanda pequena, '
    'mas permanente e pulverizada, que é a carga de celulares. Ainda que a economia individual seja modesta, '
    'a solução tem valor demonstrativo: torna visível, em espaço público, que a energia pode ser gerada e '
    'consumida no mesmo lugar.',
    'A eficiência foi considerada em cada etapa. O rastreamento busca maximizar a energia captada pelo mesmo '
    'painel — nas simulações, até 33% a 48% a mais que uma placa fixa, valores coerentes com a faixa relatada '
    'na literatura (Mousazadeh *et al.*, 2009), embora superestimados pelo modelo simplificado. Os conversores '
    'chaveados XL4015, com eficiência da ordem de 90%, evitam o desperdício dos reguladores lineares. O '
    'controle com zona morta reduz o número de movimentos dos servos e, portanto, o consumo do próprio '
    'rastreador, que deve ser sempre pequeno diante do ganho de energia que proporciona.',
    'Há ainda aspectos a melhorar: o consumo dos servos em repouso, a vida útil e o descarte da bateria de '
    'chumbo-ácido — que deve ser devolvida ao fabricante ou a pontos de coleta — e o uso de filamentos mais '
    'resistentes ao sol, como o PETG, para prolongar a vida das peças impressas.',
)

# =====================================================================  9 CONCLUSÃO
r.h1('9 CONCLUSÃO')
r.ps(
    'O objetivo de projetar uma torre solar com rastreamento automático para carga de celulares foi '
    'atendido no nível de projeto e de simulação, e parcialmente no nível de protótipo físico. O subsistema '
    'de rastreamento está especificado, modelado em CAD, com firmware funcional e validado em um simulador '
    'que executa o código real sobre a geometria real; os componentes principais foram adquiridos. A '
    'captação e o armazenamento estão projetados, mas dependem da aquisição do controlador de carga; as '
    'duas saídas USB e a PCI estão projetadas e ainda não foram construídas nem testadas [PREENCHER: '
    'atualizar conforme o andamento da montagem].',
    'O principal resultado do trabalho, contudo, foi o processo. A combinação de revisão sistemática e '
    'simulação permitiu encontrar e corrigir, antes da montagem, uma inversão no algoritmo que levaria o '
    'painel ao fim de curso, um erro de método que teria invalidado os testes e um problema de geometria — o '
    'sombreamento dos sensores pelo próprio painel — que comprometeria o funcionamento em boa parte do ano. '
    'Em simulação, a correção do algoritmo reduziu o erro de 53° para 18°, e a elevação dos sensores '
    'transformou uma perda de 74% em um ganho de 33% no inverno.',
    'Como oportunidades de melhoria para a próxima versão, recomenda-se:',
)
r.itens([
    'resolver a divergência de pinos (P1) e confirmar a montagem real;',
    'elevar o suporte dos LDRs em cerca de 25 mm (P13) e validar com lanterna rasante;',
    'implementar o retorno noturno à posição inicial (P7);',
    'reduzir a saturação dos LDRs com resistor fixo menor e tolerância relativa (P11);',
    'adquirir o controlador de carga, o fusível e o módulo USB (P12) e fabricar a PCI;',
    'medir tensão e corrente do painel ao sol, com e sem rastreamento, para obter o ganho real em Wh;',
    'avaliar um controle proporcional, com passo variável conforme o erro, para convergência mais rápida.',
], marcador='a')

# =====================================================================  REFERÊNCIAS
r.titulo_sem_numero('REFERÊNCIAS')
refs = [
    'BIBLIOTECA DA UNIVERSIDADE PAULISTA – UNIP. **Guia de normalização para apresentação de trabalhos acadêmicos da Universidade Paulista**: ABNT. São Paulo: UNIP, 2025. Disponível em: https://unip.br/servicos/biblioteca/guia.aspx. Acesso em: 4 nov. 2026.',
    'BOLTON, W. **Mecatrônica**: uma abordagem multidisciplinar. 4. ed. Porto Alegre: Bookman, 2010.',
    'BOYLESTAD, R. L. **Introdução à análise de circuitos**. 12. ed. São Paulo: Pearson Prentice Hall, 2012.',
    'DUFFIE, J. A.; BECKMAN, W. A. **Solar engineering of thermal processes**. 4. ed. Hoboken: Wiley, 2013.',
    'MICROCHIP TECHNOLOGY. **ATmega328P**: 8-bit AVR microcontroller with 32K bytes in-system programmable flash: datasheet. Chandler, 2018. Disponível em: https://www.microchip.com/en-us/product/ATmega328P. Acesso em: 4 nov. 2026.',
    'MONK, S. **Programação com Arduino**: começando com sketches. 2. ed. Porto Alegre: Bookman, 2017.',
    'MOUSAZADEH, H.; KEYHANI, A.; JAVADI, A.; MOBLI, H.; ABRINIA, K.; SHARIFI, A. A review of principle and sun-tracking methods for maximizing solar systems output. **Renewable and Sustainable Energy Reviews**, v. 13, n. 8, p. 1800-1818, 2009. DOI: https://doi.org/10.1016/j.rser.2009.01.022.',
    'OGATA, K. **Engenharia de controle moderno**. 5. ed. São Paulo: Pearson Prentice Hall, 2010.',
    'PEREIRA, E. B.; MARTINS, F. R.; GONÇALVES, A. R.; COSTA, R. S.; LIMA, F. J. L.; RÜTHER, R.; ABREU, S. L.; TIEPOLO, G. M.; PEREIRA, S. V.; SOUZA, J. G. **Atlas brasileiro de energia solar**. 2. ed. São José dos Campos: INPE, 2017. Disponível em: https://labren.ccst.inpe.br/atlas_2017.html. Acesso em: 4 nov. 2026.',
    'PINHO, J. T.; GALDINO, M. A. (org.). **Manual de engenharia para sistemas fotovoltaicos**. Rio de Janeiro: CEPEL – CRESESB, 2014.',
    'USB IMPLEMENTERS FORUM. **Battery Charging Specification**: revision 1.2. [S. l.]: USB-IF, 2010. Disponível em: https://www.usb.org/document-library/battery-charging-v12-spec-and-adopters-agreement. Acesso em: 4 nov. 2026.',
    'VILLALVA, M. G.; GAZOLI, J. R. **Energia solar fotovoltaica**: conceitos e aplicações. 2. ed. São Paulo: Érica, 2015.',
]
for ref in refs:
    r.p(ref, estilo='Referencia', recuo=False)

# =====================================================================  APÊNDICES
r.titulo_sem_numero('APÊNDICE A – CÓDIGO-FONTE DO FIRMWARE')
codigo = open(os.path.join(RAIZ, 'main.c'), encoding='utf-8').read()
r.codigo(codigo)
r.titulo_sem_numero('APÊNDICE B – REPRODUÇÃO DAS SIMULAÇÕES E FIGURAS')
r.p('Todo o material deste relatório está no repositório do projeto e pode ser reproduzido:', recuo=False)
r.itens([
    '`./simulator/build-firmware.sh` — compila o `main.c` para o simulador;',
    '`python3 -m http.server 8000` (na raiz) e acesso a `http://localhost:8000/simulator/` — abre o simulador; o parâmetro `?elevacaoLdr=25` ativa a variante com os LDRs elevados;',
    '`docs/relatorio/dados/` — dados brutos das simulações (JSON);',
    '`tools/relatorio/graficos.py` e `tools/relatorio/diagramas.py` — gráficos e diagramas;',
    '`tools/render/gerar_figuras_relatorio.sh` — renderizações no Blender a partir dos STL;',
    '`tools/relatorio/gerar_relatorio.py` — gera este documento.',
], alin=WD_ALIGN_PARAGRAPH.LEFT)
r.p('Premissas das simulações: latitude −23,55°; luz direta de 1 000 lux constante (sem atenuação '
    'atmosférica); luz difusa de 10%; variação de ±10% entre LDRs; ruído de 5 mV; servos a 400°/s; placa '
    'fixa de referência voltada ao Norte e inclinada 23,55°; dia simulado à razão de 1 hora a cada 2 segundos.', recuo=False)

r.salvar(SAIDA)
print('OK', SAIDA)
