---
name: calibrar-tracker
description: Ajustar e diagnosticar o comportamento do rastreador solar (TOLERANCIA, PASSO, delay, sentido dos eixos, oscilação, lentidão) e analisar logs do Monitor Serial. Use quando o usuário colar saída serial, disser que a placa treme, foge da luz, não se move, está lenta, ou pedir para calibrar/ajustar.
---

# Calibrar o rastreador

## Entrada esperada

Linhas do Monitor Serial no formato:

```
Esquerda: 512 | Direita: 498 | Superior: 530 | Inferior: 480 | Horizontal: 92 | Vertical: 88
```

Se o usuário colar um log, converta para tabela/CSV (scratchpad) e calcule por linha
`dH = Esquerda - Direita` e `dV = Superior - Inferior`.

## Diagnóstico por sintoma

| Sintoma | Causa provável | Ajuste |
|---------|----------------|--------|
| Placa treme parada sob luz estável | `|dH|` ou `|dV|` oscila em torno de `TOLERANCIA` | Aumentar `TOLERANCIA` (≈ 1,5× a amplitude do ruído) ou reduzir `PASSO` para 1. |
| Placa foge da luz | Sinal do eixo invertido p/ esta montagem, ou divisor do LDR invertido | Trocar `+=`/`-=` **daquele eixo**; confirmar convenção "maior = mais luz". |
| Não se move com luz lateral | `TOLERANCIA` alta demais, ou LDR no pino errado | Ver diferença real no log; checar pinos (A0–A3 × A1–A4). |
| Uma leitura fixa ~0 ou flutuando | Pino errado/sem LDR (ex.: A4 vazio) | Conferir ligação × `docs/specs/02-hardware.md`. |
| Encosta em 20° ou 160° e fica | Luz fora do alcance, ou eixo invertido | Verificar sentido; limites são intencionais. |
| Muito lento | `PASSO` pequeno + serial bloqueando (~100 ms/linha a 9600) | Aumentar `PASSO`, `Serial.begin(115200)`, imprimir a cada N ciclos. |
| Arduino reinicia ao mover | Alimentação dos servos pelo 5 V do UNO | Fonte externa 5 V + GND comum + capacitor. |

## Procedimento de calibração

1. Luz uniforme (difusa) sobre os 4 LDRs, ~30 s de log.
2. Calcular a média e a amplitude de `dH` e `dV` → isso é o desequilíbrio natural dos sensores.
3. `TOLERANCIA` ≥ |média| + amplitude, com folga de ~20 %.
4. Se a média de algum eixo for grande (>30), sugerir offset por sensor (P6 em problemas conhecidos)
   em vez de inflar a tolerância.
5. Testar com lanterna (testes F-01 a F-03 de `docs/specs/05-testes.md`).

Ao propor novos valores, mostre o raciocínio com os números do log e altere só as constantes no topo
de `main.c`; depois atualize a tabela de parâmetros em `docs/specs/03-firmware.md`.

## Gráficos para o relatório

Com o log em CSV, gere um gráfico (matplotlib) de ângulos e de `dH`/`dV` ao longo do tempo — mostra
a convergência do controle e serve como evidência no PIM.
