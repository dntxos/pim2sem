// Servidor web simulado: o simulador entrega cada requisição HTTP (ex.: "/estado", "/mover?eixo=h&direcao=1")
// ao handler registrado com server.on(), exatamente como o ESP32 faria.
#pragma once
#include <functional>
#include <map>
#include "Arduino.h"

class WebServer;
void registrarServidor(WebServer* s);  // o simulador encontra o servidor criado pelo main.c

class WebServer {
 public:
  explicit WebServer(int porta = 80) : porta(porta) { registrarServidor(this); }
  void on(const char* caminho, std::function<void()> f) { rotas[caminho] = f; }
  void begin() { iniciado = true; }
  void handleClient() {}
  String arg(const char* nome) {
    auto it = args.find(nome);
    return it == args.end() ? String("") : String(it->second);
  }
  void send(int codigo, const char* tipo, const String& corpo) { resposta(codigo, tipo, corpo.c_str()); }
  void send(int codigo, const char* tipo, const char* corpo) { resposta(codigo, tipo, corpo); }
  void send_P(int codigo, const char* tipo, const char* corpo) { resposta(codigo, tipo, corpo); }

  // ---- usado pelo simulador
  int porta;
  bool iniciado = false;
  std::map<std::string, std::function<void()>> rotas;
  std::map<std::string, std::string> args;
  int codigoResposta = 0;
  std::string tipoResposta, corpoResposta;
  void resposta(int c, const char* t, const char* b) { codigoResposta = c; tipoResposta = t; corpoResposta = b; }
};

