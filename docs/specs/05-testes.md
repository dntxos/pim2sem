# 05 — Plano de testes e calibração

> Os testes T-01 a T-08 e F-01 a F-03 também podem ser feitos no **simulador 3D**
> ([simulator/README.md](../../simulator/README.md)), que roda o mesmo `main.c` sobre as peças
> reais. Cenários de regressão já conhecidos estão na skill `.claude/skills/simulador-3d`.
> Valores de ADC abaixo estão na escala do ESP32 (0–4095).

## Testes de lógica (simulador 3D; na fase Nano, Tinkercad)

| ID | Cenário | Ação | Resultado esperado |
|----|---------|------|--------------------|
| T-01 | Luz uniforme | Todos os LDRs no mesmo nível | Servos parados em 90°/90°. |
| T-02 | Luz à esquerda | Aumentar luz de SE e IE | Horizontal aumenta até 160° ou até equilibrar. |
| T-03 | Luz à direita | Aumentar luz de SD e ID | Horizontal diminui até 20° ou até equilibrar. |
| T-04 | Luz em cima | Aumentar luz de SE e SD | Vertical diminui. |
| T-05 | Luz embaixo | Aumentar luz de IE e ID | Vertical aumenta. |
| T-06 | Diagonal | Aumentar só SE | Os dois eixos se movem. |
| T-07 | Diferença pequena | Diferença < 160 entre lados (`TOLERANCIA`) | Nenhum movimento (zona morta). |
| T-08 | Limites | Manter luz extrema de um lado | Ângulo para em 20° ou 160°, sem passar. |

## Testes no protótipo físico

Realizados na casa do integrante **Dawid Felipe Fernandes da Silva**, com o protótipo montado; os
resultados foram acompanhados pela **IHM no celular** (leituras dos LDRs, ângulos, modo e
período do dia). Registros: `docs/imagens_videos_testes_fisicos/` (fotos, vídeos e capturas da IHM).

| ID | Cenário | Resultado esperado |
|----|---------|--------------------|
| F-00 | Antes de tudo: XL4015 sem carga, medir com multímetro | #1 = 6,0 V (servos); #2 = 6 V (placa do ESP32). Só então ligar as cargas. **Feito** (12 V → 6 V). |
| F-01 | Lanterna movida lentamente em arco | Placa acompanha a lanterna. |
| F-02 | Lanterna parada | Placa estabiliza sem "tremer" (sem oscilação contínua). |
| F-03 | Sentido dos eixos | Placa vai **em direção** à luz. **Resultado registrado:** no teste com lanterna (firmware anterior às correções) o painel girou para o lado contrário. Diagnóstico: iluminar **um lado de cada vez** e olhar os indicadores de diferença da IHM — se a IHM aponta o lado certo e o painel foge → sinal do servo (`+=`/`-=`); se aponta o lado errado → LDRs trocados ou divisor invertido; se só o horizontal inverte com o painel inclinado → P10 (corrigido no `main.c` final). |
| F-04 | Alimentação | ESP32 não reinicia (IHM não cai) quando os dois servos se movem juntos; XL4015 #1 não esquenta demais. |
| F-05 | Sol real (opcional) | Ao longo de algumas horas, placa segue o sol. |
| F-06 | Torque na elevação | Com o painel montado, o servo vertical segura a placa em 20° e 160° sem "cair" nem zumbir forte. |
| F-07 | Autonomia (opcional) | Medir tensão da bateria no início e no fim do dia; com controlador de carga, deve subir ao sol. |
| F-08 | IHM no celular | Conectar em `SOLAR_TOWER`, abrir `http://192.168.4.1`: leituras atualizam a cada 1 s; manual move 5° por toque; em automático as setas ficam bloqueadas. |
| F-09 | Repouso noturno | Cobrir os LDRs por > 2 min: painel vai a 90°/90° e a IHM mostra "Noite"; descobrir: retoma após 30 s ("Amanhecendo"). |
| F-10 | Manhã após o repouso (P15) | Depois de uma noite estacionado, o painel sai do centro e segue o sol logo de manhã (antes da correção ficava preso em H = 20° até ~meio-dia no inverno). |

## Calibração

1. Abrir a IHM no celular com luz uniforme sobre os LDRs (o firmware ESP32 não imprime as
   leituras na serial; a IHM mostra os 4 valores e a diferença entre lados).
2. Anotar a diferença natural entre lados (LDRs nunca são idênticos). `TOLERANCIA` (160) deve ficar
   acima dessa diferença, com folga — a IHM desenha essa zona morta nos indicadores.
3. Se oscilar: aumentar `TOLERANCIA` ou diminuir `PASSO_AUTO`.
4. Se for lento demais: aumentar `PASSO_AUTO` ou reduzir `INTERVALO_MOVIMENTO` (100 ms).

## Ano inteiro (simulador)

Painel "📅 Ano inteiro" (ou `sim.ano()`): mesmo firmware de janeiro a dezembro contra uma placa fixa
voltada ao Norte. Resultado atual (`?elevacaoLdr=25`, a cada 15 dias): **+47% a +49%** sobre a placa
fixa, erro médio ~17° (antes do P15: +35% a +38%, ~28°). Os valores variam ~±2 p.p. entre rodadas
por causa do ruído simulado nos LDRs.

## Placas fixas × rastreador

Comparação de energia no ano com 1 placa fixa, 2 placas fixas Leste/Oeste e o rastreador:
`python3 tools/relatorio/comparar_fixas.py` (resultado e conclusão em [07-conclusao.md](07-conclusao.md)).

## Ensaio comparativo no protótipo (trabalho futuro)

Para demonstrar o ganho do rastreador, medir a tensão/corrente da placa em dois cenários
(placa fixa vs. rastreando) ao longo do mesmo período e comparar a energia. Exige ligar a placa a
uma entrada do ADC1 do ESP32 (com divisor — a entrada aceita no máximo 3,3 V) ou usar um multímetro.
