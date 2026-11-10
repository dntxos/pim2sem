// Wi-Fi simulado: o ponto de acesso existe só no simulador (a página abre no painel "Celular").
#pragma once
#include "Arduino.h"

#define WIFI_AP 2

class WiFiSimulado {
 public:
  String ssid, senha;
  void mode(int) {}
  bool softAP(const char* nome, const char* pass = nullptr) {
    ssid = nome;
    senha = pass ? pass : "";
    return true;
  }
  IPAddress softAPIP() { return IPAddress(192, 168, 4, 1); }
};
extern WiFiSimulado WiFi;
