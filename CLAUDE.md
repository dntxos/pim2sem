# CLAUDE.md

Rastreador solar de dois eixos — PIM (Projeto Integrado Multidisciplinar) da UNIP.
Arduino **Nano** + 4 LDRs + 2 servos **MG996R** movem um painel solar de 10 W para seguir a luz.
Alimentação: bateria 12 V + 2 conversores XL4015 (6 V servos, 7,5 V no VIN do Nano).
O diagrama do Tinkercad usa UNO só porque o Tinkercad não tem Nano (mesmo ATmega328P e pinos).
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
main.c                  Firmware (sketch Arduino em C++, apesar da extensão .c)
docs/diagrama_tinkercad.png   Circuito de referência (Tinkercad)
docs/specs/             Especificações — leia antes de mudar comportamento
3d_material/amf/        Montagem 3D completa (.AMF, ~11 MB)
3d_material/stl/        Peças individuais para impressão (exportadas nas coordenadas da montagem)
simulator/              Simulador 3D: firmware real emulado (avr8js) + STLs (three.js)
tools/render/           Renders fotorrealistas da montagem no Blender (figuras do relatório)
docs/relatorio/         Relatório do PIM II (.docx) e figuras
.claude/skills/         Skills do projeto
```

Specs: [visão geral](docs/specs/01-visao-geral.md) · [hardware](docs/specs/02-hardware.md) ·
[firmware](docs/specs/03-firmware.md) · [mecânica](docs/specs/04-mecanica.md) ·
[testes](docs/specs/05-testes.md) · [problemas conhecidos](docs/specs/06-problemas-conhecidos.md)

## Pontos de atenção (não óbvios)

- **Pinos dos LDRs divergem:** código usa A1–A4, diagrama usa A0–A3. Não "corrigir" um lado sem
  confirmar com o usuário qual reflete a montagem real.
- **Convenção do sensor:** leitura maior = mais luz (LDR no lado do 5 V do divisor). Inverter o
  divisor inverte o sentido dos eixos.
- **Sinais dos eixos** (`+=`/`-=`) dependem da montagem mecânica; o eixo vertical é propositalmente
  invertido em relação ao horizontal.
- **Limites 20°–160°** protegem a estrutura impressa — não ampliar sem checar a mecânica.
- **Serial a 9600 baud dita o ritmo do laço** (~100 ms por linha, medido). Mudanças de
  temporização devem considerar isso.
- **O sentido da correção horizontal depende do lado da placa** (`sentidoHorizontal` no
  `main.c`, P10 em problemas conhecidos). Não remover: sem isso o servo horizontal trava no limite
  sempre que o vertical fica abaixo de 90°.
- O AMF guarda as posições das peças em **metros** e a geometria em mm; prefira os STLs, que já
  estão nas coordenadas da montagem.
- O código precisa continuar **compatível com o Tinkercad** (só bibliotecas padrão: `Servo`; sem
  libs externas).
- Arquivos `.AMF`/`.STL` são binários/grandes: não ler nem editar; só referenciar.

## Build / verificação

Não há testes automatizados. Para checar se compila (requer `arduino-cli`, ver skill
`firmware-arduino`):

```bash
arduino-cli compile --fqbn arduino:avr:nano <pasta-do-sketch>
```

Como o arquivo é `main.c`, para compilar é preciso copiá-lo para `<pasta>/<pasta>.ino` (ver P2 em
problemas conhecidos).

## Ao alterar o firmware

1. Manter a telemetria serial (o usuário usa para calibrar e para o relatório).
2. Atualizar `docs/specs/03-firmware.md` se mudar parâmetros, algoritmo ou formato serial.
3. Atualizar `docs/specs/02-hardware.md` se mudar pinos.
4. Compilar antes de dizer que está pronto.
5. Validar o comportamento no simulador (skill `simulador-3d`): `./simulator/build-firmware.sh`
   regenera o `.hex`; o `.hex` versionado precisa corresponder ao `main.c` commitado.
