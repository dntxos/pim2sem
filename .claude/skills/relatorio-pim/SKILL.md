---
name: relatorio-pim
description: Redigir seções do relatório acadêmico do PIM (UNIP) sobre o rastreador solar — introdução, fundamentação teórica, metodologia, desenvolvimento, resultados, conclusão — em português formal e normas ABNT. Use quando pedirem texto para o trabalho, relatório, apresentação, slides ou explicação do projeto para a banca.
---

# Relatório do PIM — rastreador solar

## Fontes de verdade

Antes de escrever, leia `docs/specs/` e `main.c`. **Não invente** medições, resultados ou valores de
ganho energético: se não houver dados medidos, deixe marcadores como `[INSERIR MEDIÇÃO]` e avise o
usuário. Números do projeto (pinos, TOLERANCIA=40, PASSO=2, limites 20°–160°, 4 LDRs, 2 servos SG90,
Arduino UNO) devem vir do código/specs atuais.

## Estrutura típica de PIM

1. **Introdução** — energia solar fotovoltaica, problema da placa fixa (perda por ângulo de
   incidência), objetivo geral e específicos.
2. **Fundamentação teórica** — efeito fotovoltaico; irradiância e lei do cosseno (potência ∝ cos θ
   do ângulo de incidência); LDR e divisor de tensão; servomotor e PWM (50 Hz, pulso 0,5–2,4 ms);
   microcontrolador/Arduino; controle em malha fechada (bang-bang com zona morta); tipos de
   rastreadores (1 eixo × 2 eixos; sensorial × astronômico).
3. **Metodologia / Materiais** — BOM (`02-hardware.md`), simulação no Tinkercad, modelagem e
   impressão 3D (`04-mecanica.md`).
4. **Desenvolvimento** — circuito (figura `docs/diagrama_tinkercad.png`), algoritmo (fluxograma a
   partir de `03-firmware.md`), montagem mecânica.
5. **Testes e resultados** — tabela de testes (`05-testes.md`), gráficos da telemetria (skill
   `calibrar-tracker`), comparação placa fixa × rastreando quando houver dados.
6. **Conclusão** — objetivos atingidos, limitações (`06-problemas-conhecidos.md`) e trabalhos
   futuros (controle proporcional, modo noturno, medição de energia).
7. **Referências** — formato ABNT (NBR 6023). Use apenas referências reais e verificáveis; na
   dúvida, sugira o tipo de fonte e peça ao usuário para confirmar.

## Estilo

- Português formal, impessoal (3ª pessoa / voz passiva), sem gírias.
- Figuras e tabelas numeradas com legenda e fonte ("Fonte: autoria própria, 2026").
- Siglas por extenso na primeira ocorrência (LDR — *Light Dependent Resistor*).
- Termos estrangeiros em itálico.
- Entregar em Markdown por padrão; se o usuário pedir .docx ou slides, usar a skill/formato
  correspondente.
