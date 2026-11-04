---
name: firmware-arduino
description: Compilar, enviar (upload) e checar o firmware do rastreador solar no Arduino Nano com arduino-cli. Use ao alterar main.c, quando pedirem para compilar/testar/gravar o código, ou antes de afirmar que uma mudança no firmware está pronta.
---

# Firmware Arduino — compilar e gravar

O firmware está em `main.c` (sketch Arduino em C++). O `arduino-cli` exige um `.ino` dentro de uma
pasta com o mesmo nome, então compile a partir de uma cópia temporária enquanto o arquivo não for
migrado (ver P2 em `docs/specs/06-problemas-conhecidos.md`).

## 1. Preparar ferramentas (uma vez)

```bash
command -v arduino-cli || brew install arduino-cli
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli lib install Servo
```

## 2. Compilar

```bash
SK="$(mktemp -d)/solar_tracker"; mkdir -p "$SK"
cp main.c "$SK/solar_tracker.ino"
arduino-cli compile --fqbn arduino:avr:nano "$SK"
```

Se o repositório já tiver `firmware/solar_tracker/solar_tracker.ino`, compile essa pasta
diretamente. Relate o uso de flash/RAM que o compilador imprime.

## 3. Gravar (somente se o usuário pedir e a placa estiver conectada)

```bash
arduino-cli board list                       # descobrir a porta, ex.: /dev/cu.usbserial-1410 (clone CH340)
# clones de Nano quase sempre usam o bootloader antigo:
arduino-cli upload -p <porta> --fqbn arduino:avr:nano:cpu=atmega328old "$SK"
# se der "not in sync"/stk500_getsync, tente o bootloader novo: --fqbn arduino:avr:nano:cpu=atmega328
arduino-cli monitor -p <porta> -c baudrate=9600   # bloqueante: rodar em background ou pedir ao usuário
```

## 4. Checklist antes de concluir uma mudança

- [ ] Compila sem erros nem avisos novos.
- [ ] Pinos batem com `docs/specs/02-hardware.md` (atenção à divergência A0–A3 × A1–A4).
- [ ] Usa só bibliotecas padrão (precisa rodar no Tinkercad, que usa UNO — mesmo ATmega328P do Nano).
- [ ] Não usa A6/A7 como digitais (no Nano são só analógicos).
- [ ] Limites dos servos continuam em 20°–160° (ou o usuário aprovou outros).
- [ ] Telemetria serial mantida; se o formato mudou, atualizar `docs/specs/03-firmware.md`.
- [ ] Comentários em português.
