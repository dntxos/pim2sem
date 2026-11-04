# 05 — Plano de testes e calibração

## Testes no Tinkercad (simulação)

| ID | Cenário | Ação | Resultado esperado |
|----|---------|------|--------------------|
| T-01 | Luz uniforme | Todos os LDRs no mesmo nível | Servos parados em 90°/90°. |
| T-02 | Luz à esquerda | Aumentar luz de SE e IE | Horizontal aumenta até 160° ou até equilibrar. |
| T-03 | Luz à direita | Aumentar luz de SD e ID | Horizontal diminui até 20° ou até equilibrar. |
| T-04 | Luz em cima | Aumentar luz de SE e SD | Vertical diminui. |
| T-05 | Luz embaixo | Aumentar luz de IE e ID | Vertical aumenta. |
| T-06 | Diagonal | Aumentar só SE | Os dois eixos se movem. |
| T-07 | Diferença pequena | Diferença < 40 entre lados | Nenhum movimento (zona morta). |
| T-08 | Limites | Manter luz extrema de um lado | Ângulo para em 20° ou 160°, sem passar. |

## Testes no protótipo físico

| ID | Cenário | Resultado esperado |
|----|---------|--------------------|
| F-01 | Lanterna movida lentamente em arco | Placa acompanha a lanterna. |
| F-02 | Lanterna parada | Placa estabiliza sem "tremer" (sem oscilação contínua). |
| F-03 | Sentido dos eixos | Placa vai **em direção** à luz. Se fugir, inverter o sinal do eixo. |
| F-04 | Alimentação | Arduino não reinicia quando os dois servos se movem juntos. |
| F-05 | Sol real (opcional) | Ao longo de algumas horas, placa segue o sol. |

## Calibração

1. Abrir o Monitor Serial (9600 baud) com luz uniforme sobre os LDRs.
2. Anotar a diferença natural entre lados (LDRs nunca são idênticos). `TOLERANCIA` deve ficar
   acima dessa diferença, com folga.
3. Se oscilar: aumentar `TOLERANCIA` ou diminuir `PASSO`.
4. Se for lento demais: aumentar `PASSO` ou reduzir o `delay`.

## Ensaio comparativo para o relatório (sugestão)

Para demonstrar o ganho do rastreador, medir a tensão/corrente da placa em dois cenários
(placa fixa vs. rastreando) ao longo do mesmo período e comparar a energia. Exige ligar a placa a
uma entrada analógica (com divisor se a tensão passar de 5 V) ou usar um multímetro.
