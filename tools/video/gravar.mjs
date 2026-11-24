// Grava o vídeo de demonstração da IHM: abre o simulador no Chrome (headless) via DevTools Protocol,
// injeta roteiro_ihm.js e captura os quadros com Page.startScreencast; o ffmpeg monta o MP4.
// Sem dependências npm (Node ≥ 22 tem WebSocket nativo).
//
// Usa a variante com o suporte dos LDRs 25 mm acima do painel (correção sugerida para o P13).
// Uso: (servidor do simulador em http://127.0.0.1:8000 — ver .claude/launch.json)
//   node tools/video/gravar.mjs [saida.mp4]
import { spawn, execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = dirname(fileURLToPath(import.meta.url));
const SAIDA = process.argv[2] ?? join(AQUI, '../../docs/video/demo_ihm.mp4');
const URL_SIM = process.env.URL_SIM ?? 'http://127.0.0.1:8000/simulator/?elevacaoLdr=25';
const CHROME = process.env.CHROME ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const L = 1920, A = 1080, PORTA = 9339, FPS = 30;

const tmp = mkdtempSync(join(tmpdir(), 'demo-ihm-'));
const chrome = spawn(CHROME, [
  '--headless=new', `--remote-debugging-port=${PORTA}`, `--user-data-dir=${join(tmp, 'perfil')}`,
  `--window-size=${L},${A}`, '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
  '--enable-gpu', '--use-angle=metal', '--ignore-gpu-blocklist', 'about:blank',
], { stdio: 'ignore' });

const espera = (ms) => new Promise((r) => setTimeout(r, ms));
let alvo;
for (let i = 0; i < 50 && !alvo; i++) {
  await espera(200);
  try { alvo = (await (await fetch(`http://127.0.0.1:${PORTA}/json/list`)).json()).find((t) => t.type === 'page'); } catch {}
}
if (!alvo) throw new Error('Chrome não respondeu');

const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let id = 0; const pend = new Map(); const quadros = [];
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); return; }
  if (m.method === 'Page.screencastFrame') {
    const { data, metadata, sessionId } = m.params;
    quadros.push({ t: metadata.timestamp, data });
    enviar('Page.screencastFrameAck', { sessionId });
  }
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') console.error('[página]', m.params.args.map((a) => a.value).join(' '));
});
function enviar(method, params = {}) {
  return new Promise((r) => { const n = ++id; pend.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });
}

await enviar('Page.enable'); await enviar('Runtime.enable');
await enviar('Emulation.setDeviceMetricsOverride', { width: L, height: A, deviceScaleFactor: 1, mobile: false });
await enviar('Page.navigate', { url: URL_SIM });
await espera(6000); // módulos, STLs e WebAssembly
const pronto = await enviar('Runtime.evaluate', { expression: 'typeof sim !== "undefined" && !!sim.estado', returnByValue: true });
if (!pronto.result?.result?.value) throw new Error('simulador não carregou');

await enviar('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: L, maxHeight: A, everyNthFrame: 1 });
const r = await enviar('Runtime.evaluate', { expression: readFileSync(join(AQUI, 'roteiro_ihm.js'), 'utf8'), awaitPromise: true, returnByValue: true });
await enviar('Page.stopScreencast');
if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
ws.close(); chrome.kill();

// quadros com duração variável -> vídeo a FPS constante
const pasta = join(tmp, 'q');
execFileSync('mkdir', ['-p', pasta]);
let lista = 'ffconcat version 1.0\n';
quadros.forEach((q, i) => {
  const f = join(pasta, `${String(i).padStart(6, '0')}.jpg`);
  writeFileSync(f, Buffer.from(q.data, 'base64'));
  const dur = i + 1 < quadros.length ? quadros[i + 1].t - q.t : 1 / FPS;
  lista += `file '${f}'\nduration ${Math.max(dur, 0.001).toFixed(4)}\n`;
});
lista += `file '${join(pasta, `${String(quadros.length - 1).padStart(6, '0')}.jpg`)}'\n`;
writeFileSync(join(tmp, 'lista.txt'), lista);
execFileSync('mkdir', ['-p', dirname(SAIDA)]);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', join(tmp, 'lista.txt'),
  '-vf', `fps=${FPS},scale=${L}:${A}:flags=lanczos,format=yuv420p`, '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
  '-movflags', '+faststart', SAIDA], { stdio: 'inherit' });
const dur = quadros.at(-1).t - quadros[0].t;
console.log(`OK ${SAIDA} — ${quadros.length} quadros capturados em ${dur.toFixed(1)} s (~${(quadros.length / dur).toFixed(0)} fps)`);
rmSync(tmp, { recursive: true, force: true });
