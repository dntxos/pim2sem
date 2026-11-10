# CLAUDE.md

Rastreador solar de dois eixos — PIM (Projeto Integrado Multidisciplinar) da UNIP.
**ESP32** + 4 LDRs + 2 servos **MG996R** movem um painel solar de 10 W para seguir a luz; o ESP32
cria a rede Wi-Fi `SOLAR_TOWER` (senha `torre1234`) com controle pelo celular em `http://192.168.4.1`.
Alimentação: bateria 12 V + 2 conversores XL4015. O projeto começou com Arduino **Nano** (migrou na
etapa de testes físicos); o diagrama do Tinkercad (UNO) é da fase inicial.
Lista de materiais real: `docs/specs/02-hardware.md` — não citar SG90, UNO ou fonte USB como hardware do projeto.

## Contexto do PIM II

O tema oficial do semestre é uma **torre solar que carrega celulares por 2 saídas USB** (bateria
12 V + controlador de carga + PCI); este rastreador é o subsistema de rastreamento. Relatório:
skill `relatorio-pim`.

## Idioma

Responder, comentar código e escrever documentação **em português do Brasil**. Nomes de variáveis
seguem o padrão já usado no código (português, `camelCase`; constantes em `MAIUSCULAS`).

## Estrutura

```
main.c                  Firmware ESP32 (sketch Arduino em C++, apesar da extensão .c)
docs/diagrama_tinkercad.png   Circuito de referência (Tinkercad)
docs/specs/             Especificações — leia antes de mudar comportamento
3d_material/amf/        Montagem 3D completa (.AMF, ~11 MB)
3d_material/stl/        Peças individuais para impressão (exportadas nas coordenadas da montagem)
simulator/              Simulador 3D: o mesmo main.c compilado p/ WebAssembly (núcleo ESP32 simulado) + STLs
simulator/esp32/nucleo/ Núcleo ESP32 simulado (Arduino.h, WiFi.h, WebServer.h, ESP32Servo.h)
docs/imagens_videos_testes_fisicos/  Fotos e vídeos dos testes físicos (fonte do cap. de testes)
tools/render/           Renders fotorrealistas da montagem no Blender (figuras do relatório)
docs/relatorio/         Relatório do PIM II (.docx) e figuras
.claude/skills/         Skills do projeto
```

Specs: [visão geral](docs/specs/01-visao-geral.md) · [hardware](docs/specs/02-hardware.md) ·
[firmware](docs/specs/03-firmware.md) · [mecânica](docs/specs/04-mecanica.md) ·
[testes](docs/specs/05-testes.md) · [problemas conhecidos](docs/specs/06-problemas-conhecidos.md)

## Pontos de atenção (não óbvios)

- **ESP32:** LDRs em GPIO 34/35/32/33 (ADC1 — o ADC2 não funciona com Wi-Fi), servos em 18/19.
  Divisores dos LDRs em **3V3** (entradas não toleram 5 V). ADC de 12 bits (0–4095).
- **Pendências no `main.c` do ESP32 (achadas no simulador):** P10 regrediu (falta `sentidoHorizontal`)
  e P14 (`TOLERANCIA = 40` não foi escalada para 12 bits). Não alterar o `main.c` sem o usuário pedir.
- **Convenção do sensor:** leitura maior = mais luz (LDR no lado do 5 V do divisor). Inverter o
  divisor inverte o sentido dos eixos.
- **Sinais dos eixos** (`+=`/`-=`) dependem da montagem mecânica; o eixo vertical é propositalmente
  invertido em relação ao horizontal.
- **Limites 20°–160°** protegem a estrutura impressa — não ampliar sem checar a mecânica.
- **Ritmo do laço:** no ESP32 o rastreamento roda a cada 100 ms por `millis()` (`INTERVALO_MOVIMENTO`).
- **O painel sombreia os LDRs (P13):** no CAD o suporte dos LDRs fica abaixo do plano do painel;
  em simulação isso faz o rastreador fugir do Sol em junho. Variante `simulator/?elevacaoLdr=25`.
- **Relatório:** gerado por script (`tools/relatorio/gerar_relatorio.py` → `exportar_pdf.sh`);
  números vêm de `docs/relatorio/dados/` — não digitar resultados à mão.
- O AMF guarda as posições das peças em **metros** e a geometria em mm; prefira os STLs, que já
  estão nas coordenadas da montagem.
- O simulador só suporta as APIs do núcleo simulado; se o `main.c` passar a usar outra função do
  Arduino/ESP32, implemente-a em `simulator/esp32/nucleo/` (senão `build-firmware.sh` falha).
- Arquivos `.AMF`/`.STL` são binários/grandes: não ler nem editar; só referenciar.

## Build / verificação

Não há testes automatizados. Para checar se compila (requer `arduino-cli`, ver skill
`firmware-arduino`):

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 <pasta-do-sketch>   # requer núcleo esp32 e lib ESP32Servo
```

Como o arquivo é `main.c`, para compilar é preciso copiá-lo para `<pasta>/<pasta>.ino` (ver P2 em
problemas conhecidos).

## Ao alterar o firmware

1. Manter a telemetria serial (o usuário usa para calibrar e para o relatório).
2. Atualizar `docs/specs/03-firmware.md` se mudar parâmetros, algoritmo ou formato serial.
3. Atualizar `docs/specs/02-hardware.md` se mudar pinos.
4. Compilar antes de dizer que está pronto.
5. Validar o comportamento no simulador (skill `simulador-3d`): `./simulator/build-firmware.sh`
   recompila o `main.c` para WebAssembly (`simulator/firmware/esp32.mjs`, requer `em++`); o arquivo
   versionado precisa corresponder ao `main.c` commitado.
