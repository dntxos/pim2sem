// Captura a IHM do celular (página servida pelo main.c) rodando no simulador, em alta resolução,
// para o relatório. Abre o simulador no Chrome headless, deixa o firmware rastrear o sol por ~45 s
// (para o gráfico ter histórico) e fotografa a página inteira do celular.
// Saída: docs/relatorio/figuras/ihm_captura.png (depois fotos.py monta o painel f_ihm.png).
// Uso (servidor do simulador em 127.0.0.1:8000): node tools/relatorio/capturar_ihm.mjs
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = dirname(fileURLToPath(import.meta.url));
const SAIDA = join(AQUI, '../../docs/relatorio/figuras/ihm_captura.png');
const CHROME = process.env.CHROME ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORTA = 9341, LARG = 390, ESCALA = 3;
const tmp = mkdtempSync(join(tmpdir(), 'ihm-'));
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORTA}`, `--user-data-dir=${join(tmp, 'p')}`,
  '--window-size=1400,2000', '--hide-scrollbars', '--no-first-run', '--use-angle=metal', 'about:blank'], { stdio: 'ignore' });
const espera = (ms) => new Promise((r) => setTimeout(r, ms));
let alvo;
for (let i = 0; i < 50 && !alvo; i++) {
  await espera(200);
  try { alvo = (await (await fetch(`http://127.0.0.1:${PORTA}/json/list`)).json()).find((t) => t.type === 'page'); } catch {}
}
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let id = 0; const pend = new Map();
ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
const enviar = (method, params = {}) => new Promise((r) => { const n = ++id; pend.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });
const avaliar = async (expression) => (await enviar('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })).result?.result?.value;

await enviar('Page.enable');
await enviar('Emulation.setDeviceMetricsOverride', { width: 1400, height: 2000, deviceScaleFactor: ESCALA, mobile: false });
await enviar('Page.navigate', { url: 'http://127.0.0.1:8000/simulator/?elevacaoLdr=25' });
await espera(6000);
await avaliar(`(async () => {
  await sim.reiniciar('esp32');
  const e = sim.estado; e.modoSol = 'dia'; e.dia = 172; e.hora = 9.2; e.horasPorSegundo = 0.05;
  const fr = document.getElementById('telaCelular');
  fr.style.cssText = 'width:${LARG}px;height:1800px;border:0;border-radius:0;margin:0';
  return true; })()`);
await espera(45000);
const caixa = await avaliar(`(() => { const fr = document.getElementById('telaCelular'); const d = fr.contentDocument;
  fr.style.height = d.documentElement.scrollHeight + 'px'; fr.scrollIntoView();
  const r = fr.getBoundingClientRect(); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: d.documentElement.scrollHeight }; })()`);
await espera(1500);
const foto = await enviar('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true,
  clip: { x: caixa.x, y: caixa.y, width: caixa.w, height: caixa.h, scale: 1 } });
writeFileSync(SAIDA, Buffer.from(foto.result.data, 'base64'));
console.log('OK', SAIDA, caixa);
ws.close(); chrome.kill();
await espera(800);
try { rmSync(tmp, { recursive: true, force: true }); } catch {}
