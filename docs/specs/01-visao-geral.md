# 01 — Visão geral e requisitos

## Contexto

Projeto Integrado Multidisciplinar (PIM) — UNIP. Protótipo de **rastreador solar de dois eixos**
(*dual-axis solar tracker*): uma estrutura impressa em 3D, movida por dois servos, mantém uma placa
fotovoltaica apontada para a fonte de luz mais intensa, aumentando a energia captada em relação a
uma placa fixa.

## Como funciona (resumo)

1. Quatro LDRs ficam em cruz no suporte da placa (superior-esquerdo, superior-direito,
   inferior-esquerdo, inferior-direito), separados por anteparos.
2. O Arduino lê os quatro sensores e calcula médias por lado (esquerda/direita, superior/inferior).
3. Se um lado recebe mais luz que o oposto além de uma tolerância, o servo daquele eixo gira um
   pequeno passo na direção da luz.
4. O processo se repete continuamente; quando os lados estão equilibrados, a placa está alinhada.

Controle em malha fechada do tipo *bang-bang com zona morta* — não usa relógio, GPS nem cálculo
astronômico da posição do sol.

## Requisitos funcionais

| ID | Requisito |
|----|-----------|
| RF-01 | Ler 4 LDRs pelas entradas analógicas do Arduino. |
| RF-02 | Mover o eixo horizontal (azimute, prato giratório) em direção ao lado mais iluminado. |
| RF-03 | Mover o eixo vertical (elevação) em direção ao lado mais iluminado. |
| RF-04 | Não mover quando a diferença entre lados for menor que a tolerância (zona morta). |
| RF-05 | Limitar os ângulos dos servos a 20°–160° para proteger a mecânica. |
| RF-06 | Iniciar com ambos os servos em 90° (posição central). |
| RF-07 | Enviar leituras e ângulos pelo Monitor Serial para depuração/calibração. |

## Requisitos não funcionais

| ID | Requisito |
|----|-----------|
| RNF-01 | Plataforma: Arduino Nano (ATmega328P), firmware em C++/Arduino. Servos MG996R. |
| RNF-06 | Autônomo: alimentado por bateria 12 V (recarregada pelo próprio painel de 10 W), com conversores *step-down* XL4015. |
| RNF-02 | Simulável antes da montagem física: Tinkercad (com UNO, equivalente ao Nano) e simulador 3D do projeto. |
| RNF-03 | Peças mecânicas imprimíveis em impressora 3D FDM comum. |
| RNF-04 | Movimento suave, sem oscilação contínua quando a luz está estável. |
| RNF-05 | Código legível e comentado em português (avaliação acadêmica). |

## Fora de escopo (por ora)

- Medição de potência/tensão gerada pela placa (sugerido como melhoria — ver `03-firmware.md`).
- Modo noturno / retorno ao leste ao anoitecer.
- Rastreamento astronômico (cálculo por data/hora/latitude).

## Documentos relacionados

- [02-hardware.md](02-hardware.md) — eletrônica e ligações
- [03-firmware.md](03-firmware.md) — algoritmo e código
- [04-mecanica.md](04-mecanica.md) — peças 3D e montagem
- [05-testes.md](05-testes.md) — plano de testes e calibração
- [06-problemas-conhecidos.md](06-problemas-conhecidos.md) — achados da análise e melhorias
