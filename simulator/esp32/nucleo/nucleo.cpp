// Implementação do núcleo ESP32 simulado + funções exportadas para o simulador (JavaScript).
#include <emscripten/emscripten.h>
#include <map>
#include <string>
#include <vector>

#include "Arduino.h"
#include "ESP32Servo.h"
#include "WebServer.h"
#include "WiFi.h"

// setup() e loop() vêm do main.c
void setup();
void loop();

static unsigned long g_ms = 0;          // tempo simulado (ms)
static unsigned long g_us = 0;
static int g_bits = 12;                 // resolução do ADC (analogReadResolution)
static std::map<int, int> g_adc;        // GPIO -> valor 12 bits
static std::vector<Servo*> g_servos;
static WebServer* g_servidor = nullptr;
static std::string g_saida;             // saída serial acumulada
static std::string g_http;              // última resposta HTTP

SerialSimulado Serial;
WiFiSimulado WiFi;

unsigned long millis() { return g_ms; }
unsigned long micros() { return g_us; }
void delay(unsigned long ms) { g_ms += ms; g_us += ms * 1000; }
void pinMode(int, int) {}
void analogReadResolution(int bits) { g_bits = bits; }
int analogRead(int pino) {
  int v12 = g_adc.count(pino) ? g_adc[pino] : 0;
  return g_bits >= 12 ? v12 << (g_bits - 12) : v12 >> (12 - g_bits);
}
void SerialSimulado::print(const char* t) { g_saida += t; }
int Servo::attach(int p, int mn, int mx) {
  pino = p; minUs = mn; maxUs = mx;
  if (pulsoUs == 0) pulsoUs = (mn + mx) / 2;
  g_servos.push_back(this);
  return 1;
}
void registrarServidor(WebServer* s) { g_servidor = s; }

extern "C" {

EMSCRIPTEN_KEEPALIVE void sim_setup() { setup(); }

// Avança o tempo em passos de 1 ms, chamando loop() a cada passo (o ESP32 chama loop() muito mais
// vezes por ms; como o main.c só age a cada 100 ms via millis(), 1 ms é suficiente).
EMSCRIPTEN_KEEPALIVE void sim_avancar(int ms) {
  for (int i = 0; i < ms; i++) {
    g_ms += 1;
    g_us += 1000;
    loop();
  }
}

EMSCRIPTEN_KEEPALIVE double sim_tempo_ms() { return (double)g_ms; }
EMSCRIPTEN_KEEPALIVE void sim_adc(int pino, int valor12) { g_adc[pino] = valor12; }

// Ângulo comandado (0–180°) do servo ligado ao pino, ou -1.
EMSCRIPTEN_KEEPALIVE double sim_servo_angulo(int pino) {
  for (Servo* s : g_servos)
    if (s->pino == pino) return (double)(s->pulsoUs - s->minUs) * 180.0 / (s->maxUs - s->minUs);
  return -1;
}

// Retira a saída serial acumulada desde a última chamada.
EMSCRIPTEN_KEEPALIVE const char* sim_serial() {
  static std::string ret;
  ret = g_saida;
  g_saida.clear();
  return ret.c_str();
}

EMSCRIPTEN_KEEPALIVE const char* sim_wifi_ssid() { return WiFi.ssid.c_str(); }

// Requisição HTTP GET ao servidor do main.c. Retorna "codigo\ttipo\tcorpo".
EMSCRIPTEN_KEEPALIVE const char* sim_http(const char* url) {
  std::string u(url ? url : "/");
  std::string caminho = u, consulta;
  size_t q = u.find('?');
  if (q != std::string::npos) { caminho = u.substr(0, q); consulta = u.substr(q + 1); }
  if (!g_servidor) { g_http = "503\ttext/plain\tservidor nao criado"; return g_http.c_str(); }
  g_servidor->args.clear();
  size_t i = 0;
  while (i < consulta.size()) {
    size_t e = consulta.find('&', i);
    std::string par = consulta.substr(i, e == std::string::npos ? std::string::npos : e - i);
    size_t igual = par.find('=');
    if (igual != std::string::npos) g_servidor->args[par.substr(0, igual)] = par.substr(igual + 1);
    if (e == std::string::npos) break;
    i = e + 1;
  }
  auto rota = g_servidor->rotas.find(caminho);
  if (rota == g_servidor->rotas.end()) {
    g_http = "404\ttext/plain\tnao encontrado";
  } else {
    g_servidor->codigoResposta = 200;
    g_servidor->corpoResposta.clear();
    rota->second();
    g_http = std::to_string(g_servidor->codigoResposta) + "\t" + g_servidor->tipoResposta + "\t" + g_servidor->corpoResposta;
  }
  return g_http.c_str();
}

}  // extern "C"
