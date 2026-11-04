# 05 — Plano de testes e calibração

> Os testes T-01 a T-08 e F-01 a F-03 também podem ser feitos no **simulador 3D**
> ([simulator/README.md](../../simulator/README.md)), que roda o firmware compilado sobre as peças
> reais. Cenários de regressão já conhecidos estão na skill `.claude/skills/simulador-3d`.

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
| F-00 | Antes de tudo: XL4015 sem carga, medir com multímetro | #1 = 6,0 V (servos); #2 = 7,5 V (VIN do Nano). Só então ligar as cargas. |
| F-01 | Lanterna movida lentamente em arco | Placa acompanha a lanterna. |
| F-02 | Lanterna parada | Placa estabiliza sem "tremer" (sem oscilação contínua). |
| F-03 | Sentido dos eixos | Placa vai **em direção** à luz. Se fugir, inverter o sinal do eixo. |
| F-04 | Alimentação | Nano não reinicia quando os dois servos se movem juntos; XL4015 #1 não esquenta demais. |
| F-05 | Sol real (opcional) | Ao longo de algumas horas, placa segue o sol. |
| F-06 | Torque na elevação | Com o painel montado, o servo vertical segura a placa em 20° e 160° sem "cair" nem zumbir forte. |
| F-07 | Autonomia (opcional) | Medir tensão da bateria no início e no fim do dia; com controlador de carga, deve subir ao sol. |

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
