---
name: firmware-arduino
description: Compilar, enviar (upload) e checar o firmware do rastreador solar no ESP32 com arduino-cli (e, para o simulador, em WebAssembly). Use ao alterar main.c, quando pedirem para compilar/testar/gravar o código, ou antes de afirmar que uma mudança no firmware está pronta.
---

# Firmware Arduino — compilar e gravar

O firmware está em `main.c` (sketch Arduino em C++). O `arduino-cli` exige um `.ino` dentro de uma
pasta com o mesmo nome, então compile a partir de uma cópia temporária enquanto o arquivo não for
migrado (ver P2 em `docs/specs/06-problemas-conhecidos.md`).

## 1. Preparar ferramentas (uma vez)

```bash
command -v arduino-cli || brew install arduino-cli
arduino-cli core update-index
arduino-cli config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core update-index && arduino-cli core install esp32:esp32
arduino-cli lib install ESP32Servo
brew install emscripten          # para o simulador (build-firmware.sh)
```

## 2. Compilar

```bash
SK="$(mktemp -d)/solar_tower"; mkdir -p "$SK"
cp main.c "$SK/solar_tower.ino"
arduino-cli compile --fqbn esp32:esp32:esp32 "$SK"   # ~950 KB, 72% da flash
./simulator/build-firmware.sh                         # mesmo main.c -> simulator/firmware/esp32.mjs
```

Se o repositório já tiver `firmware/solar_tracker/solar_tracker.ino`, compile essa pasta
diretamente. Relate o uso de flash/RAM que o compilador imprime.

## 3. Gravar (somente se o usuário pedir e a placa estiver conectada)

```bash
arduino-cli board list                       # descobrir a porta (ex.: /dev/cu.usbserial-0001)
arduino-cli upload -p <porta> --fqbn esp32:esp32:esp32 "$SK"
arduino-cli monitor -p <porta> -c baudrate=115200   # bloqueante: rodar em background ou pedir ao usuário
```

## 4. Checklist antes de concluir uma mudança

- [ ] Compila sem erros nem avisos novos.
- [ ] Pinos batem com `docs/specs/02-hardware.md` (LDRs 34/35/32/33 no ADC1, servos 18/19).
- [ ] `./simulator/build-firmware.sh` compila (o núcleo simulado cobre as APIs usadas; se não, implemente em `simulator/esp32/nucleo/`).
- [ ] LDRs só em pinos do ADC1 (32–39): o ADC2 não funciona com Wi-Fi ligado.
- [ ] Constantes em unidades de ADC pensadas para 12 bits (0–4095) — ver P14.
- [ ] Limites dos servos continuam em 20°–160° (ou o usuário aprovou outros).
- [ ] Telemetria serial mantida; se o formato mudou, atualizar `docs/specs/03-firmware.md`.
- [ ] Comentários em português.
