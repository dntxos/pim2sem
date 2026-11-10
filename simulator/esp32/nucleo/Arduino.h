// Núcleo ESP32 simulado — API mínima do Arduino usada pelo main.c, para compilar o MESMO arquivo
// em WebAssembly (Emscripten) e rodar no simulador 3D. Não emula o chip: o tempo (millis), o ADC, os
// servos e o servidor web são fornecidos pelo simulador em JavaScript.
#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <string>

#define PROGMEM
#define HIGH 1
#define LOW 0

unsigned long millis();
unsigned long micros();
void delay(unsigned long ms);
int analogRead(int pino);
void analogReadResolution(int bits);
void pinMode(int, int);

template <typename T, typename A, typename B>
static inline T constrain(T x, A lo, B hi) { return x < (T)lo ? (T)lo : (x > (T)hi ? (T)hi : x); }
static inline long map(long x, long a, long b, long c, long d) { return (x - a) * (d - c) / (b - a) + c; }

// ---------------------------------------------------------------- String
class String {
 public:
  std::string s;
  String() {}
  String(const char* c) : s(c ? c : "") {}
  String(const std::string& x) : s(x) {}
  String(int v) : s(std::to_string(v)) {}
  String(long v) : s(std::to_string(v)) {}
  String(unsigned int v) : s(std::to_string(v)) {}
  String(unsigned long v) : s(std::to_string(v)) {}
  String(double v) : s(std::to_string(v)) {}
  const char* c_str() const { return s.c_str(); }
  unsigned int length() const { return (unsigned int)s.size(); }
  long toInt() const { return atol(s.c_str()); }
  String& operator+=(const String& o) { s += o.s; return *this; }
  String& operator+=(const char* o) { s += o; return *this; }
  bool operator==(const char* o) const { return s == o; }
  bool operator==(const String& o) const { return s == o.s; }
  bool operator!=(const char* o) const { return s != o; }
};
inline String operator+(const String& a, const String& b) { return String(a.s + b.s); }
inline String operator+(const String& a, const char* b) { return String(a.s + b); }
inline String operator+(const char* a, const String& b) { return String(std::string(a) + b.s); }

// ---------------------------------------------------------------- IPAddress / Serial
class IPAddress {
 public:
  uint8_t o[4];
  IPAddress(uint8_t a = 0, uint8_t b = 0, uint8_t c = 0, uint8_t d = 0) { o[0] = a; o[1] = b; o[2] = c; o[3] = d; }
  String toString() const {
    return String(std::to_string(o[0]) + "." + std::to_string(o[1]) + "." + std::to_string(o[2]) + "." + std::to_string(o[3]));
  }
};

class SerialSimulado {
 public:
  void begin(unsigned long) {}
  void print(const char* t);
  void print(const String& t) { print(t.c_str()); }
  void print(int v) { print(String(v)); }
  void print(long v) { print(String(v)); }
  void print(unsigned long v) { print(String(v)); }
  void print(const IPAddress& ip) { print(ip.toString()); }
  void println() { print("\n"); }
  template <typename T> void println(const T& v) { print(v); print("\n"); }
};
extern SerialSimulado Serial;
