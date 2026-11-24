# 03 — Firmware

Arquivo: `main.c` — sketch Arduino em C++ para **ESP32** (núcleo `esp32:esp32`, bibliotecas
`WiFi`, `WebServer` e `ESP32Servo`). A versão anterior, para Arduino Nano, está no histórico do Git
(último commit com o Nano: `e3ec9ed`) e compilada em `simulator/firmware/nano_versao_anterior.hex`.

## Funcionalidades

1. **Rastreamento automático** pelos 4 LDRs (mesma lógica de médias por lado da versão Nano).
2. **Modo manual** pelo celular: o ESP32 cria a rede Wi-Fi `SOLAR_TOWER` (senha `torre1234`) e
   serve em `http://192.168.4.1` a **IHM** (ver abaixo), com modo, controle manual e leituras.
3. **Repouso noturno:** média dos LDRs < 500 por 120 s → painel vai para a posição inicial
   (H = 90°, V = 90°) e para; média > 700 por 30 s → volta a rastrear (resolve o P7).

## Parâmetros

| Constante | Valor | Significado |
|-----------|-------|-------------|
| `TOLERANCIA` | 160 | Zona morta em unidades do ADC de 12 bits (era 40 no Nano, 10 bits — P14) |
| `PASSO_AUTO` / `PASSO_MANUAL` | 2° / 5° | Passo por ciclo automático / por toque no celular |
| `INTERVALO_MOVIMENTO` | 100 ms | Período do rastreamento (não depende mais da serial) |
| `LIMITE_*` | 20°–160° | Limites dos dois eixos |
| `INICIO_H` / `INICIO_V` | 90° / 90° | Posição inicial / de repouso noturno (H era 20° — P15) |
| `LIMITE_NOITE` / `LIMITE_DIA` | 500 / 700 | Média dos LDRs (0–4095) para noite / dia (histerese) |
| `TEMPO_NOITE` / `TEMPO_DIA` | 120 s / 30 s | Tempo contínuo para confirmar noite / dia |

## API web (usada pela página do celular)

| Rota | Função |
|------|--------|
| `GET /` | IHM "Solar Smart Tower" (HTML/CSS/JS embutidos no `main.c`, sem arquivos externos) |
| `GET /estado` | JSON abaixo |
| `GET /modo?valor=auto|manual` | Troca o modo |
| `GET /mover?eixo=h|v&direcao=±1` | Move 5° (só em modo manual; senão HTTP 409) |
| `GET /inicio` | Posição inicial (só em modo manual) |

`/estado` devolve:

| Campo | Conteúdo |
|-------|----------|
| `h`, `v` | Ângulos dos servos (°) |
| `luz` | Média dos 4 LDRs (0–4095) |
| `se`, `sd`, `ie`, `id` | Última leitura de cada LDR (0–4095) |
| `tol`, `limNoite`, `limDia` | `TOLERANCIA`, `LIMITE_NOITE`, `LIMITE_DIA` (para a IHM desenhar zona morta e limites) |
| `periodo` | `DIA`, `ANOITECENDO` (contando para o repouso), `NOITE` ou `AMANHECENDO` (contando para retomar) |
| `faltam` | Segundos até a próxima transição de período (0 se nenhuma em curso) |
| `ligado` | Segundos desde que o ESP32 ligou |
| `modo` | `AUTO` ou `MANUAL` |
| `estado` | `ATIVO` ou `NOITE - REPOUSO` (mantido por compatibilidade) |

## IHM (página do celular)

Página única, leve e sem dependências (o celular fica na rede da torre, sem internet): identidade
UNIP (azul `#0b2a5b` e amarelo `#f5b800`, logotipo em SVG inline), fundo claro para leitura ao sol.
Atualiza `/estado` a cada 1 s.

- **Resumo:** modo, período do dia (com contagem para repouso/retomada), tempo ligado e estado da
  conexão (Online/Offline, tempo de resposta).
- **Sensores:** os 4 LDRs na disposição física (SE/SD/IE/ID) com barras, média, e a **diferença
  esquerda × direita e superior × inferior** com a zona morta (`TOLERANCIA`) desenhada — útil para
  diagnosticar sentido invertido (ex.: o teste com lanterna).
- **Servos:** medidores semicirculares de H e V com a faixa útil 20°–160°.
- **Gráfico:** histórico dos últimos 60 s (4 LDRs + média) com os limites noite/dia.
- **Controle manual:** setas (toque = 5°, segurar repete) e posição inicial; bloqueado com aviso em
  modo automático ou repouso noturno; erros HTTP 409 aparecem como aviso na tela.

## Correções aplicadas após os testes físicos (11/11/2026)

O `main.c` usado nos testes físicos tinha duas falhas, encontradas no simulador (mesmo código,
compilado para WebAssembly). Ambas foram corrigidas; a versão dos testes físicos continua disponível
no simulador como variante `esp32:esp32_testes_fisicos`.

| Falha | Antes (testes físicos) | Depois (`main.c` atual) |
|-------|------------------------|-------------------------|
| **P10** — faltava `sentidoHorizontal` | Sol a SE/SO: erro 54°/59°, servo H travado no limite | 18°/17° |
| **P14** — `TOLERANCIA = 40` em 12 bits | 21/jun: painel foge do Sol (−100% vs. placa fixa) | +35% (dez: +49%) |
| **P15** — repouso noturno em H = 20° (24/11/2026) | Inverno: acorda preso no limite até ~meio-dia; ano: +34,5%, erro médio 27,7° | `INICIO_H = 90`: ano +47,1%, erro médio 16,9° |

Repouso noturno e interface web conferidos após a correção. **Validação física: pendente.**

`INICIO_H = 90` (P15) também muda o botão **Posição inicial** da IHM: agora leva o painel ao centro
(90°/90°). Comparação do ano inteiro antes/depois: `docs/relatorio/dados/ano_p15.json` e capturas
`docs/imagens_videos_testes_fisicos/ganho_anual_{antes,depois}_da_correcao_p15.jpeg` (simulação).
Dados: `docs/relatorio/dados/esp32_corrigido_vs_testes.json`.

## Build

- Arduino IDE: placa **ESP32 Dev Module**, biblioteca **ESP32Servo**. Compilado: 949 523 bytes
  (72% da flash), 47 916 bytes de RAM (14%).
- `arduino-cli compile --fqbn esp32:esp32:esp32 <pasta-do-sketch>` (ver skill `firmware-arduino`).
- Simulador: `./simulator/build-firmware.sh` compila o **mesmo `main.c`** para WebAssembly com o
  núcleo ESP32 simulado (`simulator/esp32/nucleo/`) — ver [simulator/README.md](../../simulator/README.md).
