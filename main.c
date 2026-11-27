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
int anguloV = 80;

// Ajustar conforme a montagem mecanica
// Repouso noturno no centro do horizontal (P15): estacionado em 20 graus,
// no inverno o painel acordava preso no limite ate perto do meio-dia.
const int INICIO_H = 90;
// Vertical limitado a 80 graus (P16): acima disso o peso do painel o faz
// passar do ponto e tombar para o outro lado, e o MG996R nao o traz de volta.
const int INICIO_V = 80;

const int LIMITE_H_MIN = 20;
const int LIMITE_H_MAX = 160;
const int LIMITE_V_MIN = 20;
const int LIMITE_V_MAX = 80;

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

// Ultima leitura de cada LDR (mostrada na IHM do celular)
int leituraSE = 0;
int leituraSD = 0;
int leituraIE = 0;
int leituraID = 0;

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
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0b2a5b">
<title>Solar Smart Tower · IHM</title>
<style>
:root{--azul:#0b2a5b;--azul2:#16407f;--ouro:#f5b800;--fundo:#eef1f6;--card:#fff;--txt:#14213d;--sub:#66728a;--linha:#e3e7ee;--ok:#12805c;--erro:#c0392b;--r:14px}
*{box-sizing:border-box;margin:0;padding:0}
html,body{overflow-x:hidden;-webkit-text-size-adjust:100%}
html{scrollbar-width:none}::-webkit-scrollbar{display:none}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--fundo);color:var(--txt);font-size:15px;line-height:1.35;-webkit-tap-highlight-color:transparent}
.num{font-variant-numeric:tabular-nums}
header{background:linear-gradient(135deg,var(--azul),var(--azul2));color:#fff;padding:calc(14px + env(safe-area-inset-top)) 16px 16px;border-bottom:4px solid var(--ouro)}
.topo{display:flex;align-items:center;gap:12px;max-width:520px;margin:0 auto}
.topo svg{flex:none}
.marca{flex:1;min-width:0}
.marca h1{font-size:17px;font-weight:700;letter-spacing:.2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.marca p{font-size:11.5px;opacity:.8;letter-spacing:.3px}
.pilula{display:flex;align-items:center;gap:6px;font-size:11.5px;font-weight:600;padding:5px 10px;border-radius:99px;background:rgba(255,255,255,.12);white-space:nowrap}
.pilula i{width:8px;height:8px;border-radius:50%;background:#9aa4b5}
.pilula.ok i{background:#3ddc97;box-shadow:0 0 0 3px rgba(61,220,151,.25)}
.pilula.erro i{background:#ff6b5e}
main{max-width:520px;margin:0 auto;padding:14px 12px calc(24px + env(safe-area-inset-bottom));display:grid;grid-template-columns:minmax(0,1fr);gap:12px}
.card{background:var(--card);border-radius:var(--r);padding:14px;box-shadow:0 1px 2px rgba(11,42,91,.06),0 4px 14px rgba(11,42,91,.05)}
.card h2{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--sub);margin-bottom:10px;display:flex;justify-content:space-between;align-items:center}
.card h2 span{text-transform:none;letter-spacing:0;font-weight:600;color:var(--sub)}
.resumo{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.chip{min-width:0;background:var(--card);border-radius:12px;padding:10px;box-shadow:0 1px 2px rgba(11,42,91,.06)}
.chip small{display:block;font-size:10.5px;color:var(--sub);text-transform:uppercase;letter-spacing:.6px;font-weight:700}
.chip b{display:block;font-size:14.5px;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chip em{display:block;font-style:normal;font-size:11px;color:var(--sub);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.seg{display:grid;grid-template-columns:1fr 1fr;background:var(--fundo);border-radius:12px;padding:4px;gap:4px}
.seg button{border:0;border-radius:9px;padding:12px 6px;font:inherit;font-weight:700;font-size:14px;background:transparent;color:var(--sub);cursor:pointer}
.seg button.ativo{background:var(--azul);color:#fff;box-shadow:0 2px 6px rgba(11,42,91,.3)}
.ldrs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.ldr{min-width:0;border:1px solid var(--linha);border-radius:11px;padding:9px 10px}
.ldr div{display:flex;justify-content:space-between;font-size:12px;color:var(--sub);font-weight:600}
.ldr b{font-size:20px;display:block;margin:2px 0 6px}
.barra{height:6px;background:var(--fundo);border-radius:9px;overflow:hidden}
.barra i{display:block;height:100%;width:0;border-radius:9px;transition:width .4s}
.media{display:flex;justify-content:space-between;align-items:baseline;margin:10px 2px 4px;font-size:13px;color:var(--sub)}
.media b{color:var(--txt);font-size:15px}
.eq{margin-top:12px}
.eq .rot{display:flex;justify-content:space-between;font-size:11.5px;color:var(--sub);font-weight:600;margin-bottom:5px}
.trilho{position:relative;height:22px;background:var(--fundo);border-radius:7px}
.trilho .zona{position:absolute;top:0;bottom:0;background:rgba(18,128,92,.16);border-left:1px dashed rgba(18,128,92,.5);border-right:1px dashed rgba(18,128,92,.5)}
.trilho .meio{position:absolute;left:50%;top:3px;bottom:3px;width:1px;background:#b9c1cf}
.trilho .cursor{position:absolute;top:2px;width:18px;height:18px;margin-left:-9px;border-radius:50%;background:var(--azul);border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.3);transition:left .4s;left:50%}
.eq p{font-size:12px;margin-top:4px;color:var(--sub)}
.medidores{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;text-align:center}
.medidores svg{width:100%;height:auto;display:block}
.medidores b{font-size:22px;display:block;margin-top:-6px}
.medidores small{font-size:11.5px;color:var(--sub);font-weight:600}
canvas{width:100%;height:170px;display:block}
.legenda{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:11.5px;color:var(--sub);margin-top:8px}
.legenda span{display:flex;align-items:center;gap:5px}
.legenda i{width:12px;height:3px;border-radius:2px}
.dpad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;max-width:270px;margin:4px auto 0}
.dpad button{aspect-ratio:1/1;border:0;border-radius:14px;background:var(--fundo);color:var(--azul);display:flex;align-items:center;justify-content:center;cursor:pointer;touch-action:manipulation;user-select:none;-webkit-user-select:none;transition:transform .08s,background .15s}
.dpad button:active{transform:scale(.94);background:#dfe5ef}
.dpad button.casa{background:var(--azul);color:#fff;flex-direction:column;gap:2px;font:700 10px system-ui,sans-serif;letter-spacing:.3px}
.dpad .vazio{visibility:hidden}
.bloqueio{opacity:.4;pointer-events:none;filter:grayscale(1)}
.aviso{font-size:12.5px;text-align:center;color:var(--sub);margin-top:10px;min-height:17px}
footer{text-align:center;font-size:11px;color:var(--sub);padding:2px 0 8px;line-height:1.6}
@media (max-width:360px){body{font-size:14px}main{padding-left:8px;padding-right:8px}.card{padding:12px}.chip{padding:8px}.chip b{font-size:13px}.ldr b{font-size:18px}.card h2 span{display:none}}
#toast{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom));transform:translate(-50%,30px);background:#14213d;color:#fff;padding:10px 16px;border-radius:10px;font-size:13px;opacity:0;transition:.25s;pointer-events:none;max-width:90vw}
#toast.on{opacity:1;transform:translate(-50%,0)}
</style>
</head>
<body>
<header>
 <div class="topo">
  <svg width="46" height="46" viewBox="0 0 46 46" aria-label="UNIP">
   <rect width="46" height="46" rx="10" fill="#fff"/>
   <text x="23" y="27" text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="15" fill="#0b2a5b" letter-spacing="-.5">UNIP</text>
   <rect x="9" y="32" width="28" height="4" rx="2" fill="#f5b800"/>
  </svg>
  <div class="marca">
   <h1>Solar Smart Tower</h1>
   <p>IHM do rastreador solar</p>
  </div>
  <div class="pilula" id="con"><i></i><span>Conectando</span></div>
 </div>
</header>

<main>
 <section class="resumo">
  <div class="chip"><small>Modo</small><b id="cModo">—</b><em id="cModoSub">&nbsp;</em></div>
  <div class="chip"><small>Período</small><b id="cPer">—</b><em id="cPerSub">&nbsp;</em></div>
  <div class="chip"><small>Ligado há</small><b class="num" id="cUp">—</b><em id="cLat">&nbsp;</em></div>
 </section>

 <section class="card">
  <h2>Modo de operação</h2>
  <div class="seg">
   <button id="bAuto" onclick="modo('auto')">Automático</button>
   <button id="bMan" onclick="modo('manual')">Manual</button>
  </div>
 </section>

 <section class="card">
  <h2>Sensores de luz <span>ADC 12 bits · 0–4095</span></h2>
  <div class="ldrs">
   <div class="ldr"><div>Sup. esquerdo<span>SE</span></div><b class="num" id="vSE">—</b><div class="barra"><i id="bSE" style="background:#1f6feb"></i></div></div>
   <div class="ldr"><div>Sup. direito<span>SD</span></div><b class="num" id="vSD">—</b><div class="barra"><i id="bSD" style="background:#e0a100"></i></div></div>
   <div class="ldr"><div>Inf. esquerdo<span>IE</span></div><b class="num" id="vIE">—</b><div class="barra"><i id="bIE" style="background:#12805c"></i></div></div>
   <div class="ldr"><div>Inf. direito<span>ID</span></div><b class="num" id="vID">—</b><div class="barra"><i id="bID" style="background:#d1495b"></i></div></div>
  </div>
  <div class="media"><span>Luminosidade média</span><b class="num" id="vMed">—</b></div>
  <div class="eq">
   <div class="rot"><span>◀ Esquerda</span><span>Diferença horizontal</span><span>Direita ▶</span></div>
   <div class="trilho"><div class="zona" id="zH"></div><div class="meio"></div><div class="cursor" id="kH"></div></div>
   <p id="tH">&nbsp;</p>
  </div>
  <div class="eq">
   <div class="rot"><span>▲ Superior</span><span>Diferença vertical</span><span>Inferior ▼</span></div>
   <div class="trilho"><div class="zona" id="zV"></div><div class="meio"></div><div class="cursor" id="kV"></div></div>
   <p id="tV">&nbsp;</p>
  </div>
 </section>

 <section class="card">
  <h2>Posição dos servos <span>H 20°–160° · V 20°–80°</span></h2>
  <div class="medidores">
   <div><svg viewBox="0 0 120 70" id="gH"></svg><b class="num" id="aH">—</b><small>Horizontal · base</small></div>
   <div><svg viewBox="0 0 120 70" id="gV"></svg><b class="num" id="aV">—</b><small>Inclinação · painel</small></div>
  </div>
 </section>

 <section class="card">
  <h2>Histórico de luminosidade <span>últimos 60 s</span></h2>
  <canvas id="graf"></canvas>
  <div class="legenda">
   <span><i style="background:#0b2a5b;height:4px"></i>Média</span>
   <span><i style="background:#1f6feb"></i>SE</span>
   <span><i style="background:#e0a100"></i>SD</span>
   <span><i style="background:#12805c"></i>IE</span>
   <span><i style="background:#d1495b"></i>ID</span>
   <span><i style="background:repeating-linear-gradient(90deg,#8a94a6 0 3px,transparent 3px 6px)"></i>Limites noite/dia</span>
  </div>
 </section>

 <section class="card">
  <h2>Controle manual <span>segure para repetir</span></h2>
  <div class="dpad" id="dpad">
   <div class="vazio"></div>
   <button data-e="v" data-d="1" aria-label="Subir"><svg width="30" height="30" viewBox="0 0 24 24"><path d="M6 15l6-6 6 6" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
   <div class="vazio"></div>
   <button data-e="h" data-d="-1" aria-label="Esquerda"><svg width="30" height="30" viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
   <button class="casa" id="bCasa" aria-label="Posição inicial"><svg width="24" height="24" viewBox="0 0 24 24"><path d="M4 11l8-7 8 7M6 9.5V20h4.5v-5h3v5H18V9.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>INÍCIO</button>
   <button data-e="h" data-d="1" aria-label="Direita"><svg width="30" height="30" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
   <div class="vazio"></div>
   <button data-e="v" data-d="-1" aria-label="Descer"><svg width="30" height="30" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
   <div class="vazio"></div>
  </div>
  <p class="aviso" id="aviso">&nbsp;</p>
 </section>

 <footer>Rede <b>SOLAR_TOWER</b> · 192.168.4.1<br>UNIP · Automação Industrial · PIM II</footer>
</main>
<div id="toast"></div>

<script>
const $ = (i) => document.getElementById(i);
const CORES = { se: "#1f6feb", sd: "#e0a100", ie: "#12805c", id: "#d1495b" };
const N = 60;
let hist = [], ultimo = null, okEm = 0, ocupado = false;

function aviso(t) {
  const e = $("toast"); e.textContent = t; e.classList.add("on");
  clearTimeout(aviso.t); aviso.t = setTimeout(() => e.classList.remove("on"), 2200);
}

async function chamar(url) {
  try {
    const t0 = Date.now();
    const r = await fetch(url);
    const d = await r.json();
    okEm = Date.now(); chamar.lat = okEm - t0;
    if (r.status >= 400) { aviso(d.erro || "Comando recusado"); return null; }
    return d;
  } catch (e) { return null; }
}

async function modo(m) { await chamar("/modo?valor=" + m); atualizar(); }

/* Medidor semicircular: 0° a 180° do servo; faixa útil 20°–160° */
function ponto(a, r) { const t = Math.PI * (1 - a / 180); return [60 + r * Math.cos(t), 62 - r * Math.sin(t)]; }
function arco(a0, a1, r) { const p = ponto(a0, r), q = ponto(a1, r); return "M" + p[0].toFixed(1) + " " + p[1].toFixed(1) + " A" + r + " " + r + " 0 0 1 " + q[0].toFixed(1) + " " + q[1].toFixed(1); }
function medidor(id, a, max = 160) {
  const p = ponto(a, 40);
  $(id).innerHTML =
    '<path d="' + arco(0, 180, 50) + '" stroke="#eef1f6" stroke-width="10" fill="none" stroke-linecap="round"/>' +
    '<path d="' + arco(20, max, 50) + '" stroke="#d6dce7" stroke-width="10" fill="none"/>' +
    '<path d="' + arco(20, Math.max(20, a), 50) + '" stroke="#f5b800" stroke-width="10" fill="none"/>' +
    '<line x1="60" y1="62" x2="' + p[0].toFixed(1) + '" y2="' + p[1].toFixed(1) + '" stroke="#0b2a5b" stroke-width="3.5" stroke-linecap="round"/>' +
    '<circle cx="60" cy="62" r="5.5" fill="#0b2a5b"/>';
}

/* Indicador de diferença entre lados, com a zona morta (TOLERANCIA) */
function equilibrio(k, z, t, a, b, tol, nomes) {
  const esc = tol * 6, d = a - b;
  const x = 50 + Math.max(-1, Math.min(1, d / esc)) * 46;
  $(k).style.left = (100 - x) + "%";
  const lz = 50 - (tol / esc) * 46;
  $(z).style.left = lz + "%"; $(z).style.right = lz + "%";
  $(t).textContent = Math.abs(d) <= tol ? "Equilibrado (dentro da zona morta de ±" + tol + ")"
    : "Mais luz " + (d > 0 ? nomes[0] : nomes[1]) + " (" + Math.abs(d) + ")";
}

function grafico() {
  const c = $("graf"), r = window.devicePixelRatio || 1, w = c.clientWidth, h = c.clientHeight;
  if (c.width !== Math.round(w * r)) { c.width = Math.round(w * r); c.height = Math.round(h * r); }
  const g = c.getContext("2d"); g.setTransform(r, 0, 0, r, 0, 0); g.clearRect(0, 0, w, h);
  const L = 34, T = 6, W = w - L - 6, H = h - T - 18;
  const y = (v) => T + H - (v / 4095) * H, x = (i) => L + W * (1 - (hist.length - 1 - i) / (N - 1));
  g.font = "10px system-ui,sans-serif"; g.lineWidth = 1;
  [0, 1024, 2048, 3072, 4095].forEach((v) => {
    g.strokeStyle = "#eceff4"; g.beginPath(); g.moveTo(L, y(v)); g.lineTo(L + W, y(v)); g.stroke();
    g.fillStyle = "#8a94a6"; g.textAlign = "right"; g.fillText(v, L - 5, y(v) + 3);
  });
  g.textAlign = "center";
  [["−60 s", 0], ["−30 s", 0.5], ["agora", 1]].forEach((p) => g.fillText(p[0], L + W * p[1] - (p[1] === 1 ? 14 : p[1] === 0 ? -14 : 0), h - 4));
  if (ultimo) {
    g.setLineDash([4, 4]); g.strokeStyle = "#8a94a6";
    [ultimo.limNoite, ultimo.limDia].forEach((v) => { g.beginPath(); g.moveTo(L, y(v)); g.lineTo(L + W, y(v)); g.stroke(); });
    g.setLineDash([]);
  }
  const linha = (k, cor, lw) => {
    if (hist.length < 2) return;
    g.strokeStyle = cor; g.lineWidth = lw; g.lineJoin = "round"; g.beginPath();
    hist.forEach((p, i) => (i ? g.lineTo(x(i), y(p[k])) : g.moveTo(x(i), y(p[k]))));
    g.stroke();
  };
  ["se", "sd", "ie", "id"].forEach((k) => linha(k, CORES[k], 1.4));
  linha("luz", "#0b2a5b", 2.6);
}

function tempo(s) {
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
  return (h ? h + "h " : "") + String(m).padStart(h ? 2 : 1, "0") + "m " + String(x).padStart(2, "0") + "s";
}

const PER = {
  DIA: ["☀️ Dia", "Rastreando a luz"],
  ANOITECENDO: ["🌇 Escurecendo", "Repouso em "],
  NOITE: ["🌙 Noite", "Painel em repouso"],
  AMANHECENDO: ["🌅 Amanhecendo", "Retoma em "]
};

function mostrar(d) {
  ultimo = d;
  const auto = d.modo === "AUTO";
  $("bAuto").className = auto ? "ativo" : ""; $("bMan").className = auto ? "" : "ativo";
  $("cModo").textContent = auto ? "Automático" : "Manual";
  $("cModoSub").textContent = auto ? "Seguindo o sol" : "Comando pelo celular";
  const p = PER[d.periodo] || PER.DIA;
  $("cPer").textContent = p[0];
  $("cPerSub").textContent = p[1] + (d.faltam ? d.faltam + " s" : "");
  $("cUp").textContent = tempo(d.ligado);

  ["se", "sd", "ie", "id"].forEach((k) => {
    const K = k.toUpperCase();
    $("v" + K).textContent = d[k];
    $("b" + K).style.width = (d[k] / 40.95).toFixed(1) + "%";
  });
  $("vMed").textContent = d.luz + "  (" + Math.round(d.luz / 40.95) + "%)";
  equilibrio("kH", "zH", "tH", (d.se + d.ie) / 2 | 0, (d.sd + d.id) / 2 | 0, d.tol, ["à esquerda", "à direita"]);
  equilibrio("kV", "zV", "tV", (d.se + d.sd) / 2 | 0, (d.ie + d.id) / 2 | 0, d.tol, ["em cima", "embaixo"]);

  medidor("gH", d.h); medidor("gV", d.v, 80);
  $("aH").textContent = d.h + "°"; $("aV").textContent = d.v + "°";

  const noite = d.estado.indexOf("NOITE") === 0;
  const livre = !auto && !noite;
  $("dpad").className = "dpad" + (livre ? "" : " bloqueio");
  $("aviso").textContent = noite ? "Painel em repouso noturno: comandos bloqueados."
    : auto ? "Selecione o modo Manual para mover o painel." : "Toque nas setas para mover o painel 5° por vez.";

  hist.push({ luz: d.luz, se: d.se, sd: d.sd, ie: d.ie, id: d.id });
  if (hist.length > N) hist.shift();
  grafico();
}

async function atualizar() {
  if (ocupado) return;
  ocupado = true;
  const d = await chamar("/estado");
  ocupado = false;
  if (d) mostrar(d);
  const on = Date.now() - okEm < 4000;
  $("con").className = "pilula " + (on ? "ok" : "erro");
  $("con").lastChild.textContent = on ? "Online" : "Offline";
  $("cLat").textContent = on && chamar.lat !== undefined ? "Resposta " + chamar.lat + " ms" : " ";
}

/* Setas: um passo ao tocar e repetição enquanto o dedo estiver pressionado */
document.querySelectorAll("#dpad button[data-e]").forEach((b) => {
  let rep = null, ativo = false;
  const passo = async () => { await chamar("/mover?eixo=" + b.dataset.e + "&direcao=" + b.dataset.d); atualizar(); };
  const parar = () => { ativo = false; clearTimeout(rep); };
  const ciclo = async () => { if (!ativo) return; await passo(); rep = setTimeout(ciclo, 220); };
  b.addEventListener("pointerdown", (e) => { e.preventDefault(); ativo = true; passo(); rep = setTimeout(ciclo, 450); });
  ["pointerup", "pointerleave", "pointercancel"].forEach((ev) => b.addEventListener(ev, parar));
});
$("bCasa").addEventListener("click", async () => { if (await chamar("/inicio")) aviso("Painel voltando à posição inicial"); atualizar(); });

window.addEventListener("resize", grafico);
setInterval(atualizar, 1000);
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

  leituraSE = se;
  leituraSD = sd;
  leituraIE = ie;
  leituraID = id;
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

  // Periodo do dia e segundos que faltam para a proxima transicao
  unsigned long agora = millis();
  String periodo = "DIA";
  long faltam = 0;

  if (noiteEstacionada) {
    periodo = "NOITE";
    if (inicioClaro != 0) {
      periodo = "AMANHECENDO";
      faltam = (long)(TEMPO_DIA - (agora - inicioClaro)) / 1000;
    }
  } else if (inicioEscuro != 0) {
    periodo = "ANOITECENDO";
    faltam = (long)(TEMPO_NOITE - (agora - inicioEscuro)) / 1000;
  }

  if (faltam < 0) faltam = 0;

  String resposta = "{";

  resposta += "\"h\":" + String(anguloH) + ",";
  resposta += "\"v\":" + String(anguloV) + ",";
  resposta += "\"luz\":" + String(luminosidadeMedia) + ",";
  resposta += "\"se\":" + String(leituraSE) + ",";
  resposta += "\"sd\":" + String(leituraSD) + ",";
  resposta += "\"ie\":" + String(leituraIE) + ",";
  resposta += "\"id\":" + String(leituraID) + ",";
  resposta += "\"tol\":" + String(TOLERANCIA) + ",";
  resposta += "\"limNoite\":" + String(LIMITE_NOITE) + ",";
  resposta += "\"limDia\":" + String(LIMITE_DIA) + ",";
  resposta += "\"periodo\":\"" + periodo + "\",";
  resposta += "\"faltam\":" + String(faltam) + ",";
  resposta += "\"ligado\":" + String(agora / 1000) + ",";
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