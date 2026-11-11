# 02 — Hardware e ligações

> **Placa atual: ESP32** (adotada na etapa final, de testes físicos). O projeto começou com Arduino
> Nano; o diagrama do Tinkercad (que usa UNO, pois não tem Nano nem ESP32) ficou como referência da
> fase inicial. A migração trouxe Wi-Fi (controle pelo celular), ADC de 12 bits e mais memória.

Referência visual da fase inicial: [`docs/diagrama_tinkercad.png`](../diagrama_tinkercad.png).

## Lista de materiais (BOM) — comprado

| Qtd | Componente | Função |
|-----|------------|--------|
| 1 | ESP32 (placa de desenvolvimento + placa de expansão com bornes) | Lê os 4 LDRs, comanda os 2 servos e serve a interface web por Wi-Fi |
| (1) | Arduino Nano (ATmega328P) | Usado até a migração para o ESP32 |
| 4 | LDR 5 mm | Sensores de luz |
| 4 | Resistor 10 kΩ 1/4 W | Divisor de tensão com cada LDR |
| 2 | Servo MG996R (15 kg·cm, engrenagem metálica) | Giro horizontal (azimute) e inclinação (elevação) |
| 2 | Conversor DC-DC *step-down* XL4015 (5 A) | Baixar os 12 V da bateria para os servos e para a placa de controle |
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
| Cabo USB do ESP32 | Gravar o firmware e ler o Monitor Serial (115 200 baud). |
| Capacitor eletrolítico 470–1000 µF / 16 V | Junto aos servos, absorve os picos de corrente do MG996R. |
| Fusível (2–5 A) + porta-fusível na saída da bateria | Bateria selada fornece corrente alta em curto-circuito. |
| Chave liga/desliga e fios mais grossos (≥ 0,5 mm²) | Os jumpers Dupont de 20 cm não são adequados para a corrente dos servos (até ~2,5 A cada em travamento). |
| Multímetro | Ajustar a saída dos XL4015 **antes** de ligar qualquer coisa. |

## Mapa de pinos (ESP32 — `main.c` atual)

| Sinal | GPIO | Observação |
|-------|------|------------|
| LDR superior-esquerdo (`LDR_SE`) | 34 | ADC1, só entrada |
| LDR superior-direito (`LDR_SD`) | 35 | ADC1, só entrada |
| LDR inferior-esquerdo (`LDR_IE`) | 32 | ADC1 |
| LDR inferior-direito (`LDR_ID`) | 33 | ADC1 |
| Servo horizontal (azimute) | 18 | ESP32Servo, 500–2400 µs |
| Servo vertical (elevação) | 19 | ESP32Servo, 500–2400 µs |

Os LDRs estão no **ADC1** de propósito: o ADC2 do ESP32 não funciona com o Wi-Fi ligado.

> ⚠️ **3,3 V:** as entradas do ESP32 não toleram 5 V. Os divisores dos LDRs devem ser alimentados
> pelo pino **3V3** (não pelo 5V/VIN). Confirmar na montagem.

**Histórico (Nano):** o código usava A1–A4 e o diagrama A0–A3 (P1) — divergência encerrada com a
migração, pois o ESP32 tem pinos próprios.

## Circuito dos LDRs

Cada LDR forma um divisor de tensão com um resistor de 10 kΩ, alimentado pelo **3V3 do ESP32**:

```
3V3 ──[LDR]──┬── GPIO 32–35 (entrada analógica)
            │
          [10kΩ]
            │
           GND
```

Com o LDR no lado do 3V3, **mais luz → menor resistência do LDR → leitura maior** (0–4095).
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
                                                      └──[XL4015 #2 → 6 V]── placa de expansão do ESP32
GND da bateria, dos dois XL4015, dos servos e do Nano: TODOS INTERLIGADOS
```

1. **Ajustar os XL4015 sem carga, com multímetro, antes de ligar:** o potenciômetro azul vem em
   qualquer posição — um XL4015 saindo 12 V queima o Nano ou os servos na hora.
2. **XL4015 #1 (servos): 6,0 V.** Cabos curtos e mais grossos que os jumpers; capacitor perto dos
   servos.
3. **XL4015 #2 (placa do ESP32): 6 V** — valor ajustado pelo grupo nos testes físicos (12 V → 6 V).
   *Histórico (Nano):* 7,5 V no pino VIN. O regulador do Nano baixa para 5 V e protege contra um
   ajuste descuidado. (Alternativa: 5,0 V direto no pino 5V — sem proteção, exige ajuste preciso.)
4. Com a bateria ligada, pode-se conectar o USB ao computador para ver o Monitor Serial — os GNDs
   ficam em comum pelo USB, o que é esperado.
5. **Nunca** ligar servos ou Nano direto nos 12 V da bateria.

Consumo médio estimado: Nano + LDRs ~30 mA; servos parados ~10–20 mA cada, picos curtos ao mover.
Uma bateria de 7 Ah (capacidade típica desse modelo — conferir a etiqueta) alimenta o sistema por
vários dias mesmo sem o painel.
