# Rastreador Solar — PIM UNIP

Protótipo de **rastreador solar de dois eixos**: Arduino UNO, quatro LDRs e dois servos mantêm uma
placa fotovoltaica apontada para a luz, aumentando o aproveitamento de energia.

![Circuito no Tinkercad](docs/diagrama_tinkercad.png)

## Conteúdo

| Pasta/arquivo | Descrição |
|---------------|-----------|
| `main.c` | Firmware do Arduino |
| `docs/specs/` | Especificações (requisitos, hardware, firmware, mecânica, testes) |
| `3d_material/` | Peças para impressão 3D (`stl/`) e montagem completa (`amf/`) |

## Como funciona

Os quatro LDRs ficam em cruz, separados por um anteparo. Quando a luz vem de um lado, o anteparo
sombreia os sensores do lado oposto; o Arduino compara as médias (esquerda × direita,
superior × inferior) e gira cada servo alguns graus na direção da luz até equilibrar.

Detalhes em [docs/specs/01-visao-geral.md](docs/specs/01-visao-geral.md).

## Executar

1. Montar o circuito conforme o diagrama (ver pinos em [02-hardware.md](docs/specs/02-hardware.md)).
2. Abrir o código na Arduino IDE (placa **Arduino Uno**) e enviar.
3. Abrir o Monitor Serial a 9600 baud para ver as leituras.
