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
- **Simular o ano inteiro** (seção 📅): o mesmo firmware de janeiro a dezembro em time-lapse, com
  repouso noturno real, comparando rastreador × placa fixa × ideal dia a dia (gráfico, totais e CSV).
  Rápida (a cada 15 dias, ~70 s) ou detalhada (a cada 5 dias).
- **Usar a IHM do celular** (seção 📱): a página servida pelo `main.c` comanda a torre simulada.
- **Ver o firmware reagindo**: leituras dos 4 LDRs (lux, volts, ADC), ângulos dos servos, monitor
  serial idêntico ao da Arduino IDE (com download do log) e gráfico dos ângulos e do erro de
  apontamento. (O firmware ESP32 só imprime o início na serial; as leituras ficam na IHM.)
- **Testar defeitos de montagem**: servos invertidos (o painel foge da luz, como no teste com
  lanterna), variação entre LDRs, ruído e, na versão Nano, a fiação do diagrama (A0–A3).
- **Comparar energia**: no modo "trajetória do dia", acumula a energia do rastreador e de uma
  placa fixa (voltada ao Norte, inclinada na latitude) e mostra o ganho.
- **Comparar versões do firmware**: variantes em `firmware/variantes/` (ex.: `esp32_testes_fisicos`,
  `esp32_antes_p15`) com `sim.reiniciar('esp32:<variante>')`, ou um `.hex` qualquer de Nano/Uno.

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
| Firmware ESP32 | `js/esp32.js` + `esp32/nucleo/` | O `main.c` compilado com `em++` junto com o núcleo simulado; `sim_avancar` chama `loop()` a cada 1 ms de tempo simulado. GPIO 34/35/32/33 ← tensão dos LDRs (ADC de 12 bits, 3,3 V); GPIO 18/19 → ângulo dos servos. |
| Emulador Nano (histórico) | `js/arduino.js` | [avr8js](https://github.com/wokwi/avr8js): CPU, timers, ADC, USART e GPIO do ATmega328P a 16 MHz. Os ângulos dos servos são medidos pela largura do pulso em D9/D10 (biblioteca Servo: 544–2400 µs ↔ 0–180°). |
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
await sim.ano()      // simula o ano inteiro; sim.anoTotais() -> ganho anual e erro médio
sim.http('/estado')  // JSON da IHM (LDRs, ângulos, período do dia...)
```

## Bibliotecas incluídas (`vendor/`)

- three.js 0.186.0 — MIT (`vendor/three/LICENSE`)
- avr8js 0.21.1 — MIT (`vendor/avr8js.LICENSE`), empacotado em um único módulo com esbuild

Ficam no repositório para o simulador funcionar sem internet.

## Vídeos de demonstração

`node tools/video/gravar.mjs` grava o simulador no Chrome headless (sem dependências npm) e monta o
MP4 com ffmpeg: IHM (`docs/video/demo_ihm.mp4`) e funções do simulador
(`node tools/video/gravar.mjs docs/video/demo_simulador.mp4 roteiro_simulador.js 1.2`). O servidor
acima precisa estar rodando.
