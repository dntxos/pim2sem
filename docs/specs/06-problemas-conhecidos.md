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

## <a id="p3"></a>P3 — Telemetria serial deixa o laço lento (médio)

~95 caracteres por linha a 9600 baud ≈ 100 ms por linha; o laço fica preso a esse ritmo (ver
[03-firmware.md](03-firmware.md#temporização-real)). **Correções:** usar `Serial.begin(115200)`,
e/ou imprimir a cada N ciclos, e/ou formato compacto (CSV: `e,d,s,i,h,v`), que também facilita
plotar no Serial Plotter da IDE.

## <a id="p4"></a>P4 — Servos alimentados pelo 5 V do Arduino (médio, só no físico)

Picos de corrente dos dois servos podem resetar o Arduino. Ver
[02-hardware.md](02-hardware.md#alimentação).

## P5 — Sem filtro nas leituras (baixo)

Ruído do ADC/iluminação pode gerar micro-movimentos. **Melhoria:** média de várias leituras por
sensor ou filtro exponencial (`x = x*0.8 + leitura*0.2`).

## P6 — Sem compensação entre LDRs (baixo)

LDRs do mesmo lote variam bastante. **Melhoria:** offsets de calibração por sensor, medidos com luz
uniforme no `setup()`.

## P7 — Sem modo noturno (baixo)

No escuro as leituras ficam próximas e a placa para onde estiver. **Melhoria:** se a soma das 4
leituras ficar abaixo de um limiar por alguns minutos, voltar à posição de "nascer do sol" (leste).

## P8 — Controle proporcional (melhoria opcional)

Hoje o passo é fixo (2°). Um passo proporcional ao erro (`PASSO = k * (esquerda - direita)`,
limitado) aproxima mais rápido quando longe e suaviza perto do alvo — bom tópico para o relatório
(comparação bang-bang × proporcional).

## P9 — Medição de energia (melhoria para o relatório)

Ler a tensão da placa em uma entrada analógica e enviar na telemetria permite provar o ganho do
rastreador em relação a uma placa fixa (ver [05-testes.md](05-testes.md)).

## <a id="p10"></a>P10 — Correção horizontal se inverte quando a placa passa da vertical — ✅ corrigido

*Encontrado com o simulador.* Os LDRs ficam presos à placa, então "esquerda/direita" é medido no
referencial da placa. Quando o servo vertical cruza 90° (a face passa a olhar para o outro lado),
girar o azimute no mesmo sentido move o sol para o lado **oposto** do sensor. O firmware original
sempre aplicava `anguloHorizontal += PASSO` para "esquerda mais clara", então em metade da faixa
de elevação a correção horizontal empurrava a placa para longe do sol até o limite (20° ou 160°).
Isso acontece para qualquer sentido de montagem dos servos — só muda qual metade da faixa falha.

**Correção aplicada em `main.c`:** o sentido da correção horizontal depende do lado da placa.

```cpp
int sentidoHorizontal = (anguloVertical >= 90) ? 1 : -1;
if (esquerda > direita + TOLERANCIA)      anguloHorizontal += sentidoHorizontal * PASSO;
else if (direita > esquerda + TOLERANCIA) anguloHorizontal -= sentidoHorizontal * PASSO;
```

Resultado no simulador (partindo do `setup()`, servos em 90°/90°, ~1 000 lux, 6 s):

| Sol | Antes | Depois |
|-----|-------|--------|
| Sudeste, 40° | erro 53° (H travado em 160°) | erro 18° |
| Sudoeste, 35° | erro 58° (H travado em 20°) | erro 17° |
| Nordeste 30° / Noroeste 35° | 17–18° | 17–18° (sem mudança) |
| Leste 55° / Oeste 50° (cruza 90°) | — | 18°, sem oscilação na fronteira |

> No protótipo físico, conferir o lado: se a placa fugir do sol só quando o servo vertical está
> abaixo (ou acima) de 90°, trocar `>= 90` por `< 90`.

## <a id="p11"></a>P11 — Erro residual por saturação dos LDRs + zona morta (médio)

*Encontrado com o simulador.* Com luz forte, os quatro divisores (LDR + 10 kΩ) ficam perto de 5 V;
a diferença entre lados cai abaixo de `TOLERANCIA = 40` antes de a placa estar alinhada e o
firmware para. A ~1 000 lux a placa estabiliza com 12–18° de erro (≈ 3–5 % de perda, cos θ); sob
sol pleno (~100 000 lux) os LDRs saturam completamente e quase não há sinal.

**Melhorias:** resistor fixo menor (1–2,2 kΩ) para uso ao sol, anteparo do divisor mais alto,
tolerância relativa (`|e − d| > 5 % de (e + d)`) em vez de absoluta.
