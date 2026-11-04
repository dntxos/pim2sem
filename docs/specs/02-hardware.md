# 02 — Hardware e ligações

Referência visual: [`docs/diagrama_tinkercad.png`](../diagrama_tinkercad.png) (circuito no Tinkercad).

## Lista de materiais (BOM)

| Qtd | Componente | Observação |
|-----|------------|------------|
| 1 | Arduino UNO R3 | Alimentado via USB no protótipo |
| 2 | Servo SG90 (ou MG90S) | 0–180°, sinal PWM 50 Hz |
| 4 | LDR (fotorresistor 5 mm) | Sensores de luz |
| 4 | Resistor 10 kΩ | Divisor de tensão com cada LDR |
| 1 | Protoboard + jumpers | |
| 1 | Placa fotovoltaica pequena | Montada sobre o suporte |
| — | Peças impressas em 3D | Ver [04-mecanica.md](04-mecanica.md) |
| (rec.) | Fonte 5 V ≥ 2 A externa | Para os servos — ver "Alimentação" |

## Mapa de pinos

| Sinal | Pino no **código** (`main.c`) | Pino no **diagrama Tinkercad** |
|-------|------------------------------|--------------------------------|
| LDR superior-esquerdo (`LDR_SE`) | A1 | A0 ⚠️ |
| LDR superior-direito (`LDR_SD`) | A2 | A1 ⚠️ |
| LDR inferior-esquerdo (`LDR_IE`) | A3 | A2 ⚠️ |
| LDR inferior-direito (`LDR_ID`) | A4 | A3 ⚠️ |
| Servo horizontal (azimute) | D9 | D9 |
| Servo vertical (elevação) | D10 | D10 |

> ⚠️ **Divergência:** no diagrama os quatro fios analógicos saem de **A0–A3**; o código lê
> **A1–A4**. Um dos dois precisa ser corrigido antes da montagem final (ver
> [06-problemas-conhecidos.md](06-problemas-conhecidos.md#p1)). Também é preciso confirmar qual
> LDR físico vai em cada pino, pois a lógica depende da posição (SE/SD/IE/ID).

## Circuito dos LDRs

Cada LDR forma um divisor de tensão com um resistor de 10 kΩ:

```
5V ──[LDR]──┬── Ax (entrada analógica)
            │
          [10kΩ]
            │
           GND
```

Com o LDR no lado do 5 V, **mais luz → menor resistência do LDR → leitura maior** (0–1023).
A lógica do firmware assume essa convenção (valor maior = lado mais iluminado). Se o divisor for
montado invertido (LDR no GND), os sentidos dos eixos se invertem.

## Servos

- Fio marrom/preto → GND; vermelho → 5 V; laranja/amarelo → sinal (D9/D10).
- A biblioteca `Servo` usa o Timer1 do ATmega328P, o que desativa `analogWrite` (PWM) nos pinos
  9 e 10 — sem impacto aqui, pois esses pinos são usados justamente pelos servos.

## Alimentação

No diagrama, os servos são alimentados pelo pino 5 V do Arduino (via USB). Para simulação é ok,
mas fisicamente **dois SG90 podem puxar picos de 500–700 mA cada**, acima do que o regulador/USB
fornece com folga, causando *reset* do Arduino ou tremores.

Recomendação para a montagem física: alimentar os servos com uma fonte 5 V externa e **interligar
o GND** da fonte com o GND do Arduino. Um capacitor eletrolítico de 470–1000 µF entre 5 V e GND
dos servos ajuda a absorver os picos.
