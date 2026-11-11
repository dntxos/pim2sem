# 03 — Firmware

Arquivo: `main.c` — sketch Arduino em C++ para **ESP32** (núcleo `esp32:esp32`, bibliotecas
`WiFi`, `WebServer` e `ESP32Servo`). A versão anterior, para Arduino Nano, está no histórico do Git
(último commit com o Nano: `e3ec9ed`) e compilada em `simulator/firmware/nano_versao_anterior.hex`.

## Funcionalidades

1. **Rastreamento automático** pelos 4 LDRs (mesma lógica de médias por lado da versão Nano).
2. **Modo manual** pelo celular: o ESP32 cria a rede Wi-Fi `SOLAR_TOWER` (senha `torre1234`) e
   serve uma página em `http://192.168.4.1` com botões ◀ ▶ ▲ ▼, posição inicial e leituras.
3. **Repouso noturno:** média dos LDRs < 500 por 120 s → painel vai para a posição inicial
   (H = 20°, V = 90°) e para; média > 700 por 30 s → volta a rastrear (resolve o P7).

## Parâmetros

| Constante | Valor | Significado |
|-----------|-------|-------------|
| `TOLERANCIA` | 160 | Zona morta em unidades do ADC de 12 bits (era 40 no Nano, 10 bits — P14) |
| `PASSO_AUTO` / `PASSO_MANUAL` | 2° / 5° | Passo por ciclo automático / por toque no celular |
| `INTERVALO_MOVIMENTO` | 100 ms | Período do rastreamento (não depende mais da serial) |
| `LIMITE_*` | 20°–160° | Limites dos dois eixos |
| `INICIO_H` / `INICIO_V` | 20° / 90° | Posição inicial / de repouso noturno |
| `LIMITE_NOITE` / `LIMITE_DIA` | 500 / 700 | Média dos LDRs (0–4095) para noite / dia (histerese) |
| `TEMPO_NOITE` / `TEMPO_DIA` | 120 s / 30 s | Tempo contínuo para confirmar noite / dia |

## API web (usada pela página do celular)

| Rota | Função |
|------|--------|
| `GET /` | Página "SOLAR SMART TOWER" |
| `GET /estado` | `{"h":…, "v":…, "luz":…, "modo":"AUTO"|"MANUAL", "estado":"ATIVO"|"NOITE - REPOUSO"}` |
| `GET /modo?valor=auto|manual` | Troca o modo |
| `GET /mover?eixo=h|v&direcao=±1` | Move 5° (só em modo manual; senão HTTP 409) |
| `GET /inicio` | Posição inicial (só em modo manual) |

## Correções aplicadas após os testes físicos (11/11/2026)

O `main.c` usado nos testes físicos tinha duas falhas, encontradas no simulador (mesmo código,
compilado para WebAssembly). Ambas foram corrigidas; a versão dos testes físicos continua disponível
no simulador como variante `esp32:esp32_testes_fisicos`.

| Falha | Antes (testes físicos) | Depois (`main.c` atual) |
|-------|------------------------|-------------------------|
| **P10** — faltava `sentidoHorizontal` | Sol a SE/SO: erro 54°/59°, servo H travado no limite | 18°/17° |
| **P14** — `TOLERANCIA = 40` em 12 bits | 21/jun: painel foge do Sol (−100% vs. placa fixa) | +35% (dez: +49%) |

Repouso noturno e interface web conferidos após a correção. **Validação física: pendente.**
Dados: `docs/relatorio/dados/esp32_corrigido_vs_testes.json`.

## Build

- Arduino IDE: placa **ESP32 Dev Module**, biblioteca **ESP32Servo**. Compilado: 949 523 bytes
  (72% da flash), 47 916 bytes de RAM (14%).
- `arduino-cli compile --fqbn esp32:esp32:esp32 <pasta-do-sketch>` (ver skill `firmware-arduino`).
- Simulador: `./simulator/build-firmware.sh` compila o **mesmo `main.c`** para WebAssembly com o
  núcleo ESP32 simulado (`simulator/esp32/nucleo/`) — ver [simulator/README.md](../../simulator/README.md).
