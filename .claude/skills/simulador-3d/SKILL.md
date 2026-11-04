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
s.sondar(90, 90);                          // servos em 90/90; retorna lux de cada LDR
for (let i = 0; i < 5; i++) { s.avancar(1); console.log(s.estado.servoH, s.estado.servoV, s.erro()); }
```

`avancar` roda ~4× o tempo real; mantenha cada chamada abaixo de ~30 s simulados (limite de
tempo das ferramentas). `s.estado.linhasSerial` tem a saída serial do firmware.

## Cenários de regressão

| Cenário | Esperado com o firmware atual |
|---------|-------------------------------|
| Sol N, el 50°, início 90/90 | converge para V ≈ 118–130, erro ≈ 12° (zona morta + saturação, P11) |
| Dia 172, 9h e 14h, lat −23,55 | erro final < 20° |
| Sol NE el 30°, início 90/60 | **falha**: H vai a 160°, erro ~75° (P10) — deve passar após corrigir P10 |
| Fiação "diagrama" (A0–A3) | erro cresce (P1) |

Se uma correção de firmware mudar esses resultados, atualize esta tabela e
`docs/specs/06-problemas-conhecidos.md`.

## Ao mexer no simulador

- Convenção da cena: Y para cima, mm, Norte = −X, Leste = −Z. Pose exportada da placa: 56,252°.
- Bibliotecas ficam em `simulator/vendor/` (sem CDN, funciona offline); não atualize versões sem
  necessidade.
- Verifique no navegador: sem erros no console, `sim.perf` com emulação + sensores + render < 16 ms
  por quadro.
