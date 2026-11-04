# 06 — Problemas conhecidos e melhorias

Resultado da análise do repositório (nov/2026). Ordenado por impacto.

## <a id="p1"></a>P1 — Pinos dos LDRs divergem entre código e diagrama (alto)

`main.c` lê **A1–A4**; o diagrama do Tinkercad liga os LDRs em **A0–A3**. Montado como no
diagrama, o firmware lê A4 (vazio, flutuando) e perde A0 → o rastreador se comporta de forma
errática. **Correção:** alinhar um ao outro (o mais simples é mudar o código para A0–A3).

## <a id="p2"></a>P2 — Extensão `.c` em código C++/Arduino (médio)

`main.c` usa classes (`Servo`), então é C++. Um compilador C rejeita o arquivo, e a Arduino IDE só
abre *sketches* `.ino` dentro de uma pasta com o mesmo nome. **Correção sugerida:** mover para
`firmware/solar_tracker/solar_tracker.ino`.

## <a id="p3"></a>P3 — `Servo.h` copiado na raiz (baixo)

É apenas o cabeçalho da biblioteca oficial (sem `.cpp` nem `ServoTimers.h`). Como o código usa
`#include <Servo.h>` (colchetes), a IDE usa a biblioteca instalada e ignora esta cópia; se alguém
trocar para aspas, a compilação quebra. **Correção:** remover o arquivo (ou mover para `docs/` como
referência).

## <a id="p4"></a>P4 — Telemetria serial deixa o laço lento (médio)

~95 caracteres por linha a 9600 baud ≈ 100 ms por linha, bloqueando o laço (ver
[03-firmware.md](03-firmware.md#temporização-real)). **Correções:** usar `Serial.begin(115200)`,
e/ou imprimir a cada N ciclos, e/ou formato compacto (CSV: `e,d,s,i,h,v`), que também facilita
plotar no Serial Plotter da IDE.

## <a id="p5"></a>P5 — Servos alimentados pelo 5 V do Arduino (médio, só no físico)

Picos de corrente dos dois servos podem resetar o Arduino. Ver
[02-hardware.md](02-hardware.md#alimentação).

## P6 — Sem filtro nas leituras (baixo)

Ruído do ADC/iluminação pode gerar micro-movimentos. **Melhoria:** média de várias leituras por
sensor ou filtro exponencial (`x = x*0.8 + leitura*0.2`).

## P7 — Sem compensação entre LDRs (baixo)

LDRs do mesmo lote variam bastante. **Melhoria:** offsets de calibração por sensor, medidos com luz
uniforme no `setup()`.

## P8 — Sem modo noturno (baixo)

No escuro as leituras ficam próximas e a placa para onde estiver. **Melhoria:** se a soma das 4
leituras ficar abaixo de um limiar por alguns minutos, voltar à posição de "nascer do sol" (leste).

## P9 — Controle proporcional (melhoria opcional)

Hoje o passo é fixo (2°). Um passo proporcional ao erro (`PASSO = k * (esquerda - direita)`,
limitado) aproxima mais rápido quando longe e suaviza perto do alvo — bom tópico para o relatório
(comparação bang-bang × proporcional).

## P10 — Medição de energia (melhoria para o relatório)

Ler a tensão da placa em uma entrada analógica e enviar na telemetria permite provar o ganho do
rastreador em relação a uma placa fixa (ver [05-testes.md](05-testes.md)).
