# 06 — Problemas conhecidos e melhorias

Resultado da análise do repositório e das simulações (nov/2026). **Projeto concluído — nenhuma pendência.** Corrigidos no `main.c` final: P1, P7, P10, P14, P15.
Os demais itens (P2, P5, P6, P8, P9, P11, P13) ficam registrados como **melhorias possíveis**;
o teste com lanterna (sentido invertido) está registrado com causas e roteiro de diagnóstico em
`05-testes.md` (F-03). Conclusão do projeto: [07-conclusao.md](07-conclusao.md). P3 só valia para o Nano; P4 confirmado na montagem; P12 resolvido (controlador de carga na montagem final).

## <a id="p1"></a>P1 — Pinos dos LDRs divergem entre código e diagrama — encerrado com a migração para o ESP32

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

## <a id="p4"></a>P4 — Alimentação dos servos — ✅ resolvido (montagem confirmada pelo grupo em 24/11/2026)

O diagrama do Tinkercad alimenta os servos pelo 5 V do Arduino, o que não funciona com MG996R
(até ~2,5 A cada). O projeto físico usa bateria 12 V + XL4015 dedicado aos servos (6 V). Riscos que
continuam: XL4015 desajustado (medir antes de ligar), GND não interligado, jumpers Dupont finos
demais para a corrente dos servos. Ver [02-hardware.md](02-hardware.md#alimentação).

**Confirmado pelo grupo:** servos numa fonte externa regulada de 6 V, GND dessa fonte ligado ao GND
do ESP32, LDRs no 3,3 V do ESP32.

## <a id="p12"></a>P12 — Sem controlador de carga entre painel e bateria — resolvido

**Resolvido na montagem final:** o grupo usou um controlador de carga solar 12 V (com 2 portas USB,
uma delas alimentando o ESP32). Registro original:

O painel de 10 W (≈ 18 V em operação, ≈ 21 V em aberto) não pode ser ligado direto à bateria
selada de 12 V: sobrecarrega durante o dia e descarrega a bateria pelo painel à noite. Nenhum
controlador aparece na lista de compras. **Correção:** controlador PWM 12 V (≥ 5 A) entre painel e
bateria — ou não ligar o painel à bateria e usá-lo só para medir a geração.

## P5 — Sem filtro nas leituras (baixo)

Ruído do ADC/iluminação pode gerar micro-movimentos. **Melhoria:** média de várias leituras por
sensor ou filtro exponencial (`x = x*0.8 + leitura*0.2`).

## P6 — Sem compensação entre LDRs (baixo)

LDRs do mesmo lote variam bastante. **Melhoria:** offsets de calibração por sensor, medidos com luz
uniforme no `setup()`.

## <a id="p7"></a>P7 — Sem modo noturno — ✅ resolvido no firmware ESP32 (repouso noturno)

No escuro as leituras ficam próximas e a placa para onde estiver (voltada a Oeste). Simulação de
21/jun sem reiniciar o Arduino entre um dia e outro: a placa amanhece de costas para o Sol (erro
110° às 7 h) e só se realinha perto das 10h45; ligando às 6h30 em 90°/90°, alinha às 8h50 (erro 2° às
9h50) — `docs/relatorio/dados/noite_elev25.json`. **Melhoria:** se a soma das 4 leituras ficar
abaixo de um limiar por alguns minutos, voltar à posição inicial (90°/90°) ou ao nascente.

## P8 — Controle proporcional (melhoria opcional)

Hoje o passo é fixo (2°). Um passo proporcional ao erro (`PASSO = k * (esquerda - direita)`,
limitado) aproxima mais rápido quando longe e suaviza perto do alvo — bom tópico para o relatório
(comparação bang-bang × proporcional).

## P9 — Medição de energia (melhoria para o relatório)

Ler a tensão da placa em uma entrada analógica e enviar na telemetria permite provar o ganho do
rastreador em relação a uma placa fixa (ver [05-testes.md](05-testes.md)).

## <a id="p10"></a>P10 — Correção horizontal se inverte quando a placa passa da vertical — ✅ corrigido (Nano), regrediu no ESP32 e foi **restaurado em 11/11/2026**

> O `main.c` do ESP32 não tem `sentidoHorizontal`. Simulação com o mesmo `main.c`: Sol a SE 40° → erro 54°
> (H travado em 160°); SO 35° → 59°. Com a correção restaurada (variante `esp32_tol160_p10`): 18° / 17°.
> Dados: `docs/relatorio/dados/esp32_cenarios_elev25.json`.

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

> Se em alguma montagem a placa fugir do sol só quando o servo vertical está abaixo (ou acima) de
> 90°, trocar `>= 90` por `< 90`.

## <a id="p11"></a>P11 — Erro residual por saturação dos LDRs + zona morta (médio)

*Encontrado com o simulador.* Com luz forte, os quatro divisores (LDR + 10 kΩ) ficam perto de 5 V;
a diferença entre lados cai abaixo de `TOLERANCIA = 40` antes de a placa estar alinhada e o
firmware para. A ~1 000 lux a placa estabiliza com 12–18° de erro (≈ 3–5 % de perda, cos θ); sob
sol pleno (~100 000 lux) os LDRs saturam completamente e quase não há sinal.

**Melhorias:** resistor fixo menor (1–2,2 kΩ) para uso ao sol, anteparo do divisor mais alto,
tolerância relativa (`|e − d| > 5 % de (e + d)`) em vez de absoluta.

## <a id="p13"></a>P13 — O próprio painel sombreia os LDRs (alto) — encontrado em simulação

No CAD, o suporte dos LDRs fica preso à borda da trave ~13 mm **abaixo** do plano do painel. Com o
Sol baixo vindo do lado "inferior" do painel, a trave/painel sombreiam os LDRs inferiores; o firmware
lê "mais luz em cima" e inclina o painel para longe do Sol, ficando preso. Simulação de 21/jun
(lat −23,55°, partindo de 90°/90° ao amanhecer): rastreador capta **−74%** em relação à placa fixa.
Com o suporte elevado 25 mm (`simulator/?elevacaoLdr=25`): **+33%**, erro < 20° das 8h40 às 17 h.
Em 21/dez as duas geometrias rendem +48%. Dados: `docs/relatorio/dados/dia172*.json`, `dia355*.json`.

**Correção proposta:** espaçador de ~25 mm (ou reimprimir `SUPORTE_DO_SUPORTE_LDR`) para que os
sensores fiquem acima do painel. **Ressalva:** posição/espessura do painel real foram estimadas no
modelo; o efeito pode ser maior ou menor no protótipo.

Diagnóstico no simulador: `sim.bloqueios()` mostra qual peça bloqueia o raio de cada LDR ao Sol.

## <a id="p14"></a>P14 — Tolerância não foi reescalonada para o ADC de 12 bits — ✅ corrigido (`TOLERANCIA = 160`, 11/11/2026)

No Nano, `TOLERANCIA = 40` era ~4% da escala (0–1023). No ESP32 o ADC vai de 0 a 4095 e o mesmo 40
vale ~1%: a diferença natural entre LDRs (±10%) passa a comandar o painel com pouca luz. Simulação
de 21/jun com o `main.c` atual: ao amanhecer o painel desce até V = 20° e fica de costas para o Sol
o dia todo (−100% de energia). Sem variação entre LDRs o rastreamento funciona (erro 1°–8°);
com `TOLERANCIA = 160` (variante `esp32_tol160`): +35% sobre a placa fixa.

**Correção:** `TOLERANCIA = 160` (ou tolerância relativa à soma das leituras — ver P11) e calibrar
com o painel real.

## <a id="p15"></a>P15 — No inverno, depois do repouso noturno, o painel acorda preso no limite — ✅ corrigido (`INICIO_H = 90`, 24/11/2026)

Encontrado pela simulação do ano inteiro (painel "📅 Ano inteiro" do simulador). Em junho, o painel
acorda na posição de repouso (H = 20°, V = 90°); o eixo vertical desce para baixo de 90°, o
`sentidoHorizontal` inverte (P10) e empurra o horizontal contra o limite de 20°. O painel fica
preso em H = 20° até perto do meio-dia (erro de ~55° a manhã toda) e só então se solta. Confirmado
também com o Sol andando devagar (não é efeito do tempo acelerado). Em dezembro não acontece.

Efeito no ano (`?elevacaoLdr=25`, amostragem a cada 15 dias): ganho anual de ~+38% sobre a placa
fixa, mas erro médio de apontamento de ~40° em maio–julho contra ~18° no verão.

**Correção aplicada:** estacionar à noite com o horizontal no centro, `INICIO_H = 90` (era 20).
Comparação no simulador, ano inteiro (`?elevacaoLdr=25`, a cada 15 dias), mesmo `main.c` mudando só
o necessário (variantes em `simulator/firmware/variantes/`):

| Variante | Ganho anual × placa fixa | Erro médio | 21/jun (ganho / erro) | 21/dez |
|----------|-------------------------|------------|-----------------------|--------|
| Antes (`esp32_antes_p15`, repouso em H = 20°) | +34,5% | 27,7° | +4% / 42° | +63% / 19° |
| **`INICIO_H = 90` (aplicada)** | **+47,1%** | **16,9°** | **+38% / 16°** | +67% / 18° |
| Horizontal travado no limite → vertical cruza 90° | +32,7% | 23,1° | +23% / 21° | +49% / 22° |
| As duas juntas | +44,0% | 17,7° | +38% / 16° | +58% / 20° |

Dados: `docs/relatorio/dados/ano_p15.json`. Teste de verificação no protótipo: F-10 em `05-testes.md`.
