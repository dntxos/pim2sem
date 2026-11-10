// Simulador 3D do rastreador solar.
// - Estrutura: STLs reais de 3d_material/stl, agrupados por eixo (fixo / azimute / elevação).
// - Cérebro: o firmware compilado (main.c -> .hex) rodando num ATmega328P emulado (avr8js).
// - Sensores: a luz em cada LDR é calculada por raycasting contra as peças (sombra real do divisor em cruz)
//   e convertida em tensão pelo divisor LDR + 10 kΩ, que alimenta o ADC emulado.
import * as THREE from 'three';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Arduino328P, FREQ_HZ } from './arduino.js';
import { Esp32Simulado } from './esp32.js';
import {
  PECAS, EIXO_AZIMUTE, EIXO_ELEVACAO, INCLINACAO_EXPORTADA_GRAUS, N0, U0, LDRS, RAIO_LDR, PLACA, ELEVACAO_LDR,
} from './montagem.js';
import { posicaoSolar, direcaoSolar, azElDeDirecao } from './sol.js';
import { resistenciaLdr, tensaoDivisor, rng, gauss } from './sensores.js';

const GRAU = Math.PI / 180;
const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------- estado
const estado = {
  rodando: true,
  modoSol: 'dia',
  hora: 9,
  dia: 172,
  latitude: -23.55,
  horasPorSegundo: 0.2,
  azManual: 45,
  elManual: 40,
  luxDireta: 1000,
  difusa: 0.1,
  fiacao: 'codigo',
  invH: false,
  invV: false,
  variacao: 0.1,
  ruidoMv: 5,
  velSim: 1,
  sol: [0, 1, 0],
  servoH: 90, // ângulo físico atual (°)
  servoV: 90,
  energiaTrack: 0,
  energiaFixa: 0,
  linhasSerial: [],
  amostras: [],
  flutuante: 2.5,
};
let uno = null;
let hexAtual = null;
let fatoresLdr = [1, 1, 1, 1];
const leituras = LDRS.map(() => ({ lux: 0, volts: 0 }));

// ---------------------------------------------------------------- cena
const cenaEl = $('cena');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
cenaEl.prepend(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, 1, 5, 6000);
camera.position.set(-600, 420, 330); // do Noroeste: vê a face ativa da placa (voltada ao Norte no hemisfério sul)
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 150, 0);
controls.enableDamping = true;
controls.maxPolarAngle = 89 * GRAU;

const hemi = new THREE.HemisphereLight(0xdfeaff, 0x8a7f70, 0.9);
scene.add(hemi);
const luzSol = new THREE.DirectionalLight(0xfff3d6, 2.2);
luzSol.castShadow = true;
luzSol.shadow.mapSize.set(2048, 2048);
Object.assign(luzSol.shadow.camera, { left: -260, right: 260, top: 260, bottom: -260, near: 10, far: 2000 });
luzSol.shadow.bias = -0.0004;
luzSol.target.position.set(0, 150, 0);
scene.add(luzSol, luzSol.target);

// chão + bússola
const chao = new THREE.Mesh(
  new THREE.CircleGeometry(700, 64).rotateX(-Math.PI / 2),
  new THREE.MeshStandardMaterial({ color: 0x9fae8f, roughness: 1 }),
);
chao.receiveShadow = true;
scene.add(chao);
const grade = new THREE.PolarGridHelper(600, 8, 6, 64, 0x6f7d63, 0x7f8d73);
grade.position.y = 0.3;
scene.add(grade);
function rotulo(texto, cor = '#1d2330', escala = 40) {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const g = c.getContext('2d');
  g.fillStyle = 'rgba(255,255,255,0.85)';
  g.beginPath(); g.arc(64, 64, 56, 0, Math.PI * 2); g.fill();
  g.fillStyle = cor; g.font = 'bold 64px system-ui'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(texto, 64, 68);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), depthTest: false }));
  s.scale.set(escala, escala, 1);
  return s;
}
for (const [txt, az] of [['N', 0], ['L', 90], ['S', 180], ['O', 270]]) {
  const d = direcaoSolar(az, 0);
  const s = rotulo(txt, txt === 'N' ? '#b91c1c' : '#1d2330');
  s.position.set(d[0] * 620, 20, d[2] * 620);
  scene.add(s);
}

// grupos da cinemática (origem = eixo do azimute no chão)
const ORIGEM = new THREE.Vector3(EIXO_AZIMUTE.x, 0, EIXO_AZIMUTE.z);
const PIVO_EL = new THREE.Vector3(EIXO_ELEVACAO.x, EIXO_ELEVACAO.y, EIXO_AZIMUTE.z);
const grupoFixo = new THREE.Group();
const grupoAz = new THREE.Group();
const grupoEl = new THREE.Group();
grupoEl.position.copy(PIVO_EL).sub(ORIGEM);
grupoAz.add(grupoEl);
scene.add(grupoFixo, grupoAz);
const deslocamento = { fixo: ORIGEM, azimute: ORIGEM, elevacao: PIVO_EL };
const grupoDe = { fixo: grupoFixo, azimute: grupoAz, elevacao: grupoEl };
const oclusores = [];

function addMalha(geo, material, grupo) {
  geo.translate(-deslocamento[grupo].x, -deslocamento[grupo].y, -deslocamento[grupo].z);
  const m = new THREE.Mesh(geo, material);
  m.castShadow = m.receiveShadow = true;
  grupoDe[grupo].add(m);
  oclusores.push(m);
  return m;
}

// placa fotovoltaica (não está nos STLs)
{
  const n = new THREE.Vector3(...N0);
  const u = new THREE.Vector3(...U0);
  const z = new THREE.Vector3(0, 0, 1);
  const geo = new THREE.BoxGeometry(PLACA.altura, PLACA.espessura, PLACA.largura);
  // colunas da base: X local -> u, Y local -> n, Z local -> z
  const m = new THREE.Matrix4().makeBasis(u, n, z).setPosition(new THREE.Vector3(...PLACA.centro));
  geo.applyMatrix4(m);
  const mats = [0x9aa4b2, 0x9aa4b2, 0x0d2a6b, 0x9aa4b2, 0x9aa4b2, 0x9aa4b2].map(
    (c, i) => new THREE.MeshStandardMaterial({ color: c, roughness: i === 2 ? 0.25 : 0.6, metalness: i === 2 ? 0.3 : 0.1 }),
  );
  addMalha(geo, mats, 'elevacao').name = 'PAINEL';
  // células (linhas desenhadas na face)
  const linhas = [];
  for (let i = -2; i <= 2; i++) {
    const a = i * (PLACA.altura / 6);
    linhas.push(new THREE.Vector3(...PLACA.centro).addScaledVector(n, PLACA.espessura / 2 + 0.3).addScaledVector(u, a).addScaledVector(z, -PLACA.largura / 2));
    linhas.push(new THREE.Vector3(...PLACA.centro).addScaledVector(n, PLACA.espessura / 2 + 0.3).addScaledVector(u, a).addScaledVector(z, PLACA.largura / 2));
  }
  for (let i = -3; i <= 3; i++) {
    const b = i * (PLACA.largura / 8);
    linhas.push(new THREE.Vector3(...PLACA.centro).addScaledVector(n, PLACA.espessura / 2 + 0.3).addScaledVector(z, b).addScaledVector(u, -PLACA.altura / 2));
    linhas.push(new THREE.Vector3(...PLACA.centro).addScaledVector(n, PLACA.espessura / 2 + 0.3).addScaledVector(z, b).addScaledVector(u, PLACA.altura / 2));
  }
  const lg = new THREE.BufferGeometry().setFromPoints(linhas);
  lg.translate(-PIVO_EL.x, -PIVO_EL.y, -PIVO_EL.z);
  grupoEl.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0x8fb3ff, transparent: true, opacity: 0.35 })));
}

// servos MG996R ilustrativos (corpo 40,7 × 19,7 × 42,9 mm), não fazem parte dos STLs
{
  const mat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.5 });
  const sH = new THREE.Mesh(new THREE.BoxGeometry(19.7, 36, 40.7), mat);
  sH.position.set(0, 68.7 - 36 / 2, 10);
  sH.castShadow = true;
  grupoFixo.add(sH);
  const sV = new THREE.Mesh(new THREE.BoxGeometry(19.7, 40.7, 42.9), mat);
  sV.position.set(0, EIXO_ELEVACAO.y - 10, 0);
  sV.castShadow = true;
  grupoAz.add(sV);
}

// LDRs
const malhasLdr = LDRS.map((l) => {
  const geo = new THREE.CylinderGeometry(RAIO_LDR, RAIO_LDR, 2, 20);
  const n = new THREE.Vector3(...N0);
  geo.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), n));
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0xc98a3a, emissive: 0x000000 }));
  m.position.set(...l.posicao).sub(PIVO_EL);
  grupoEl.add(m);
  const r = rotulo(l.id, '#1d2330', 9);
  r.position.copy(m.position).addScaledVector(n, 34);
  grupoEl.add(r);
  return m;
});

// sol, raio e normal
const DIST_SOL = 900;
const sol = new THREE.Mesh(new THREE.SphereGeometry(28, 32, 16), new THREE.MeshBasicMaterial({ color: 0xffd34d }));
const halo = new THREE.Mesh(new THREE.SphereGeometry(60, 24, 12), new THREE.MeshBasicMaterial({ color: 0xffd34d, transparent: true, opacity: 0.18 }));
sol.add(halo);
scene.add(sol);
const raioGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
const raio = new THREE.Line(raioGeo, new THREE.LineDashedMaterial({ color: 0xffb300, dashSize: 12, gapSize: 8 }));
scene.add(raio);
const setaNormal = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(), 140, 0x2563eb, 18, 9);
scene.add(setaNormal);

// ---------------------------------------------------------------- carga das peças
async function carregarPecas() {
  const loader = new STLLoader();
  await Promise.all(PECAS.map(async (p) => {
    const r = await fetch(p.url);
    if (!r.ok) throw new Error(`Não foi possível carregar ${p.arquivo}.STL (${r.status})`);
    const geo = loader.parse(await r.arrayBuffer());
    geo.computeVertexNormals();
    if (ELEVACAO_LDR && p.arquivo.startsWith('SUPORTE')) {
      geo.translate(N0[0] * ELEVACAO_LDR, N0[1] * ELEVACAO_LDR, 0);
    }
    addMalha(geo, new THREE.MeshStandardMaterial({ color: p.cor, roughness: 0.75 }), p.grupo).name = p.arquivo;
  }));
}

// ---------------------------------------------------------------- Arduino
// firmwareAtual: { tipo: 'nano', hex } ou { tipo: 'esp32', url, cfg }
let firmwareAtual = null;
const firmwares = { esp32: null, nano: null }; // firmwares conhecidos, para trocar sem ambiguidade
function iniciarArduino(hexTexto) {
  hexAtual = hexTexto;
  firmwareAtual = { tipo: 'nano', hex: hexTexto };
  uno = new Arduino328P(hexTexto, { onSerialLine: receberSerial });
  estado.amostras = [];
  mostrarCelular(false);
}
/** (Re)inicia o firmware atual, como apertar RESET. Para o ESP32 recria a instância WebAssembly. */
async function iniciarFirmware(fw = firmwareAtual) {
  if (!fw) return;
  if (fw.tipo === 'nano') return iniciarArduino(fw.hex);
  firmwareAtual = fw;
  uno = await Esp32Simulado.criar(fw.url, fw.cfg, { onSerialLine: receberSerial });
  estado.amostras = [];
  mostrarCelular(true);
}

// ---------------------------------------------------------------- celular (interface web do ESP32)
// A página é a do próprio main.c (rota "/"); os fetch() dela são entregues ao servidor simulado.
window.simHttp = (url) => (uno && uno.http ? uno.http(url) : { status: 503, tipo: 'text/plain', corpo: '' });
function mostrarCelular(visivel) {
  const box = $('boxCelular');
  if (!box) return;
  box.hidden = !visivel;
  if (!visivel) return;
  const pagina = uno.http('/').corpo;
  const ponte = `<script>window.fetch = async (u) => { const r = parent.simHttp(String(u));
    return { ok: r.status < 400, status: r.status, json: async () => JSON.parse(r.corpo), text: async () => r.corpo }; };<\/script>`;
  $('telaCelular').srcdoc = pagina.replace('<head>', '<head>' + ponte);
  $('ssidCelular').textContent = uno.ssid();
}
function receberSerial(linha) {
  const t = (uno ? uno.segundos : 0).toFixed(2).padStart(7);
  estado.linhasSerial.push(`[${t}s] ${linha.replace(/\r$/, '')}`);
  if (estado.linhasSerial.length > 2000) estado.linhasSerial.splice(0, 500);
  serialSujo = true;
}
let serialSujo = false;

// Mapa LDR -> canal analógico, conforme a fiação escolhida.
function canaisDaFiacao() {
  return estado.fiacao === 'codigo' ? [1, 2, 3, 4] : [0, 1, 2, 3];
}

// ---------------------------------------------------------------- física
const raycaster = new THREE.Raycaster();
const qEl = new THREE.Quaternion();
const vN = new THREE.Vector3();
const vU = new THREE.Vector3();
const vZ = new THREE.Vector3();
const vP = new THREE.Vector3();
const vS = new THREE.Vector3();
const AMOSTRAS_DISCO = [[0, 0], [0.7, 0], [-0.7, 0], [0, 0.7], [0, -0.7], [0.5, 0.5], [-0.5, -0.5], [0.5, -0.5], [-0.5, 0.5]];

function normalDaPlaca(destino) {
  grupoEl.getWorldQuaternion(qEl);
  return destino.set(...N0).applyQuaternion(qEl);
}

function calcularSensores() {
  scene.updateMatrixWorld();
  grupoEl.getWorldQuaternion(qEl);
  vN.set(...N0).applyQuaternion(qEl);
  vU.set(...U0).applyQuaternion(qEl);
  vZ.set(0, 0, 1).applyQuaternion(qEl);
  vS.set(...estado.sol);
  const solAcima = vS.y > 0;
  const cosi = vN.dot(vS);
  // luz difusa: só a parte do céu "vista" pela face (aprox.) e reduzida pelo poço do divisor
  const ceu = estado.luxDireta * estado.difusa * 0.5 * (1 + vN.y) * 0.5 * Math.max(0, Math.min(1, vS.y * 4 + 0.2));
  raycaster.far = 3000;
  LDRS.forEach((l, i) => {
    let direta = 0;
    if (solAcima && cosi > 0) {
      let vis = 0;
      malhasLdr[i].getWorldPosition(vP);
      for (const [a, b] of AMOSTRAS_DISCO) {
        const o = vP.clone().addScaledVector(vU, a * RAIO_LDR).addScaledVector(vZ, b * RAIO_LDR).addScaledVector(vN, 1.2);
        raycaster.set(o, vS);
        if (raycaster.intersectObjects(oclusores, false).length === 0) vis++;
      }
      direta = estado.luxDireta * cosi * (vis / AMOSTRAS_DISCO.length);
    }
    const lux = direta + ceu;
    const r = resistenciaLdr(lux, 15_000 * fatoresLdr[i]);
    const ruido = (estado.ruidoMv / 1000) * gauss();
    leituras[i].lux = lux;
    leituras[i].volts = Math.max(0, Math.min(5, tensaoDivisor(r) + ruido));
    // brilho visual do LDR
    const k = Math.min(1, lux / Math.max(1, estado.luxDireta));
    malhasLdr[i].material.emissive.setRGB(k * 0.9, k * 0.7, k * 0.2);
  });
}

function aplicarNoArduino() {
  for (let c = 0; c <= 5; c++) uno.setAnalog(c, 0);
  const canais = canaisDaFiacao();
  LDRS.forEach((_, i) => uno.setAnalog(canais[i], leituras[i].volts));
  if (estado.fiacao === 'diagrama') {
    // A4 sem nada ligado: entrada flutuante (valor imprevisível que deriva)
    estado.flutuante = Math.max(0.3, Math.min(4.7, estado.flutuante + 0.25 * gauss()));
    uno.setAnalog(4, estado.flutuante);
  }
}

// ângulo do servo -> pose da estrutura
function aplicarPose() {
  const sH = estado.invH ? 1 : -1;
  const sV = estado.invV ? -1 : 1;
  grupoAz.rotation.y = sH * (estado.servoH - 90) * GRAU;
  const inclinacao = sV * (estado.servoV - 90); // 0° = placa horizontal
  grupoEl.rotation.z = (inclinacao - INCLINACAO_EXPORTADA_GRAUS) * GRAU;
}

const VEL_SERVO = 400; // °/s (MG996R a 6 V ≈ 0,14–0,15 s / 60°)
function moverServos(dt) {
  for (const [pino, chave] of [[9, 'servoH'], [10, 'servoV']]) {
    const alvo = uno.anguloServo(pino);
    if (alvo == null) continue;
    const d = alvo - estado[chave];
    const passo = VEL_SERVO * dt;
    estado[chave] += Math.abs(d) <= passo ? d : Math.sign(d) * passo;
  }
}

function atualizarSol() {
  let az; let el;
  if (estado.modoSol === 'dia') {
    ({ azimute: az, elevacao: el } = posicaoSolar(estado.latitude, estado.dia, estado.hora));
  } else {
    az = estado.azManual; el = estado.elManual;
  }
  estado.sol = direcaoSolar(az, el);
  estado.azSol = az; estado.elSol = el;
  const p = new THREE.Vector3(...estado.sol).multiplyScalar(DIST_SOL);
  p.y += 150;
  sol.position.copy(p);
  luzSol.position.copy(p);
  const acima = el > 0;
  luzSol.intensity = acima ? 2.2 * Math.min(1, el / 10 + 0.2) : 0;
  const ceu = new THREE.Color().setHSL(0.58, 0.55, acima ? 0.55 + 0.25 * Math.min(1, el / 40) : 0.12);
  scene.background = ceu;
  hemi.intensity = acima ? 0.9 : 0.25;
}

// ---------------------------------------------------------------- laço principal
let ultimo = performance.now();
let acumGrafico = 0;
function quadro(agora) {
  const dtReal = Math.min(0.05, (agora - ultimo) / 1000);
  ultimo = agora;
  if (estado.rodando && uno) {
    avancar(dtReal);
  } else {
    atualizarSol();
  }
  atualizarCenaAuxiliar();
  controls.update();
  const t = performance.now();
  renderer.render(scene, camera);
  perf.render += performance.now() - t;
  perf.quadros++;
  atualizarUI();
  requestAnimationFrame(quadro);
}

/** Avança a simulação em `dtReal` segundos de relógio (multiplicado pela velocidade escolhida). */
function avancar(dtReal) {
  {
    if (estado.modoSol === 'dia' && estado.horasPorSegundo > 0) {
      estado.hora += dtReal * estado.horasPorSegundo;
      if (estado.hora > 19) estado.hora = 5;
      $('inHora').value = estado.hora;
      $('outHora').value = fmtHora(estado.hora);
    }
    atualizarSol();
    const dtSim = dtReal * estado.velSim;
    // passos de ~10 ms: sensores atualizados com frequência suficiente para o laço de ~100 ms
    let restante = dtSim;
    while (restante > 1e-6) {
      const passo = Math.min(0.01, restante);
      let t = performance.now();
      calcularSensores();
      perf.sensores += performance.now() - t;
      aplicarNoArduino();
      t = performance.now();
      uno.run(Math.round(passo * FREQ_HZ));
      perf.emulador += performance.now() - t;
      moverServos(passo);
      aplicarPose();
      restante -= passo;
    }
    integrarEnergia(dtReal);
    acumGrafico += dtSim;
    if (acumGrafico >= 0.1) { acumGrafico = 0; amostrar(); }
  }
}
// Depuração pelo console do navegador:
//   sim.perf               -> tempo gasto por etapa
//   sim.avancar(10)        -> avança 10 s de simulação de uma vez (sem esperar o relógio)
//   sim.estado / sim.erro()
const perf = { sensores: 0, emulador: 0, render: 0, quadros: 0 };
window.sim = {
  perf,
  estado,
  avancar: (seg) => {
    for (let t = 0; t < seg; t += 0.05) avancar(0.05);
    atualizarCenaAuxiliar();
    renderer.render(scene, camera);
  },
  erro: () => anguloErro(),
  leituras,
  /** Reinicia o Arduino (firmware volta ao setup(): servos em 90°/90°). Opcional: outro .hex. */
  /** Reinicia o firmware (como o botão RESET). `qual`: 'esp32' | 'nano' | texto de um .hex | omitido (o atual).
   *  Sempre confira sim.firmware() depois: rodadas anteriores podem ter trocado o firmware atual. */
  reiniciar: async (qual) => {
    if (qual === 'esp32') await iniciarFirmware(firmwares.esp32);
    else if (typeof qual === 'string' && qual.startsWith('esp32:')) {
      // variante de teste: simulator/firmware/variantes/<nome>.mjs (mesmos pinos do firmware atual)
      await iniciarFirmware({ ...firmwares.esp32, url: `../firmware/variantes/${qual.slice(6)}.mjs`, variante: qual });
    }
    else if (qual === 'nano') iniciarArduino(firmwares.nano ?? await fetch('firmware/nano_versao_anterior.hex').then((r) => r.text()));
    else if (qual) iniciarArduino(qual);
    else await iniciarFirmware();
    estado.servoH = 90; estado.servoV = 90; aplicarPose(); zerarEnergia();
    return firmwareAtual.variante ?? firmwareAtual.tipo;
  },
  http: (url) => window.simHttp(url),
  /** Roda um cenário completo a partir do RESET e devolve a série
   *  [t, H, V, erro, solAz, solEl, hora, energiaRastreador, energiaFixa] a cada `passo` s simulados. */
  traco: async (fw, cfg = {}, seg = 8, passo = 0.25) => {
    Object.assign(estado, { difusa: 0.1, ruidoMv: 5, variacao: 0.1, fiacao: 'codigo', luxDireta: 1000,
      horasPorSegundo: 0, velSim: 1, rodando: false }, cfg);
    sortearFatores();
    const hps = estado.horasPorSegundo;
    estado.horasPorSegundo = 0;
    const usado = await window.sim.reiniciar(fw);
    if (fw && usado !== fw) throw new Error(`firmware errado: ${usado}`);
    estado.horasPorSegundo = hps;
    const serie = [];
    for (let t = 0; t < seg - 1e-9; t += passo) {
      window.sim.avancar(passo);
      serie.push([+(t + passo).toFixed(2), +estado.servoH.toFixed(1), +estado.servoV.toFixed(1), +anguloErro().toFixed(2),
        +(estado.azSol ?? 0).toFixed(1), +(estado.elSol ?? 0).toFixed(1), +estado.hora.toFixed(3),
        +estado.energiaTrack.toFixed(3), +estado.energiaFixa.toFixed(3)]);
    }
    return serie;
  },
  colunas: ['t', 'H', 'V', 'erro', 'solAz', 'solEl', 'hora', 'eTrack', 'eFixa'],
  salvar: (nome, obj) => fetch(`http://127.0.0.1:8001/${nome}`, { method: 'POST', body: JSON.stringify(obj) }).then((r) => r.text()),
  firmware: () => firmwareAtual && (firmwareAtual.variante ?? firmwareAtual.tipo),
  /** Posiciona os servos (sem firmware) e devolve a luz em cada LDR.
   *  Atenção: o firmware guarda os próprios ângulos e vai sobrescrever esta pose ao rodar. */
  /** Diagnóstico: qual peça bloqueia o raio do centro de cada LDR até o sol (ou '-' se livre). */
  bloqueios: () => {
    scene.updateMatrixWorld(); grupoEl.getWorldQuaternion(qEl);
    const n = new THREE.Vector3(...N0).applyQuaternion(qEl); const sDir = new THREE.Vector3(...estado.sol);
    return LDRS.map((l, i) => {
      malhasLdr[i].getWorldPosition(vP); raycaster.set(vP.clone().addScaledVector(n, 1.2), sDir); raycaster.far = 3000;
      const hit = raycaster.intersectObjects(oclusores, false)[0];
      return `${l.id}:${hit ? hit.object.name || '?' : '-'}`;
    }).join(' ') + ` cos=${n.dot(sDir).toFixed(2)}`;
  },
  sondar: (h, v) => {
    estado.servoH = h; estado.servoV = v; aplicarPose(); atualizarSol(); calcularSensores();
    return LDRS.map((l, i) => `${l.id}=${Math.round(leituras[i].lux)}`).join(' ');
  },
};

function anguloErro() {
  normalDaPlaca(vN);
  vS.set(...estado.sol);
  return Math.acos(Math.max(-1, Math.min(1, vN.dot(vS)))) / GRAU;
}

function integrarEnergia(dtReal) {
  if (estado.modoSol !== 'dia' || estado.horasPorSegundo <= 0) return;
  const dh = dtReal * estado.horasPorSegundo;
  if (estado.sol[1] <= 0) return;
  normalDaPlaca(vN);
  const s = new THREE.Vector3(...estado.sol);
  estado.energiaTrack += estado.luxDireta * Math.max(0, vN.dot(s)) * dh / 1000;
  // placa fixa: voltada ao equador (Norte no hemisfério sul), inclinada na latitude
  const inc = Math.abs(estado.latitude) * GRAU;
  const azFixa = estado.latitude < 0 ? 0 : 180;
  const h = direcaoSolar(azFixa, 0);
  const nf = new THREE.Vector3(h[0] * Math.sin(inc), Math.cos(inc), h[2] * Math.sin(inc));
  estado.energiaFixa += estado.luxDireta * Math.max(0, nf.dot(s)) * dh / 1000;
}

function amostrar() {
  estado.amostras.push({ t: uno.segundos, h: estado.servoH, v: estado.servoV, e: anguloErro() });
  if (estado.amostras.length > 600) estado.amostras.shift();
}

function atualizarCenaAuxiliar() {
  scene.updateMatrixWorld();
  const centro = new THREE.Vector3();
  malhasLdr[0].getWorldPosition(centro);
  const c2 = new THREE.Vector3(); malhasLdr[3].getWorldPosition(c2); centro.add(c2).multiplyScalar(0.5);
  const pos = raioGeo.attributes.position;
  pos.setXYZ(0, sol.position.x, sol.position.y, sol.position.z);
  pos.setXYZ(1, centro.x, centro.y, centro.z);
  pos.needsUpdate = true;
  raio.computeLineDistances();
  raio.visible = estado.sol[1] > 0;
  normalDaPlaca(vN);
  const cPlaca = new THREE.Vector3(...PLACA.centro).sub(PIVO_EL);
  grupoEl.localToWorld(cPlaca);
  setaNormal.position.copy(cPlaca);
  setaNormal.setDirection(vN);
}

// ---------------------------------------------------------------- UI
const fmt = (x, d = 0) => x.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
function fmtHora(h) {
  const hh = Math.floor(h); const mm = Math.floor((h - hh) * 60);
  return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
}
function fmtDia(d) {
  const data = new Date(2026, 0, d);
  return data.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
}
const corpoTab = $('tabLdr').querySelector('tbody');
corpoTab.innerHTML = LDRS.map((l) => `<tr title="${l.nome}"><td>${l.id}</td><td></td><td></td><td></td><td></td></tr>`).join('');

let ultimoUI = 0;
function atualizarUI() {
  const agora = performance.now();
  if (agora - ultimoUI < 100) return;
  ultimoUI = agora;
  const canais = canaisDaFiacao();
  [...corpoTab.rows].forEach((tr, i) => {
    const v = leituras[i].volts;
    tr.cells[1].textContent = uno && uno.gpioDoCanal ? `GPIO ${uno.gpioDoCanal[canais[i]]}` : `A${canais[i]}`;
    tr.cells[2].textContent = fmt(leituras[i].lux);
    // ESP32: divisor em 3,3 V e ADC de 12 bits; Nano: 5 V e 10 bits (mesma proporção do divisor)
    const esp = uno && uno.placa === 'esp32';
    const vref = esp ? 3.3 : 5;
    const maxAdc = esp ? 4095 : 1023;
    tr.cells[3].textContent = fmt((v / 5) * vref, 2);
    tr.cells[4].innerHTML = `${Math.round((v / 5) * maxAdc)}<span class="barra" style="width:${(v / 5) * 50}px"></span>`;
  });
  $('mH').textContent = `${fmt(estado.servoH, 0)}°`;
  $('mV').textContent = `${fmt(estado.servoV, 0)}°`;
  const erro = anguloErro();
  const e = $('mErro');
  e.textContent = estado.sol[1] > 0 ? `${fmt(erro, 1)}°` : 'noite';
  e.className = erro < 10 ? 'bom' : erro > 30 ? 'mau' : '';
  $('mApr').textContent = estado.sol[1] > 0 ? `${fmt(Math.max(0, Math.cos(erro * GRAU)) * 100, 0)} %` : '–';
  $('chipEstado').textContent = estado.rodando ? '● firmware rodando' : '❚❚ pausado';
  $('chipTempo').textContent = `t = ${fmt(uno ? uno.segundos : 0, 1)} s`;
  const emDia = estado.modoSol === 'dia';
  $('boxEnergia').style.opacity = emDia ? 1 : 0.45;
  $('mEtrack').textContent = fmt(estado.energiaTrack, 1);
  $('mEfixa').textContent = fmt(estado.energiaFixa, 1);
  const ganho = estado.energiaFixa > 0.5 ? (estado.energiaTrack / estado.energiaFixa - 1) * 100 : null;
  const g = $('mGanho');
  g.textContent = ganho == null ? '–' : `${ganho >= 0 ? '+' : ''}${fmt(ganho, 0)} %`;
  g.className = ganho == null ? '' : ganho >= 0 ? 'bom' : 'mau';
  if (serialSujo) {
    serialSujo = false;
    const pre = $('serial');
    const noFim = pre.scrollTop + pre.clientHeight >= pre.scrollHeight - 20;
    pre.textContent = estado.linhasSerial.slice(-200).join('\n');
    if (noFim) pre.scrollTop = pre.scrollHeight;
  }
  desenharGrafico();
}

function desenharGrafico() {
  const cv = $('grafico');
  const w = cv.clientWidth; const h = 150;
  if (cv.width !== w * devicePixelRatio) { cv.width = w * devicePixelRatio; cv.height = h * devicePixelRatio; }
  const g = cv.getContext('2d');
  g.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  g.clearRect(0, 0, w, h);
  const css = getComputedStyle(document.documentElement);
  const cores = { h: css.getPropertyValue('--s1'), v: css.getPropertyValue('--s2'), e: css.getPropertyValue('--s3') };
  const a = estado.amostras;
  const pad = { l: 28, r: 6, t: 18, b: 14 };
  g.font = '10px system-ui'; g.fillStyle = css.getPropertyValue('--suave');
  g.strokeStyle = css.getPropertyValue('--borda'); g.lineWidth = 1;
  for (const val of [0, 90, 180]) {
    const y = pad.t + (1 - val / 180) * (h - pad.t - pad.b);
    g.beginPath(); g.moveTo(pad.l, y); g.lineTo(w - pad.r, y); g.stroke();
    g.fillText(`${val}°`, 2, y + 3);
  }
  [['h', 'horizontal'], ['v', 'vertical'], ['e', 'erro de apontamento']].forEach(([k, nome], i) => {
    g.fillStyle = cores[k]; g.fillRect(pad.l + i * 92, 4, 10, 3); g.fillText(nome, pad.l + 14 + i * 92, 9);
  });
  if (a.length < 2) return;
  const t0 = a[0].t; const t1 = a[a.length - 1].t; const span = Math.max(1, t1 - t0);
  for (const k of ['h', 'v', 'e']) {
    g.strokeStyle = cores[k]; g.lineWidth = 1.5; g.beginPath();
    a.forEach((s, i) => {
      const x = pad.l + ((s.t - t0) / span) * (w - pad.l - pad.r);
      const y = pad.t + (1 - Math.min(180, s[k]) / 180) * (h - pad.t - pad.b);
      i ? g.lineTo(x, y) : g.moveTo(x, y);
    });
    g.stroke();
  }
}

// controles
function ligar(id, evento, fn) { $(id).addEventListener(evento, fn); }
function zerarEnergia() { estado.energiaTrack = 0; estado.energiaFixa = 0; }
function sincronizarSaidas() {
  $('outHora').value = fmtHora(estado.hora);
  $('outDia').value = fmtDia(estado.dia);
  $('outAz').value = `${fmt(estado.azManual, 0)}°`;
  $('outEl').value = `${fmt(estado.elManual, 0)}°`;
  $('outLux').value = `${fmt(estado.luxDireta)} lux`;
  $('outDif').value = `${fmt(estado.difusa * 100)} %`;
  $('outVar').value = `±${fmt(estado.variacao * 100)} %`;
  $('outRuido').value = `${fmt(estado.ruidoMv)} mV`;
}
function sortearFatores() {
  const r = rng(42);
  fatoresLdr = LDRS.map(() => 1 + estado.variacao * (2 * r() - 1));
}
document.querySelectorAll('input[name=modoSol]').forEach((el) => el.addEventListener('change', () => {
  definirModo(el.value);
}));
function definirModo(modo) {
  estado.modoSol = modo;
  document.querySelector(`input[name=modoSol][value=${modo}]`).checked = true;
  $('grupoDia').hidden = modo !== 'dia';
  $('grupoManual').hidden = modo !== 'manual';
  zerarEnergia();
}
ligar('inHora', 'input', (e) => { estado.hora = +e.target.value; sincronizarSaidas(); });
ligar('inDia', 'input', (e) => { estado.dia = +e.target.value; zerarEnergia(); sincronizarSaidas(); });
ligar('inLat', 'change', (e) => { estado.latitude = +e.target.value; zerarEnergia(); });
ligar('inVelDia', 'change', (e) => { estado.horasPorSegundo = +e.target.value; });
ligar('inAz', 'input', (e) => { estado.azManual = +e.target.value; sincronizarSaidas(); });
ligar('inEl', 'input', (e) => { estado.elManual = +e.target.value; sincronizarSaidas(); });
ligar('inLux', 'input', (e) => { estado.luxDireta = Math.round(10 ** +e.target.value); zerarEnergia(); sincronizarSaidas(); });
ligar('inDif', 'input', (e) => { estado.difusa = +e.target.value / 100; sincronizarSaidas(); });
ligar('inFiacao', 'change', (e) => { estado.fiacao = e.target.value; });
ligar('inInvH', 'change', (e) => { estado.invH = e.target.checked; });
ligar('inInvV', 'change', (e) => { estado.invV = e.target.checked; });
ligar('inVar', 'input', (e) => { estado.variacao = +e.target.value / 100; sortearFatores(); sincronizarSaidas(); });
ligar('inRuido', 'input', (e) => { estado.ruidoMv = +e.target.value; sincronizarSaidas(); });
ligar('inVelSim', 'change', (e) => { estado.velSim = +e.target.value; });
ligar('btnPausa', 'click', () => {
  estado.rodando = !estado.rodando;
  $('btnPausa').textContent = estado.rodando ? '⏸ Pausar' : '▶ Continuar';
});
ligar('btnReset', 'click', async () => { await iniciarFirmware(); zerarEnergia(); });
ligar('btnLimpar', 'click', () => { estado.linhasSerial = []; serialSujo = true; });
ligar('btnLog', 'click', () => {
  const blob = new Blob([estado.linhasSerial.join('\n') + '\n'], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'monitor-serial.txt';
  a.click();
  URL.revokeObjectURL(a.href);
});
ligar('inHex', 'change', async (e) => {
  const f = e.target.files[0];
  if (!f) return;
  try {
    iniciarArduino(await f.text());
    zerarEnergia();
    $('notaHex').innerHTML = `Rodando: <code>${f.name}</code>`;
  } catch (err) {
    alert(`Não foi possível carregar o .hex: ${err.message}`);
  }
});

// arrastar o sol
const ponteiro = new THREE.Vector2();
let arrastandoSol = false;
function raioDoPonteiro(ev) {
  const r = renderer.domElement.getBoundingClientRect();
  ponteiro.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(ponteiro, camera);
  raycaster.far = Infinity;
  return raycaster.ray;
}
renderer.domElement.addEventListener('pointerdown', (ev) => {
  raioDoPonteiro(ev);
  if (raycaster.intersectObject(sol, true).length) {
    arrastandoSol = true;
    controls.enabled = false;
    renderer.domElement.setPointerCapture(ev.pointerId);
    if (estado.modoSol !== 'manual') definirModo('manual');
  }
});
renderer.domElement.addEventListener('pointermove', (ev) => {
  const ray = raioDoPonteiro(ev);
  renderer.domElement.style.cursor = arrastandoSol || raycaster.intersectObject(sol, true).length ? 'grab' : '';
  if (!arrastandoSol) return;
  const centro = new THREE.Vector3(0, 150, 0);
  const p = new THREE.Vector3();
  if (!ray.intersectSphere(new THREE.Sphere(centro, DIST_SOL), p)) return;
  const d = p.sub(centro).normalize();
  const { azimute, elevacao } = azElDeDirecao([d.x, d.y, d.z]);
  estado.azManual = Math.round(azimute * 2) / 2;
  estado.elManual = Math.max(-5, Math.round(elevacao * 2) / 2);
  $('inAz').value = estado.azManual;
  $('inEl').value = estado.elManual;
  sincronizarSaidas();
});
renderer.domElement.addEventListener('pointerup', () => {
  arrastandoSol = false;
  controls.enabled = true;
});

function redimensionar() {
  const w = cenaEl.clientWidth; const h = cenaEl.clientHeight;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(redimensionar).observe(cenaEl);

// ---------------------------------------------------------------- início
(async function iniciar() {
  sortearFatores();
  sincronizarSaidas();
  aplicarPose();
  redimensionar();
  try {
    // ?firmware=nano carrega a versão anterior (Arduino Nano, .hex emulado); padrão: firmware.json
    const pedido = new URLSearchParams(location.search).get('firmware');
    const [cfg] = await Promise.all([
      pedido === 'nano' ? { placa: 'nano', arquivo: 'nano_versao_anterior.hex' }
        : fetch('firmware/firmware.json', { cache: 'no-store' }).then((r) => {
          if (!r.ok) throw new Error('firmware/firmware.json não encontrado — rode simulator/build-firmware.sh');
          return r.json();
        }),
      carregarPecas(),
    ]);
    if (cfg.placa === 'esp32') {
      firmwares.esp32 = { tipo: 'esp32', url: `../firmware/${cfg.arquivo}`, cfg };
      await iniciarFirmware(firmwares.esp32);
      $('notaHex').innerHTML = `Rodando: <b>ESP32</b> — o <code>main.c</code> compilado para WebAssembly com o núcleo ESP32 simulado (<code>firmware/${cfg.arquivo}</code>).`;
      $('inFiacao').disabled = true;
    } else {
      const hex = await fetch(`firmware/${cfg.arquivo}`, { cache: 'no-store' }).then((r) => r.text());
      iniciarArduino(hex);
      $('notaHex').innerHTML = `Rodando: <b>Arduino Nano</b> emulado (<code>firmware/${cfg.arquivo}</code>).`;
    }
  } catch (err) {
    const box = $('erroCarga');
    box.hidden = false;
    box.innerHTML = `<b>Erro ao iniciar:</b> ${err.message}<br><br>Abra pelo servidor local, a partir da raiz do repositório:<br>
      <code>python3 -m http.server 8000</code> e acesse <code>http://localhost:8000/simulator/</code>`;
    console.error(err);
  }
  requestAnimationFrame(quadro);
})();
