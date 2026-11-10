#!/usr/bin/env bash
# Compila o main.c para o simulador, conforme a placa para a qual ele foi escrito:
#  - ESP32 (inclui WiFi.h / ESP32Servo.h): compila o MESMO main.c para WebAssembly com o núcleo
#    ESP32 simulado (simulator/esp32/nucleo) -> simulator/firmware/esp32.mjs  (requer emscripten)
#  - Arduino Nano/UNO: compila com arduino-cli -> simulator/firmware/solar_tracker.hex
# Gera também simulator/firmware/firmware.json, que diz ao simulador qual firmware carregar.
# Uso: ./simulator/build-firmware.sh   (a partir de qualquer pasta)
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SAIDA="$RAIZ/simulator/firmware"
mkdir -p "$SAIDA"
MAIN="$RAIZ/main.c"

pino() { grep -E "const int $1 *=" "$MAIN" | head -1 | sed -E 's/.*= *([0-9]+).*/\1/'; }

if grep -qE '#include *<(WiFi|ESP32Servo)\.h>' "$MAIN"; then
  command -v em++ >/dev/null || { echo "em++ não encontrado. Instale com: brew install emscripten" >&2; exit 1; }
  NUC="$RAIZ/simulator/esp32/nucleo"
  em++ -std=gnu++17 -O2 -I"$NUC" -include Arduino.h -x c++ "$MAIN" -x c++ "$NUC/nucleo.cpp" \
    -sMODULARIZE -sEXPORT_ES6 -sSINGLE_FILE -sENVIRONMENT=web,node -sALLOW_MEMORY_GROWTH \
    -sEXPORTED_RUNTIME_METHODS=ccall,cwrap,UTF8ToString \
    -sEXPORTED_FUNCTIONS=_sim_setup,_sim_avancar,_sim_tempo_ms,_sim_adc,_sim_servo_angulo,_sim_serial,_sim_wifi_ssid,_sim_http \
    -o "$SAIDA/esp32.mjs"
  cat > "$SAIDA/firmware.json" <<EOF
{
  "placa": "esp32",
  "arquivo": "esp32.mjs",
  "pinos": { "SE": $(pino LDR_SE), "SD": $(pino LDR_SD), "IE": $(pino LDR_IE), "ID": $(pino LDR_ID),
             "servoH": $(pino PINO_SERVO_H), "servoV": $(pino PINO_SERVO_V) },
  "adcBits": 12, "vref": 3.3
}
EOF
  echo "OK (ESP32 → WebAssembly): $SAIDA/esp32.mjs"
else
  command -v arduino-cli >/dev/null || { echo "arduino-cli não encontrado. Instale com: brew install arduino-cli" >&2; exit 1; }
  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  arduino-cli core list | grep -q '^arduino:avr' || arduino-cli core install arduino:avr
  arduino-cli lib list | grep -q '^Servo ' || arduino-cli lib install Servo
  mkdir -p "$TMP/solar_tracker"
  cp "$MAIN" "$TMP/solar_tracker/solar_tracker.ino"
  arduino-cli compile --fqbn "${FQBN:-arduino:avr:nano}" --output-dir "$TMP/out" "$TMP/solar_tracker"
  cp "$TMP/out/solar_tracker.ino.hex" "$SAIDA/solar_tracker.hex"
  echo '{ "placa": "nano", "arquivo": "solar_tracker.hex" }' > "$SAIDA/firmware.json"
  echo "OK (Nano → .hex): $SAIDA/solar_tracker.hex"
fi
