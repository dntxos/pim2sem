#!/usr/bin/env bash
# Compila o main.c (sketch Arduino) para o .hex usado pelo simulador.
# Uso: ./simulator/build-firmware.sh   (a partir da raiz do repositório ou de qualquer lugar)
# Placa: Arduino Nano (ATmega328P). O .hex não inclui o bootloader, então é o mesmo para
# cpu=atmega328 e cpu=atmega328old; outra placa: FQBN=arduino:avr:uno ./simulator/build-firmware.sh
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SAIDA="$RAIZ/simulator/firmware"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if ! command -v arduino-cli >/dev/null; then
  echo "arduino-cli não encontrado. Instale com: brew install arduino-cli" >&2
  exit 1
fi
arduino-cli core list | grep -q '^arduino:avr' || arduino-cli core install arduino:avr
arduino-cli lib list | grep -q '^Servo ' || arduino-cli lib install Servo

mkdir -p "$TMP/solar_tracker" "$SAIDA"
cp "$RAIZ/main.c" "$TMP/solar_tracker/solar_tracker.ino"
arduino-cli compile --fqbn "${FQBN:-arduino:avr:nano}" --output-dir "$TMP/out" "$TMP/solar_tracker"
cp "$TMP/out/solar_tracker.ino.hex" "$SAIDA/solar_tracker.hex"
echo "OK: $SAIDA/solar_tracker.hex"
