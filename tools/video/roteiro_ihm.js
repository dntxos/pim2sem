// Roteiro do vídeo de demonstração da IHM. Roda DENTRO da página do simulador
// (injetado por gravar.mjs). Devolve uma Promise que termina quando o vídeo acaba.
(async () => {
  const espera = (ms) => new Promise((r) => setTimeout(r, ms));
  const $ = (i) => document.getElementById(i);

  // ---------- modo demonstração: só a cena 3D e o celular, grandes ----------
  const css = document.createElement('style');
  css.textContent = `
    .app{grid-template-columns:1fr 500px!important}
    .painel{overflow:hidden!important;padding:18px 34px!important;background:#e9edf3!important;display:flex;align-items:center;justify-content:center}
    .painel>*:not(#boxCelular){display:none!important}
    #boxCelular>summary,#boxCelular>p{display:none!important}
    #boxCelular{width:100%}
    .celular{height:calc(100vh - 60px)!important;width:100%!important;border-width:12px!important;border-radius:44px!important;box-shadow:0 30px 60px rgba(11,42,91,.35)}
    .overlay.topo{display:none!important}
    #leg{position:absolute;left:48px;bottom:48px;max-width:70%;color:#fff;font:600 34px system-ui,-apple-system,sans-serif;
      text-shadow:0 2px 12px rgba(0,0,0,.45);transition:opacity .5s, transform .5s;opacity:0;transform:translateY(12px)}
    #leg small{display:block;font-weight:400;font-size:22px;opacity:.92;margin-top:6px}
    #leg.on{opacity:1;transform:none}
    #leg:before{content:"";display:block;width:64px;height:5px;background:#f5b800;border-radius:3px;margin-bottom:14px}
    #capa{position:fixed;inset:0;z-index:50;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;
      background:linear-gradient(135deg,#0b2a5b,#16407f);color:#fff;font-family:system-ui,-apple-system,sans-serif;transition:opacity .8s}
    #capa h1{font-size:76px;font-weight:800;letter-spacing:-1px}
    #capa p{font-size:28px;opacity:.85}
    #capa .barra{width:120px;height:7px;border-radius:4px;background:#f5b800;margin:6px 0 10px}
    #capa svg{margin-bottom:18px}`;
  document.head.appendChild(css);
  window.dispatchEvent(new Event('resize'));

  const capa = document.createElement('div');
  capa.id = 'capa';
  const logo = `<svg width="110" height="110" viewBox="0 0 46 46"><rect width="46" height="46" rx="10" fill="#fff"/>
    <text x="23" y="27" text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="15" fill="#0b2a5b" letter-spacing="-.5">UNIP</text>
    <rect x="9" y="32" width="28" height="4" rx="2" fill="#f5b800"/></svg>`;
  const mostrarCapa = (titulo, sub, sub2) => {
    capa.innerHTML = `${logo}<h1>${titulo}</h1><div class="barra"></div><p>${sub}</p><p style="font-size:22px;opacity:.7">${sub2}</p>`;
    capa.style.opacity = 1;
    if (!capa.parentNode) document.body.appendChild(capa);
  };
  const leg = document.createElement('div');
  leg.id = 'leg';
  $('cena').appendChild(leg);
  const legenda = async (t, sub = '') => {
    leg.classList.remove('on'); await espera(350);
    leg.innerHTML = t + (sub ? `<small>${sub}</small>` : '');
    leg.classList.add('on');
  };

  // ---------- capa ----------
  mostrarCapa('Solar Smart Tower', 'Rastreador solar de dois eixos · ESP32 · IHM pelo celular',
    'Prévia — simulação 3D rodando o firmware real (main.c)');

  // prepara a cena por trás da capa
  const est = sim.estado;
  est.modoSol = 'dia'; est.dia = 172; est.hora = 8.5; est.horasPorSegundo = 0;
  const { camera, controls } = sim.cena;
  camera.position.set(-120, 390, 730); controls.target.set(40, 165, 40); controls.update();
  await espera(3500);
  await sim.reiniciar('esp32'); // RESET ao sair da capa: o vídeo mostra o painel encontrando o sol

  // celular (a página servida pelo main.c)
  const fr = $('telaCelular');
  const doc = () => fr.contentDocument;
  const toque = (el) => {
    const d = doc(), r = el.getBoundingClientRect();
    const c = d.createElement('div');
    c.style.cssText = `position:fixed;z-index:99;pointer-events:none;left:${r.left + r.width / 2 - 26}px;top:${r.top + r.height / 2 - 26}px;
      width:52px;height:52px;border-radius:50%;background:rgba(245,184,0,.45);border:3px solid rgba(245,184,0,.95);transition:transform .5s, opacity .5s`;
    d.body.appendChild(c);
    return () => { c.style.transform = 'scale(1.6)'; c.style.opacity = 0; setTimeout(() => c.remove(), 600); };
  };
  const tocar = async (el) => { const fim = toque(el); el.click(); await espera(250); fim(); };
  const segurar = async (el, ms) => {
    const fim = toque(el);
    el.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
    await espera(ms);
    el.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
    fim();
  };
  const rolarAte = (sel, margem = 12) => {
    const d = doc(), el = d.querySelector(sel);
    d.scrollingElement.scrollTo({ top: el.offsetTop - margem, behavior: 'smooth' });
  };
  const rolarTopo = () => doc().scrollingElement.scrollTo({ top: 0, behavior: 'smooth' });

  capa.style.opacity = 0; await espera(800); capa.remove();

  // ---------- 1. automático ----------
  est.horasPorSegundo = 0.32;
  await legenda('Modo automático: o painel segue o sol', 'Quatro sensores de luz (LDR) comandam os dois servos');
  await espera(5000);
  rolarAte('.ldrs', 70);
  await legenda('Leitura de cada sensor em tempo real', 'E a diferença de luz entre os lados, com a zona morta do controle');
  await espera(6500);
  rolarAte('.medidores', 60);
  await legenda('Posição dos servos e histórico de luz', 'Ângulos horizontal e de inclinação · gráfico dos últimos 60 s');
  await espera(4500);
  rolarAte('#graf', 70);
  await espera(4000);

  // ---------- 2. manual ----------
  est.horasPorSegundo = 0;
  rolarTopo();
  await legenda('Modo manual: controle pelo celular', 'Rede Wi-Fi da própria torre — sem internet');
  await espera(1600);
  await tocar(doc().getElementById('bMan'));
  await espera(1400);
  rolarAte('#dpad', 90);
  await espera(1400);
  const seta = (e, d) => doc().querySelector(`#dpad [data-e="${e}"][data-d="${d}"]`);
  await legenda('Toque move 5°, segurar repete', 'Setas para girar a base e inclinar o painel');
  await segurar(seta('h', 1), 1900);
  await espera(500);
  await segurar(seta('v', -1), 1500);
  await espera(500);
  await tocar(seta('h', -1)); await espera(450);
  await tocar(seta('h', -1)); await espera(900);
  await legenda('Retorno à posição inicial', 'Mesma posição usada no repouso noturno');
  await tocar(doc().getElementById('bCasa'));
  await espera(3200);

  // ---------- 3. volta ao automático ----------
  rolarTopo();
  await legenda('De volta ao automático', 'O rastreador reencontra o sol em poucos segundos');
  await espera(1200);
  await tocar(doc().getElementById('bAuto'));
  est.horasPorSegundo = 0.1; // sol devagar: não chega ao fim da tarde (limites mecânicos)
  await espera(8500);

  // ---------- fim ----------
  leg.classList.remove('on');
  mostrarCapa('Solar Smart Tower', 'Rede Wi-Fi SOLAR_TOWER · http://192.168.4.1',
    'UNIP · PIM II · Automação Industrial');
  capa.style.opacity = 0; await espera(50); capa.style.opacity = 1;
  await espera(3500);
  return 'ok';
})();
