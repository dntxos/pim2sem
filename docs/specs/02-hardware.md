# 02 — Hardware e ligações

Referência visual: [`docs/diagrama_tinkercad.png`](../diagrama_tinkercad.png). O Tinkercad não tem
Arduino Nano, por isso o diagrama usa um **UNO** — os dois usam o mesmo microcontrolador
(ATmega328P) e os mesmos nomes de pinos, então o circuito e o código são equivalentes.

## Lista de materiais (BOM) — comprado

| Qtd | Componente | Função |
|-----|------------|--------|
| 1 | Arduino Nano (ATmega328P) | Lê os 4 LDRs e comanda os 2 servos |
| 4 | LDR 5 mm | Sensores de luz |
| 4 | Resistor 10 kΩ 1/4 W | Divisor de tensão com cada LDR |
| 2 | Servo MG996R (15 kg·cm, engrenagem metálica) | Giro horizontal (azimute) e inclinação (elevação) |
| 2 | Conversor DC-DC *step-down* XL4015 (5 A) | Baixar os 12 V da bateria para os servos e para o Nano |
| 1 | Bateria selada 12 V (Elgin, tipo alarme/cerca) | Fonte de energia do sistema |
| 1 | Painel solar 10 W monocristalino (Ztroon) | Placa que o rastreador aponta para o sol |
| 40 | Jumper Dupont macho–fêmea 20 cm | Ligações |
| 40 | Jumper Dupont macho–macho 20 cm | Ligações |
| — | Peças impressas em 3D | Estrutura — ver [04-mecanica.md](04-mecanica.md) |

### Não aparece nas compras — confirmar se já existe

| Item | Por que é necessário |
|------|----------------------|
| **Controlador de carga solar 12 V** (PWM, ≥ 5 A) | Um painel de 12 V "nominal" chega a ~21 V em aberto. Ligado direto na bateria, sobrecarrega e danifica a bateria selada, e à noite a bateria descarrega pelo painel. Só dispensável se o painel **não** for ligado à bateria (ex.: só medido com multímetro). |
| Protoboard ou placa perfurada | Montar os divisores dos LDRs e distribuir 5 V/GND. |
| Cabo USB do Nano (Mini-USB na maioria dos clones) | Gravar o firmware e ler o Monitor Serial. |
| Capacitor eletrolítico 470–1000 µF / 16 V | Junto aos servos, absorve os picos de corrente do MG996R. |
| Fusível (2–5 A) + porta-fusível na saída da bateria | Bateria selada fornece corrente alta em curto-circuito. |
| Chave liga/desliga e fios mais grossos (≥ 0,5 mm²) | Os jumpers Dupont de 20 cm não são adequados para a corrente dos servos (até ~2,5 A cada em travamento). |
| Multímetro | Ajustar a saída dos XL4015 **antes** de ligar qualquer coisa. |

## Mapa de pinos (Nano)

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

O Nano tem A0–A7, mas **A6 e A7 são só analógicos** e ficam em outra posição da barra de pinos — os
pinos usados (A0–A4) estão em sequência, logo após o pino REF/3V3.

## Circuito dos LDRs

Cada LDR forma um divisor de tensão com um resistor de 10 kΩ, alimentado pelo **5 V do Nano**:

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

## Servos MG996R

- Marrom → GND; vermelho → **+6 V do XL4015 dos servos** (não do Nano); laranja → sinal (D9/D10).
- Tensão de trabalho 4,8–7,2 V; torque ~9,4 kg·cm a 4,8 V e ~11 kg·cm a 6 V (o "15 kg" do anúncio é
  otimista). Corrente: ~0,5–0,9 A em movimento e **até ~2,5 A travado**, cada.
- O CAD já foi desenhado para ele: o servo modelado no AMF tem 54 × 20 × 40 mm (corpo + abas).
- Carga estimada no eixo de elevação: o centro da placa fica a ~64 mm do pino da trave. Com um
  painel de 10 W de ~1 kg (pesar o real), o torque é ~6,4 kg·cm no pior caso — dentro do MG996R,
  com pouca folga a 4,8 V. Por isso a recomendação de **6 V**.
- A biblioteca `Servo` usa o Timer1 do ATmega328P (desativa `analogWrite` em D9/D10, sem impacto
  aqui). O pulso padrão da biblioteca (544–2400 µs) funciona com o MG996R; se o servo bater no fim
  de curso, use `attach(pino, 1000, 2000)`.

## Alimentação

```
                  [fusível]
Painel 10 W ──[controlador de carga]── Bateria 12 V ──┬──[XL4015 #1 → 6,0 V]── servos (+ capacitor 1000 µF)
  (não comprado — ver acima)                          │
                                                      └──[XL4015 #2 → 7,5 V]── VIN do Nano
GND da bateria, dos dois XL4015, dos servos e do Nano: TODOS INTERLIGADOS
```

1. **Ajustar os XL4015 sem carga, com multímetro, antes de ligar:** o potenciômetro azul vem em
   qualquer posição — um XL4015 saindo 12 V queima o Nano ou os servos na hora.
2. **XL4015 #1 (servos): 6,0 V.** Cabos curtos e mais grossos que os jumpers; capacitor perto dos
   servos.
3. **XL4015 #2 (Nano): 7,5 V no pino VIN.** O regulador do Nano baixa para 5 V e protege contra um
   ajuste descuidado. (Alternativa: 5,0 V direto no pino 5V — sem proteção, exige ajuste preciso.)
4. Com a bateria ligada, pode-se conectar o USB ao computador para ver o Monitor Serial — os GNDs
   ficam em comum pelo USB, o que é esperado.
5. **Nunca** ligar servos ou Nano direto nos 12 V da bateria.

Consumo médio estimado: Nano + LDRs ~30 mA; servos parados ~10–20 mA cada, picos curtos ao mover.
Uma bateria de 7 Ah (capacidade típica desse modelo — conferir a etiqueta) alimenta o sistema por
vários dias mesmo sem o painel.
