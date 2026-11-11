#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

// =====================================
// REDE WI-FI DA TORRE
// =====================================
const char* nomeRede = "SOLAR_TOWER";
const char* senhaRede = "torre1234";

WebServer server(80);

// =====================================
// PINOS DOS LDRs
// =====================================
const int LDR_SE = 34;
const int LDR_SD = 35;
const int LDR_IE = 32;
const int LDR_ID = 33;

// =====================================
// PINOS DOS SERVOS
// =====================================
const int PINO_SERVO_H = 18;
const int PINO_SERVO_V = 19;

Servo servoHorizontal;
Servo servoVertical;

// =====================================
// POSICOES
// =====================================
int anguloH = 90;
int anguloV = 90;

// Ajustar conforme a montagem mecanica
const int INICIO_H = 20;
const int INICIO_V = 90;

const int LIMITE_H_MIN = 20;
const int LIMITE_H_MAX = 160;
const int LIMITE_V_MIN = 20;
const int LIMITE_V_MAX = 160;

// =====================================
// CONFIGURACOES DO RASTREAMENTO
// =====================================
// Zona morta em unidades do ADC de 12 bits (0-4095). No Nano (10 bits)
// era 40; no ESP32 a escala e 4x maior, entao 40 x 4 = 160 (P14).
const int TOLERANCIA = 160;
const int PASSO_AUTO = 2;
const int PASSO_MANUAL = 5;

bool modoAutomatico = true;
bool noiteEstacionada = false;

int luminosidadeMedia = 0;

const int LIMITE_NOITE = 500;
const int LIMITE_DIA = 700;

const unsigned long TEMPO_NOITE = 120000;
const unsigned long TEMPO_DIA = 30000;

unsigned long inicioEscuro = 0;
unsigned long inicioClaro = 0;

unsigned long ultimoMovimento = 0;
const unsigned long INTERVALO_MOVIMENTO = 100;

// =====================================
// INTERFACE WEB
// =====================================
const char pagina[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset="UTF-8">
<title>Solar Tower</title>

<style>
body {
  font-family: Arial;
  background: #101820;
  color: white;
  text-align: center;
  padding: 15px;
}

.caixa {
  background: #1d2b36;
  padding: 18px;
  margin: 12px auto;
  border-radius: 15px;
  max-width: 400px;
}

button {
  border: none;
  border-radius: 12px;
  padding: 17px;
  margin: 5px;
  font-size: 17px;
  background: #344b5c;
  color: white;
  min-width: 90px;
}

.ativo {
  background: #168653;
}

.seta {
  font-size: 24px;
  min-width: 75px;
}

#status {
  color: #76e6a7;
}
</style>
</head>

<body>

<h2>☀️ SOLAR SMART TOWER</h2>
<p id="status">Conectando...</p>

<div class="caixa">
<h3>Modo de funcionamento</h3>

<button onclick="modo('auto')" id="auto">
AUTOMATICO
</button>

<button onclick="modo('manual')" id="manual">
MANUAL
</button>
</div>

<div class="caixa">
<h3>Controle do painel</h3>

<p>Movimento horizontal</p>

<button class="seta" onclick="mover('h',-1)">◀️</button>
<button class="seta" onclick="mover('h',1)">▶️</button>

<p>Movimento vertical</p>

<button class="seta" onclick="mover('v',1)">▲</button>
<button class="seta" onclick="mover('v',-1)">▼</button>

<p>
<button onclick="centralizar()">
POSICAO INICIAL
</button>
</p>
</div>

<div class="caixa">
<h3>Informacoes</h3>

<p>Horizontal: <span id="h">90</span>°</p>
<p>Vertical: <span id="v">90</span>°</p>
<p>Luminosidade: <span id="luz">--</span></p>
<p>Estado: <span id="estado">--</span></p>
</div>

<script>

async function chamar(url) {
  try {
    const r = await fetch(url);
    return await r.json();
  } catch(e) {
    document.getElementById("status").innerText =
    "Falha na comunicacao";
  }
}

async function modo(m) {
  await chamar("/modo?valor=" + m);
  atualizar();
}

async function mover(eixo,direcao) {
  await chamar("/mover?eixo=" + eixo +
               "&direcao=" + direcao);
  atualizar();
}

async function centralizar() {
  await chamar("/inicio");
  atualizar();
}

async function atualizar() {
  const d = await chamar("/estado");
  if (!d) return;

  document.getElementById("status").innerText =
  "Wi-Fi conectado a torre";

  document.getElementById("h").innerText = d.h;
  document.getElementById("v").innerText = d.v;
  document.getElementById("luz").innerText = d.luz;
  document.getElementById("estado").innerText = d.estado;

  document.getElementById("auto").className =
  d.modo == "AUTO" ? "ativo" : "";

  document.getElementById("manual").className =
  d.modo == "MANUAL" ? "ativo" : "";
}

setInterval(atualizar,1500);
atualizar();

</script>
</body>
</html>
)rawliteral";

// =====================================
// APLICAR POSICAO
// =====================================
void aplicarPosicao() {
  servoHorizontal.write(anguloH);
  servoVertical.write(anguloV);
}

// =====================================
// RETORNO NOTURNO
// =====================================
void voltarInicio() {
  anguloH = INICIO_H;
  anguloV = INICIO_V;

  aplicarPosicao();

  noiteEstacionada = true;
}

// =====================================
// LEITURA DOS LDRs
// =====================================
void lerSensores(int &se, int &sd, int &ie, int &id) {

  se = analogRead(LDR_SE);
  sd = analogRead(LDR_SD);
  ie = analogRead(LDR_IE);
  id = analogRead(LDR_ID);

  luminosidadeMedia = (se + sd + ie + id) / 4;
}

// =====================================
// RASTREAMENTO AUTOMATICO
// =====================================
void rastrearSol() {

  int se, sd, ie, id;

  lerSensores(se, sd, ie, id);

  int esquerda = (se + ie) / 2;
  int direita = (sd + id) / 2;

  int superior = (se + sd) / 2;
  int inferior = (ie + id) / 2;

  // Os LDRs giram junto com o painel. Quando o servo vertical passa de 90,
  // o painel fica voltado para o outro lado e "esquerda/direita" se invertem
  // em relacao ao giro do prato; por isso o sentido da correcao tambem
  // inverte (P10). Sem isso o servo horizontal trava no limite.
  int sentidoHorizontal = (anguloV >= 90) ? 1 : -1;

  if (esquerda > direita + TOLERANCIA)
    anguloH += sentidoHorizontal * PASSO_AUTO;

  else if (direita > esquerda + TOLERANCIA)
    anguloH -= sentidoHorizontal * PASSO_AUTO;

  if (superior > inferior + TOLERANCIA)
    anguloV -= PASSO_AUTO;

  else if (inferior > superior + TOLERANCIA)
    anguloV += PASSO_AUTO;

  anguloH = constrain(
    anguloH,LIMITE_H_MIN,LIMITE_H_MAX
  );

  anguloV = constrain(
    anguloV,LIMITE_V_MIN,LIMITE_V_MAX
  );

  aplicarPosicao();
}

// =====================================
// DETECCAO DE DIA E NOITE
// =====================================
void verificarDiaNoite() {

  int se, sd, ie, id;

  lerSensores(se, sd, ie, id);

  unsigned long agora = millis();

  if (luminosidadeMedia < LIMITE_NOITE) {

    inicioClaro = 0;

    if (inicioEscuro == 0)
      inicioEscuro = agora;

    if (!noiteEstacionada &&
        agora - inicioEscuro >= TEMPO_NOITE) {

      voltarInicio();
    }
  }

  else if (luminosidadeMedia > LIMITE_DIA) {

    inicioEscuro = 0;

    if (inicioClaro == 0)
      inicioClaro = agora;

    if (noiteEstacionada &&
        agora - inicioClaro >= TEMPO_DIA) {

      noiteEstacionada = false;
    }
  }

  else {
    inicioEscuro = 0;
    inicioClaro = 0;
  }
}

// =====================================
// PAGINA PRINCIPAL
// =====================================
void paginaInicial() {
  server.send_P(200,"text/html",pagina);
}

// =====================================
// ALTERAR MODO
// =====================================
void mudarModo() {

  if (server.arg("valor") == "auto") {

    modoAutomatico = true;

    inicioEscuro = 0;
    inicioClaro = 0;

  } else {

    modoAutomatico = false;
  }

  server.send(
    200,"application/json","{\"ok\":true}"
  );
}

// =====================================
// MOVIMENTO MANUAL
// =====================================
void moverManual() {

  if (modoAutomatico) {
    server.send(
      409,"application/json",
      "{\"erro\":\"Ative o modo manual\"}"
    );
    return;
  }

  if (noiteEstacionada) {
    server.send(
      409,"application/json",
      "{\"erro\":\"Painel em repouso noturno\"}"
    );
    return;
  }

  String eixo = server.arg("eixo");

  int direcao = server.arg("direcao").toInt();

  if (eixo == "h") {

    anguloH += direcao * PASSO_MANUAL;

    anguloH = constrain(
      anguloH,LIMITE_H_MIN,LIMITE_H_MAX
    );
  }

  if (eixo == "v") {

    anguloV += direcao * PASSO_MANUAL;

    anguloV = constrain(
      anguloV,LIMITE_V_MIN,LIMITE_V_MAX
    );
  }

  aplicarPosicao();

  server.send(
    200,"application/json","{\"ok\":true}"
  );
}

// =====================================
// POSICAO INICIAL
// =====================================
void posicaoInicial() {

  if (modoAutomatico || noiteEstacionada) {
    server.send(
      409,"application/json",
      "{\"erro\":\"Comando indisponivel\"}"
    );
    return;
  }

  anguloH = INICIO_H;
  anguloV = INICIO_V;

  aplicarPosicao();

  server.send(
    200,"application/json","{\"ok\":true}"
  );
}

// =====================================
// INFORMACOES PARA O CELULAR
// =====================================
void estadoAtual() {

  String modo = modoAutomatico ? "AUTO" : "MANUAL";

  String estado = noiteEstacionada ?
  "NOITE - REPOUSO" : "ATIVO";

  String resposta = "{";

  resposta += "\"h\":" + String(anguloH) + ",";
  resposta += "\"v\":" + String(anguloV) + ",";
  resposta += "\"luz\":" + String(luminosidadeMedia) + ",";
  resposta += "\"modo\":\"" + modo + "\",";
  resposta += "\"estado\":\"" + estado + "\"";

  resposta += "}";

  server.send(
    200,"application/json",resposta
  );
}

// =====================================
// CONFIGURACAO
// =====================================
void setup() {

  Serial.begin(115200);

  analogReadResolution(12);

  servoHorizontal.setPeriodHertz(50);
  servoVertical.setPeriodHertz(50);

  servoHorizontal.attach(
    PINO_SERVO_H,500,2400
  );

  servoVertical.attach(
    PINO_SERVO_V,500,2400
  );

  aplicarPosicao();

  WiFi.mode(WIFI_AP);
  WiFi.softAP(nomeRede,senhaRede);

  Serial.println("Torre iniciada!");

  Serial.print("Endereco: ");
  Serial.println(WiFi.softAPIP());

  server.on("/",paginaInicial);
  server.on("/modo",mudarModo);
  server.on("/mover",moverManual);
  server.on("/inicio",posicaoInicial);
  server.on("/estado",estadoAtual);

  server.begin();
}

// =====================================
// LOOP PRINCIPAL
// =====================================
void loop() {

  server.handleClient();

  if (millis() - ultimoMovimento >=
      INTERVALO_MOVIMENTO) {

    ultimoMovimento = millis();

    // Verifica dia e noite em qualquer modo
    verificarDiaNoite();

    // Rastreamento apenas no automatico
    if (modoAutomatico && !noiteEstacionada) {
      rastrearSol();
    }
  }
}