---
name: calibrar-tracker
description: Ajustar e diagnosticar o comportamento do rastreador solar (TOLERANCIA, PASSO_AUTO, INTERVALO_MOVIMENTO, sentido dos eixos, oscilação, lentidão) a partir da IHM (/estado) ou de logs. Use quando o usuário colar leituras da IHM ou saída serial, disser que a placa treme, foge da luz, não se move, está lenta, ou pedir para calibrar/ajustar.
---

# Calibrar o rastreador

## Entrada esperada

No ESP32 as leituras vêm da **IHM** (rota `/estado`: `se`, `sd`, `ie`, `id` em 0–4095, `h`, `v`,
`tol`) — a página já mostra a diferença entre lados com a zona morta. O firmware final não imprime as
leituras na serial. (Na fase Nano o log serial era `Esquerda: … | Direita: … | …`.)

Com leituras coletadas, monte uma tabela/CSV (scratchpad) e calcule
`dH = (se+ie)/2 − (sd+id)/2` e `dV = (se+sd)/2 − (ie+id)/2`.

## Diagnóstico por sintoma

| Sintoma | Causa provável | Ajuste |
|---------|----------------|--------|
| Placa treme parada sob luz estável | `|dH|` ou `|dV|` oscila em torno de `TOLERANCIA` | Aumentar `TOLERANCIA` (≈ 1,5× a amplitude do ruído) ou reduzir `PASSO` para 1. |
| Placa foge da luz | Sinal do eixo invertido p/ esta montagem, divisor do LDR invertido ou LDRs trocados | Iluminar um lado de cada vez e olhar a diferença na IHM: lado certo e painel foge → trocar `+=`/`-=` **daquele eixo**; lado errado → pinos/divisor. |
| Não se move com luz lateral | `TOLERANCIA` alta demais, ou LDR no pino errado | Ver a diferença real na IHM; checar GPIO 34/35/32/33. |
| Uma leitura fixa ~0, ~4095 ou flutuando | Pino errado/sem LDR, divisor sem 3V3 ou sem GND | Conferir ligação × `docs/specs/02-hardware.md`. |
| Encosta em 20° ou 160° e fica | Luz fora do alcance, eixo invertido ou P10/P15 | Verificar sentido; `sentidoHorizontal` e `INICIO_H = 90` presentes; limites são intencionais. |
| Muito lento | `PASSO_AUTO` pequeno ou `INTERVALO_MOVIMENTO` longo | Aumentar `PASSO_AUTO` (2°) ou reduzir o intervalo (100 ms). |
| ESP32 reinicia ao mover (IHM cai) | Servos puxando corrente da placa, XL4015 fraco/desajustado ou GND não comum | Servos só no XL4015 de 6 V, GNDs interligados, capacitor 1000 µF, fios mais grossos que jumper. |
| Servo vertical "cai" ou zumbe com o painel | Torque no limite (MG996R a 4,8 V) | XL4015 dos servos em 6 V; conferir peso do painel. |

## Procedimento de calibração

1. Luz uniforme (difusa) sobre os 4 LDRs; anotar as leituras da IHM por ~30 s.
2. Calcular a média e a amplitude de `dH` e `dV` → isso é o desequilíbrio natural dos sensores.
3. `TOLERANCIA` ≥ |média| + amplitude, com folga de ~20 %.
4. Se a média de algum eixo for grande (> 120 no ADC de 12 bits), sugerir offset por sensor (P6 em problemas conhecidos)
   em vez de inflar a tolerância.
5. Testar com lanterna (testes F-01 a F-03 de `docs/specs/05-testes.md`).

Ao propor novos valores, mostre o raciocínio com os números do log e altere só as constantes no topo
de `main.c`; depois atualize a tabela de parâmetros em `docs/specs/03-firmware.md`.

## Gráficos para o relatório

Com as leituras em CSV, gere um gráfico (matplotlib) de ângulos e de `dH`/`dV` ao longo do tempo — mostra
a convergência do controle e serve como evidência no PIM.
