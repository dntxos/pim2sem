// ESP32Servo simulado: guarda a largura de pulso comandada; o simulador lê o ângulo por pino.
#pragma once
#include "Arduino.h"

class Servo {
 public:
  int pino = -1, minUs = 544, maxUs = 2400, pulsoUs = 0;
  void setPeriodHertz(int) {}
  int attach(int p, int mn = 544, int mx = 2400);
  void detach() { pino = -1; }
  void write(int valor) {
    // Mesmo critério da biblioteca: valores pequenos são ângulos (0–180), grandes são microssegundos.
    if (valor < minUs) valor = (int)map(constrain(valor, 0, 180), 0, 180, minUs, maxUs);
    writeMicroseconds(valor);
  }
  void writeMicroseconds(int us) { pulsoUs = constrain(us, minUs, maxUs); }
  int read() { return (int)map(pulsoUs, minUs, maxUs, 0, 180); }
  bool attached() { return pino >= 0; }
};
