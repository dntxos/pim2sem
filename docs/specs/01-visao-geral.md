# 01 — Visão geral e requisitos

> **Projeto concluído (24/11/2026)** — protótipo montado, `main.c` final e conclusão em
> [07-conclusao.md](07-conclusao.md).

## Contexto

Projeto Integrado Multidisciplinar (PIM) — UNIP. Protótipo de **rastreador solar de dois eixos**
(*dual-axis solar tracker*): uma estrutura impressa em 3D, movida por dois servos, mantém uma placa
fotovoltaica apontada para a fonte de luz mais intensa, aumentando a energia captada em relação a
uma placa fixa. É o subsistema de rastreamento da **torre solar** do PIM II (carregamento de
celulares por USB a partir de bateria de 12 V).

## Como funciona (resumo)

1. Quatro LDRs ficam em cruz no suporte da placa (superior-esquerdo, superior-direito,
   inferior-esquerdo, inferior-direito), separados por anteparos.
2. O **ESP32** lê os quatro sensores (ADC de 12 bits) e calcula médias por lado
   (esquerda/direita, superior/inferior).
3. Se um lado recebe mais luz que o oposto além de uma tolerância, o servo daquele eixo gira um
   pequeno passo na direção da luz.
4. O processo se repete a cada 100 ms; quando os lados estão equilibrados, a placa está alinhada.
5. À noite (luz baixa por 2 min) o painel estaciona no centro (90°/90°) e volta a rastrear quando
   a luz se mantém por 30 s.
6. O ESP32 cria a rede Wi-Fi `SOLAR_TOWER`; pelo celular (`http://192.168.4.1`) a **IHM** mostra
   sensores, servos, período do dia e histórico, e permite o controle manual.

Controle em malha fechada do tipo *bang-bang com zona morta* — não usa relógio, GPS nem cálculo
astronômico da posição do sol.

## Requisitos funcionais

| ID | Requisito |
|----|-----------|
| RF-01 | Ler 4 LDRs pelas entradas analógicas do ESP32 (ADC1: GPIO 34, 35, 32, 33). |
| RF-02 | Mover o eixo horizontal (azimute, prato giratório) em direção ao lado mais iluminado. |
| RF-03 | Mover o eixo vertical (elevação) em direção ao lado mais iluminado. |
| RF-04 | Não mover quando a diferença entre lados for menor que a tolerância (zona morta). |
| RF-05 | Limitar os ângulos dos servos a 20°–160° para proteger a mecânica. |
| RF-06 | Iniciar com ambos os servos em 90° (posição central). |
| RF-07 | Expor leituras e ângulos para depuração/calibração (IHM e rota `/estado`; serial a 115 200 baud). |
| RF-08 | Repouso noturno: estacionar em 90°/90° com luz baixa por 120 s; retomar após 30 s de luz. |
| RF-09 | IHM pelo celular (Wi-Fi próprio, sem internet): modo automático/manual, dia/noite, 4 LDRs, ângulos, gráfico, setas e posição inicial. |

## Requisitos não funcionais

| ID | Requisito |
|----|-----------|
| RNF-01 | Plataforma: ESP32 (migrado do Arduino Nano na etapa de testes físicos), firmware em C++/Arduino. Servos MG996R. |
| RNF-06 | Autônomo: alimentado por bateria 12 V (recarregada pelo próprio painel de 10 W), com conversores *step-down* XL4015. |
| RNF-02 | Simulável: o simulador 3D roda o **mesmo `main.c`** (WebAssembly), inclusive o ano inteiro; Tinkercad na fase inicial. |
| RNF-03 | Peças mecânicas imprimíveis em impressora 3D FDM comum. |
| RNF-04 | Movimento suave, sem oscilação contínua quando a luz está estável. |
| RNF-05 | Código legível e comentado em português (avaliação acadêmica). |

## Fora de escopo (por ora)

- Medição de potência/tensão gerada pela placa e da carga da bateria (melhoria — ver `02-hardware.md`).
- Rastreamento astronômico (cálculo por data/hora/latitude).

## Documentos relacionados

- [02-hardware.md](02-hardware.md) — eletrônica e ligações
- [03-firmware.md](03-firmware.md) — algoritmo e código
- [04-mecanica.md](04-mecanica.md) — peças 3D e montagem
- [05-testes.md](05-testes.md) — plano de testes e calibração
- [06-problemas-conhecidos.md](06-problemas-conhecidos.md) — achados da análise e melhorias
- [07-conclusao.md](07-conclusao.md) — resultados, consulta ao mercado e conclusão (placas fixas × rastreador)
