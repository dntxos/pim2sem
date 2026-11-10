# Simulador 3D do rastreador solar

Simulador no navegador que roda o **mesmo `main.c`** do projeto e mostra a estrutura montada com as
**peças 3D reais**.

- **ESP32 (atual):** o `main.c` é compilado para WebAssembly junto com um *núcleo ESP32 simulado*
  (`esp32/nucleo/`: `millis()`, ADC de 12 bits, `ESP32Servo`, `WiFi.softAP`, `WebServer`). Não é uma
  emulação do chip Xtensa — é o mesmo código-fonte, com a mesma lógica e os mesmos tempos. A página
  do celular servida pelo `main.c` aparece no painel **📱 Celular** e controla a torre simulada.
- **Arduino Nano (versão anterior):** `?firmware=nano` roda o `.hex` em um ATmega328P emulado (avr8js).

## Como abrir

A partir da **raiz do repositório** (o simulador lê os STLs de `3d_material/stl/`):

```bash
python3 -m http.server 8000
```

Depois acesse http://localhost:8000/simulator/

> Abrir o `index.html` direto (file://) não funciona: o navegador bloqueia o carregamento dos STLs.

## O que dá para fazer

- **Mover o sol**: arrastando o ☀️ na cena, pelos controles manuais (azimute/elevação) ou pela
  trajetória real de um dia (latitude, data e hora, com reprodução acelerada).
- **Ver o firmware reagindo**: leituras dos 4 LDRs (lux, volts, ADC), ângulos dos servos, monitor
  serial idêntico ao da Arduino IDE (com download do log) e gráfico dos ângulos e do erro de
  apontamento.
- **Testar defeitos de montagem**: fiação do diagrama (A0–A3) × do código (A1–A4), servos
  invertidos, variação entre LDRs e ruído.
- **Comparar energia**: no modo "trajetória do dia", acumula a energia do rastreador e de uma
  placa fixa (voltada ao Norte, inclinada na latitude) e mostra o ganho.
- **Rodar outro firmware**: carregue qualquer `.hex` para Arduino Nano/Uno (ex.: exportado pela
  Arduino IDE em *Sketch → Exportar binário compilado*).

## Atualizar o firmware depois de editar o `main.c`

```bash
./simulator/build-firmware.sh
```

Detecta a placa pelo `main.c`: para ESP32 gera `simulator/firmware/esp32.mjs` (requer `em++`:
`brew install emscripten`); para Nano, o `.hex` (requer `arduino-cli`). Depois recarregue a página.
Se o `main.c` usar uma função do Arduino/ESP32 que o núcleo simulado ainda não tem, a compilação
falha indicando qual — basta implementá-la em `esp32/nucleo/`.

## Como funciona

| Parte | Arquivo | Detalhe |
|-------|---------|---------|
| Emulador | `js/arduino.js` | [avr8js](https://github.com/wokwi/avr8js): CPU, timers, ADC, USART e GPIO do ATmega328P a 16 MHz. Os ângulos dos servos são medidos pela largura do pulso em D9/D10 (biblioteca Servo: 544–2400 µs ↔ 0–180°). |
| Montagem | `js/montagem.js` | Os STLs foram exportados nas coordenadas da montagem; as peças são agrupadas em fixo / azimute / elevação. Eixos extraídos da geometria (centro do prato e pino da trave). O painel (280 × 250 mm, medida do AMF — conferir com o painel de 10 W real), os servos MG996R e os LDRs são desenhados à parte. |
| Sensores | `js/sensores.js` + `main.js` | Luz direta em cada LDR por *raycasting* contra as peças (a sombra do divisor em cruz é a da peça real) + luz difusa. Lux → resistência (curva do GL5528, R10 = 15 kΩ, γ = 0,7) → divisor com 10 kΩ → tensão no ADC. |
| Sol | `js/sol.js` | Posição solar simplificada (declinação + ângulo horário). Convenção: Norte = −X, Leste = −Z. |

### Suposições (ajuste se a montagem real for diferente)

- Servo vertical em 90° = placa **horizontal**; aumentar o ângulo inclina a face para o Norte.
- Servo horizontal: aumentar o ângulo gira a placa para o Leste (quando ela está voltada ao Norte).
- Se o protótipo físico girar ao contrário, use as opções "Inverter servo".

## Depuração pelo console do navegador

```js
sim.estado.modoSol = 'manual'; sim.estado.azManual = 0; sim.estado.elManual = 50;
sim.sondar(90, 90)   // posiciona os servos e mostra a luz em cada LDR (sem firmware)
sim.avancar(10)      // avança 10 s de simulação de uma vez
sim.erro()           // ângulo entre a normal da placa e o sol (°)
sim.perf             // tempo gasto em emulação, sensores e renderização
```

## Bibliotecas incluídas (`vendor/`)

- three.js 0.186.0 — MIT (`vendor/three/LICENSE`)
- avr8js 0.21.1 — MIT (`vendor/avr8js.LICENSE`), empacotado em um único módulo com esbuild

Ficam no repositório para o simulador funcionar sem internet.
