# CLAUDE.md

Rastreador solar de dois eixos — PIM (Projeto Integrado Multidisciplinar) da UNIP.
Arduino UNO + 4 LDRs + 2 servos movem uma placa fotovoltaica para seguir a luz.

## Idioma

Responder, comentar código e escrever documentação **em português do Brasil**. Nomes de variáveis
seguem o padrão já usado no código (português, `camelCase`; constantes em `MAIUSCULAS`).

## Estrutura

```
main.c                  Firmware (sketch Arduino em C++, apesar da extensão .c)
docs/diagrama_tinkercad.png   Circuito de referência (Tinkercad)
docs/specs/             Especificações — leia antes de mudar comportamento
3d_material/amf/        Montagem 3D completa (.AMF, ~11 MB)
3d_material/stl/        Peças individuais para impressão
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
- **Serial a 9600 baud bloqueia o laço** (~100 ms por linha). Mudanças de temporização devem
  considerar isso.
- O código precisa continuar **compatível com o Tinkercad** (só bibliotecas padrão: `Servo`; sem
  libs externas).
- Arquivos `.AMF`/`.STL` são binários/grandes: não ler nem editar; só referenciar.

## Build / verificação

Não há testes automatizados. Para checar se compila (requer `arduino-cli`, ver skill
`firmware-arduino`):

```bash
arduino-cli compile --fqbn arduino:avr:uno <pasta-do-sketch>
```

Como o arquivo é `main.c`, para compilar é preciso copiá-lo para `<pasta>/<pasta>.ino` (ver P2 em
problemas conhecidos).

## Ao alterar o firmware

1. Manter a telemetria serial (o usuário usa para calibrar e para o relatório).
2. Atualizar `docs/specs/03-firmware.md` se mudar parâmetros, algoritmo ou formato serial.
3. Atualizar `docs/specs/02-hardware.md` se mudar pinos.
4. Compilar antes de dizer que está pronto.
