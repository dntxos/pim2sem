// Roteiro do vídeo "funções do simulador". Roda DENTRO da página do simulador (injetado por gravar.mjs).
// Mostra: cena 3D, trajetória do dia e dias do ano, sol manual, leituras/energia, teste de falha
// (servo invertido), celular, monitor serial e a simulação do ano inteiro (trecho acelerado).
(async () => {
  const espera = (ms) => new Promise((r) => setTimeout(r, ms));
  const $ = (i) => document.getElementById(i);
  const acelerar = (fator) => window.__marcas.push({ t: Date.now() / 1000, fator });

  // ---------- estilo do vídeo ----------
  const css = document.createElement('style');
  css.textContent = `
    .app{grid-template-columns:1fr 430px!important}
    .overlay.topo .dica{display:none}
    #leg{position:absolute;left:36px;bottom:36px;max-width:78%;color:#fff;font:600 28px system-ui,-apple-system,sans-serif;
      text-shadow:0 2px 12px rgba(0,0,0,.5);transition:opacity .45s, transform .45s;opacity:0;transform:translateY(10px);pointer-events:none;z-index:5}
    #leg small{display:block;font-weight:400;font-size:18px;opacity:.93;margin-top:6px}
    #leg.on{opacity:1;transform:none}
    #leg:before{content:"";display:block;width:56px;height:5px;background:#f5b800;border-radius:3px;margin-bottom:12px}
    #selo{position:absolute;right:20px;top:16px;background:#0b2a5b;color:#fff;font:700 18px system-ui,sans-serif;padding:6px 12px;border-radius:9px;opacity:0;transition:opacity .3s;z-index:5}
    #selo.on{opacity:1}
    .foco{outline:3px solid #f5b800;outline-offset:3px;border-radius:8px;transition:outline-color .3s}
    .toque{position:fixed;z-index:99;pointer-events:none;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;
      background:rgba(245,184,0,.45);border:3px solid rgba(245,184,0,.95);transition:transform .5s, opacity .5s}
    #capa{position:fixed;inset:0;z-index:50;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;
      background:linear-gradient(135deg,#0b2a5b,#16407f);color:#fff;font-family:system-ui,-apple-system,sans-serif;transition:opacity .8s;text-align:center}
    #capa h1{font-size:64px;font-weight:800;letter-spacing:-1px;margin:0}
    #capa p{font-size:24px;opacity:.85;margin:0}
    #capa .barra{width:110px;height:7px;border-radius:4px;background:#f5b800;margin:6px 0 10px}`;
  document.head.appendChild(css);
  window.dispatchEvent(new Event('resize'));

  const capa = document.createElement('div'); capa.id = 'capa';
  const logo = `<svg width="96" height="96" viewBox="0 0 46 46"><rect width="46" height="46" rx="10" fill="#fff"/>
    <text x="23" y="27" text-anchor="middle" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="15" fill="#0b2a5b" letter-spacing="-.5">UNIP</text>
    <rect x="9" y="32" width="28" height="4" rx="2" fill="#f5b800"/></svg>`;
  const mostrarCapa = (t, a, b) => {
    capa.innerHTML = `${logo}<h1>${t}</h1><div class="barra"></div><p>${a}</p><p style="font-size:19px;opacity:.7">${b}</p>`;
    if (!capa.parentNode) document.body.appendChild(capa);
    capa.style.opacity = 1;
  };
  const leg = document.createElement('div'); leg.id = 'leg'; $('cena').appendChild(leg);
  const selo = document.createElement('div'); selo.id = 'selo'; $('cena').appendChild(selo);
  const legenda = async (t, sub = '') => {
    leg.classList.remove('on'); await espera(300);
    leg.innerHTML = t + (sub ? `<small>${sub}</small>` : ''); leg.classList.add('on');
  };

  const painel = document.querySelector('.painel');
  const secao = (txt) => [...document.querySelectorAll('.painel details')].find((d) => d.querySelector('summary').textContent.includes(txt));
  let focado = null;
  const focar = (el, margem = 10) => {
    if (focado) focado.classList.remove('foco');
    focado = el; if (!el) return;
    el.classList.add('foco');
    const topo = el.getBoundingClientRect().top - painel.getBoundingClientRect().top + painel.scrollTop - margem;
    painel.scrollTo({ top: topo, behavior: 'smooth' });
  };
  const toque = async (el) => {
    const r = el.getBoundingClientRect(); const c = document.createElement('div'); c.className = 'toque';
    c.style.left = `${r.left + r.width / 2}px`; c.style.top = `${r.top + r.height / 2}px`; document.body.appendChild(c);
    await espera(260); c.style.transform = 'scale(1.6)'; c.style.opacity = 0; setTimeout(() => c.remove(), 600);
  };
  const deslizar = async (id, de, ate, ms) => { // move um controle deslizante como um usuário faria
    const el = $(id); const passos = Math.max(1, Math.round(ms / 33));
    for (let i = 0; i <= passos; i++) { el.value = de + ((ate - de) * i) / passos; el.dispatchEvent(new Event('input')); await espera(33); }
  };
  const escolher = (id, valor) => { const el = $(id); el.value = valor; el.dispatchEvent(new Event('change')); };
  const { camera, controls } = sim.cena;
  const orbitar = async (graus, ms) => { // gira a câmera em torno do alvo
    const alvo = controls.target; const p = camera.position.clone().sub(alvo);
    const passos = Math.round(ms / 33);
    for (let i = 1; i <= passos; i++) {
      const a = (graus * Math.PI / 180) * (i / passos);
      camera.position.set(alvo.x + p.x * Math.cos(a) - p.z * Math.sin(a), alvo.y + p.y, alvo.z + p.x * Math.sin(a) + p.z * Math.cos(a));
      await espera(33);
    }
  };

  // ---------- capa ----------
  mostrarCapa('Simulador 3D do rastreador', 'O mesmo main.c do ESP32, compilado para WebAssembly',
    'Peças 3D reais do projeto · luz calculada por raios · interface do celular');
  const est = sim.estado;
  await sim.reiniciar('esp32');
  est.modoSol = 'dia'; est.dia = 172; est.hora = 9; escolher('inVelDia', '0');
  $('inDia').value = 172; $('inDia').dispatchEvent(new Event('input'));
  camera.position.set(-120, 390, 730); controls.target.set(40, 165, 40); controls.update();
  await espera(3800);
  capa.style.opacity = 0; await espera(800); capa.remove();

  // ---------- 1. visão geral ----------
  escolher('inVelDia', '1');
  await legenda('Firmware real rodando sobre o modelo 3D', 'Os servos obedecem ao main.c; os LDRs “enxergam” o sol por raycasting');
  await orbitar(-40, 6500);

  // ---------- 2. trajetória do dia e dias do ano ----------
  focar(secao('Sol'));
  await legenda('Trajetória do sol: hora, dia do ano e latitude', 'Inverno (junho) e verão (dezembro) em São Paulo, −23,5°');
  escolher('inVelDia', '0.2');
  await toque($('inDia'));
  await deslizar('inDia', 172, 355, 2600);
  escolher('inVelDia', '1');
  await espera(4500);

  // ---------- 3. sol manual ----------
  document.querySelector('input[name=modoSol][value=manual]').click();
  await toque(document.querySelector('input[name=modoSol][value=manual]'));
  await legenda('Sol manual: posicione o sol onde quiser', 'O rastreador reage como reagiria a uma lanterna');
  await deslizar('inAz', 45, 140, 2200);
  await deslizar('inEl', 40, 62, 1000);
  await deslizar('inAz', 140, 30, 2600);
  await deslizar('inEl', 62, 50, 800);
  await espera(1200);

  // ---------- 4. leituras e energia ----------
  focar(secao('Leituras'));
  await legenda('Leituras, erro de apontamento e energia', 'Lux, tensão e ADC de cada LDR · comparação com uma placa fixa');
  await espera(5500);

  // ---------- 5. teste de falha ----------
  focar(secao('Montagem'));
  await legenda('Teste de falhas sem queimar nada', 'Servo horizontal invertido: o painel foge da luz (como no teste com lanterna)');
  await espera(900);
  await toque($('inInvH')); $('inInvH').click();
  await espera(5000);
  await legenda('Corrigido: o painel volta a seguir o sol', 'Também dá para inverter o vertical, trocar a fiação, variar LDRs e ruído');
  await toque($('inInvH')); $('inInvH').click();
  await espera(3800);

  // ---------- 6. celular + serial ----------
  document.querySelector('input[name=modoSol][value=dia]').click();
  escolher('inVelDia', '0.2');
  focar($('boxCelular'));
  await legenda('A página do ESP32 dentro do simulador', 'Os botões do celular comandam a torre simulada');
  await espera(5000);
  focar(secao('Monitor serial'));
  await legenda('Monitor serial do firmware', 'Mesmas mensagens que o ESP32 envia pela USB');
  await espera(3000);

  // ---------- 7. ano inteiro ----------
  focar($('boxAno'), 6);
  await legenda('E o ano inteiro?', 'Um clique roda o firmware de janeiro a dezembro');
  await espera(2600);
  await toque($('btnAno'));
  const fim = sim.ano();
  await espera(1500);
  await legenda('365 dias em time-lapse', 'Rastreador × placa fixa × ideal, dia a dia');
  selo.textContent = '⏩ 6× mais rápido'; selo.classList.add('on');
  acelerar(6);
  await fim;
  acelerar(1); selo.classList.remove('on');
  const t = sim.anoTotais();
  const g = Math.round(t.ganho);
  await legenda(`Resultado: ${g >= 0 ? '+' : ''}${g}% de energia sobre a placa fixa no ano`,
    'O gráfico mostra onde o rastreador rende mais (verão) e onde ainda pode melhorar (inverno)');
  await espera(7000);

  // ---------- fim ----------
  leg.classList.remove('on'); focar(null);
  mostrarCapa('Solar Smart Tower', 'Simulador: abrir simulator/index.html · mesmo código do protótipo',
    'UNIP · PIM II · Automação Industrial');
  await espera(3500);
  return 'ok';
})();
