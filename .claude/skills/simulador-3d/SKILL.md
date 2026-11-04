---
name: simulador-3d
description: Rodar, testar e modificar o simulador 3D do rastreador solar (simulator/) — firmware real emulado com avr8js sobre as peças STL em three.js. Use para validar mudanças no main.c sem hardware, reproduzir um comportamento (placa foge do sol, oscila, trava no limite), gerar evidências/gráficos para o relatório, ou alterar a cena, o modelo dos LDRs e a cinemática.
---

# Simulador 3D

Detalhes de arquitetura em `simulator/README.md`. Resumo: `js/arduino.js` (emulador),
`js/montagem.js` (peças, eixos, posição dos LDRs), `js/sensores.js` (lux → volts), `js/sol.js`,
`js/main.js` (cena, física, UI).

## Testar uma mudança no firmware

1. `./simulator/build-firmware.sh` (recompila `main.c` → `simulator/firmware/solar_tracker.hex`).
2. Subir o servidor da **raiz** do repo: configuração `simulador` em `.claude/launch.json`
   (`python3 -m http.server 8000`), abrir `http://localhost:8000/simulator/`.
3. Testar de forma determinística pelo console da página (não dependa da animação: com o painel
   do navegador oculto o `requestAnimationFrame` cai para ~2 fps):

```js
const s = window.sim;
s.estado.rodando = false;                 // pausa o laço animado
s.estado.modoSol = 'manual'; s.estado.azManual = 0; s.estado.elManual = 50;
s.reiniciar();                             // SEMPRE antes de cada cenário: firmware volta a 90/90
for (let i = 0; i < 5; i++) { s.avancar(1); console.log(s.estado.servoH, s.estado.servoV, s.erro()); }
```

O firmware guarda os próprios ângulos internos: `s.sondar(h, v)` só serve para inspecionar a luz
nos LDRs numa pose — ao rodar, o firmware volta para os ângulos dele. Para comparar firmwares,
`s.reiniciar(textoDoHex)` carrega outro `.hex`.

`avancar` roda ~4× o tempo real; mantenha cada chamada abaixo de ~30 s simulados (limite de
tempo das ferramentas). `s.estado.linhasSerial` tem a saída serial do firmware.

## Variantes e diagnóstico

- `?elevacaoLdr=25` na URL eleva o suporte dos LDRs 25 mm (variante de projeto do P13).
- `sim.bloqueios()` → para cada LDR, a peça que bloqueia o raio ao Sol (`-` = livre).
- **Cache:** depois de editar `simulator/js/*.js`, force o recarregamento
  (`await fetch('/simulator/js/main.js',{cache:'reload'})` + `location.reload()`) e confirme que a
  função/variante nova existe antes de confiar no resultado — uma rodada "elevada" já saiu inválida
  por usar o módulo antigo em cache.
- Para extrair séries longas, rodar em blocos < 30 s simulados por chamada; para salvar em disco,
  um pequeno servidor local de POST (ver histórico em `docs/relatorio/dados/`).

## Cenários de regressão

Todos partindo de `s.reiniciar()` (90/90), ~1 000 lux, difusa 10 %:

| Cenário | Esperado com o firmware atual |
|---------|-------------------------------|
| Sol N el 50° / S el 50° (6 s) | V ≈ 118 / 62, erro ≈ 12° (zona morta + saturação, P11) |
| Sol SE el 40° / SO el 35° (6 s) | erro ≈ 17–18° (falhava antes da correção do P10: 53–58°) |
| Sol NE el 30° / NO el 35° (6 s) | erro ≈ 17–18° |
| Sol L el 55° / O el 50° (10 s) | erro ≈ 18°, sem oscilar quando V cruza 90° |
| Dia 355, 7h, lat −23,55 (16 s) | erro ≈ 16° |
| Fiação "diagrama" (A0–A3) | erro cresce (P1, ainda não corrigido) |
| Dia 172 completo (6h30→17h30, 0,5 h/s) — CAD | **falha** (P13): energia ≈ 1,8 u.r. × placa fixa 6,9 |
| Dia 172 completo — `?elevacaoLdr=25` | ≈ 9,2 u.r. (+33%) |

Se uma correção de firmware mudar esses resultados, atualize esta tabela e
`docs/specs/06-problemas-conhecidos.md`.

## Ao mexer no simulador

- Convenção da cena: Y para cima, mm, Norte = −X, Leste = −Z. Pose exportada da placa: 56,252°.
- Bibliotecas ficam em `simulator/vendor/` (sem CDN, funciona offline); não atualize versões sem
  necessidade.
- Verifique no navegador: sem erros no console, `sim.perf` com emulação + sensores + render < 16 ms
  por quadro.
