# Solar Smart Tower — rastreador solar de dois eixos (PIM II · UNIP)

Protótipo de **rastreador solar de dois eixos**: um **ESP32**, quatro LDRs e dois servos **MG996R**
mantêm um painel solar de 10 W apontado para a luz. É o subsistema de rastreamento da torre solar
do PIM II (carregamento de celulares por USB), alimentada por bateria de 12 V com conversores
XL4015. O ESP32 cria a rede Wi-Fi **`SOLAR_TOWER`** e serve uma **IHM** para o celular em
`http://192.168.4.1`.

> **Projeto concluído.** Conclusão em [07-conclusao.md](docs/specs/07-conclusao.md): o rastreador
> rende ~+47% sobre uma placa fixa (simulação do ano), mas **não compensa** nesse porte — duas placas
> fixas voltadas para Leste e Oeste geram mais (+82%), custam menos e não têm peças móveis, como
> confirmaram fornecedores de postes solares profissionais.

## Conteúdo

| Pasta/arquivo | Descrição |
|---------------|-----------|
| `main.c` | Firmware do ESP32 (sketch Arduino em C++): rastreamento, repouso noturno, Wi-Fi e IHM |
| `docs/specs/` | Especificações: visão geral, hardware, firmware, mecânica, testes, problemas, conclusão |
| `docs/relatorio/` | Relatório do PIM II (`.docx` + `.pdf` para impressão + `.low.pdf` ≤ 10 MB para submissão) |
| `docs/etiquetas/` | Etiquetas adesivas da torre (título 90 × 32 mm e Wi-Fi 90 × 60 mm com QR da rede e QR da IHM): `etiquetas_A4.pdf`; arte do poste 120 × 400 mm (`poster_poste_A3.pdf`). Imprimir em 100% |
| `docs/video/` | Vídeos de demonstração: IHM (`demo_ihm.mp4`) e simulador (`demo_simulador.mp4`) |
| `docs/imagens_videos_testes_fisicos/` | Fotos e vídeos dos testes físicos (e capturas do simulador do P15) |
| `3d_material/` | Peças para impressão 3D (`stl/`) e montagem completa (`amf/`) |
| `simulator/` | Simulador 3D no navegador: o mesmo `main.c` compilado para WebAssembly sobre as peças 3D |
| `tools/` | Geração do relatório, renders do Blender, gravação dos vídeos e etiquetas |

## Hardware e ligações

| Sinal | ESP32 |
|-------|-------|
| LDR superior esquerdo / superior direito | GPIO 34 / GPIO 35 |
| LDR inferior esquerdo / inferior direito | GPIO 32 / GPIO 33 |
| Servo horizontal / vertical (sinal) | GPIO 18 / GPIO 19 |

- **LDRs:** divisores com 10 kΩ no **3,3 V do ESP32** e GND (as entradas não toleram 5 V).
- **Servos:** fonte externa regulada de **6 V** (XL4015 a partir da bateria de 12 V).
- **GND da fonte dos servos ligado ao GND do ESP32.**

Lista de materiais e detalhes: [02-hardware.md](docs/specs/02-hardware.md).

## Como funciona

Os quatro LDRs ficam em cruz, separados por um anteparo. Quando a luz vem de um lado, o anteparo
sombreia os sensores do lado oposto; o ESP32 compara as médias (esquerda × direita,
superior × inferior) a cada 100 ms e gira cada servo 2° na direção da luz até equilibrar (zona
morta de 160 no ADC de 12 bits). À noite (luz baixa por 2 min) o painel estaciona no centro
(90°/90°) e volta a rastrear depois de 30 s de luz.

**IHM pelo celular** (rede `SOLAR_TOWER`, senha `torre1234`, `http://192.168.4.1`, funciona sem
internet): modo automático/manual, dia/noite, leitura dos 4 LDRs, diferença entre lados, ângulos dos
servos, gráfico dos últimos 60 s, setas de movimento manual e retorno à posição inicial.

Detalhes: [01-visao-geral.md](docs/specs/01-visao-geral.md) · [03-firmware.md](docs/specs/03-firmware.md).

## Gravar no ESP32

1. Ajustar os XL4015 com multímetro **antes** de ligar as cargas (6 V).
2. Montar o circuito conforme a tabela acima.
3. Arduino IDE (ou `arduino-cli`): placa **ESP32 Dev Module**, biblioteca **ESP32Servo**. Como o
   arquivo se chama `main.c`, copie-o para uma pasta `torre/torre.ino` antes de compilar.
4. Conectar o celular à rede `SOLAR_TOWER` e abrir `http://192.168.4.1`.

## Simulador 3D

Teste o código sem hardware: mova o sol, veja a estrutura seguir a luz, use a IHM do celular dentro
do simulador, injete falhas (servo invertido, fiação, ruído) e simule **o ano inteiro** comparando
com uma placa fixa.

```bash
python3 -m http.server 8000   # na raiz do repositório
```

Abra http://localhost:8000/simulator/ — detalhes em [simulator/README.md](simulator/README.md).

## Histórico

O projeto começou com Arduino Nano (diagrama do Tinkercad abaixo, com UNO, que o Tinkercad oferece)
e migrou para o ESP32 na etapa de testes físicos. Os erros e acertos do caminho (P1–P15) estão em
[06-problemas-conhecidos.md](docs/specs/06-problemas-conhecidos.md).

![Circuito da fase inicial no Tinkercad](docs/diagrama_tinkercad.png)
