# 03 — Firmware

Arquivo atual: `main.c` (é um *sketch* Arduino em C++, apesar da extensão `.c` — ver
[06-problemas-conhecidos.md](06-problemas-conhecidos.md#p2)).

## Parâmetros

| Constante | Valor | Significado |
|-----------|-------|-------------|
| `TOLERANCIA` | 40 | Zona morta (unidades ADC, 0–1023). Diferença mínima entre lados para mover. |
| `PASSO` | 2 | Graus movidos por iteração quando há desequilíbrio. |
| Limites | 20°–160° | `constrain` aplicado aos dois eixos. |
| Posição inicial | 90° / 90° | Ambos os eixos centralizados no `setup()`. |
| `delay` | 50 ms | Pausa ao fim de cada ciclo. |
| Serial | 9600 baud | Telemetria por linha. |

## Algoritmo (por ciclo do `loop()`)

```
ler SE, SD, IE, ID                     (analogRead, 0–1023)

esquerda = (SE + IE) / 2
direita  = (SD + ID) / 2
superior = (SE + SD) / 2
inferior = (IE + ID) / 2

se esquerda > direita + TOL   → horizontal += PASSO
senão se direita > esquerda + TOL → horizontal -= PASSO

se superior > inferior + TOL  → vertical -= PASSO
senão se inferior > superior + TOL → vertical += PASSO

limitar ambos a [20, 160]
escrever ângulos nos servos
imprimir telemetria
esperar 50 ms
```

O sinal (+/−) de cada eixo depende de como o servo está montado na estrutura. Se, na montagem
física, a placa fugir da luz em vez de segui-la, basta inverter o sinal daquele eixo.

## Formato da telemetria serial

Uma linha por ciclo:

```
Esquerda: 512 | Direita: 498 | Superior: 530 | Inferior: 480 | Horizontal: 92 | Vertical: 88
```

Útil para calibração (ver skill `calibrar-tracker`) e para gerar gráficos no relatório.

## Temporização real

A linha de telemetria tem ~95 caracteres. A 9600 baud (~960 caracteres/s) cada linha leva
**~100 ms** para ser transmitida; como o buffer de TX do UNO tem 64 bytes, o `Serial.print`
bloqueia até sobrar espaço. O `delay(50)` acontece enquanto o restante do buffer ainda está saindo,
então o período real do laço é **≈ 100 ms** (medido no simulador: 0,098 s), e não 50 ms.
Velocidade máxima efetiva ≈ 2° / 0,1 s ≈ **20°/s** por eixo. Ver melhoria em
[06-problemas-conhecidos.md](06-problemas-conhecidos.md#p3).

## Build

- Arduino IDE: abrir o sketch, placa **Arduino Uno**, porta USB, *Upload*.
- `arduino-cli` (linha de comando): ver skill `.claude/skills/firmware-arduino`.
- Tinkercad: colar o conteúdo de `main.c` no editor de código (modo texto) do circuito.
- Simulador 3D do projeto: `./simulator/build-firmware.sh` e abrir `simulator/` (ver
  [simulator/README.md](../../simulator/README.md)).

A biblioteca `Servo` já vem com a Arduino IDE (no `arduino-cli`: `arduino-cli lib install Servo`).
