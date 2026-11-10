# Pendências do relatório — versão 2 (ESP32 + testes físicos)

Itens marcados em **amarelo** (`[PREENCHER: …]`) no `PIM_Torre_Solar_v2.docx` (36 páginas; limite
combinado: 40). Preencher no `tools/relatorio/gerar_relatorio.py` e regenerar, ou editar direto no Word.

## Folha de rosto

- [ ] Nome do professor orientador
- [ ] Confirmar **Campus Sorocaba** e o nome do curso

## Testes físicos (cap. 4 e Tabela 3) — só registrar o que foi realmente feito

- [ ] **Quebra da peça (4.3):** onde quebrou, causa e solução adotada (reimpressão? mais perímetros?)
- [ ] **Tensão ajustada no XL4015 da placa do ESP32** (4.4) e dos servos — valores medidos
- [ ] **Rastreamento automático** com lanterna ou ao sol: foi testado? resultado?
- [ ] **Repouso noturno** no protótipo: foi observado?
- [ ] Confirmar que os divisores dos LDRs estão no **3V3** do ESP32 (entradas não toleram 5 V)

## Projeto

- [ ] Software e método de fabricação da **PCI** (3.7)
- [ ] Valores pagos: ESP32 + placa de expansão, MG996R, XL4015, bateria, painel, filamento (Tabela 2)

## Decisões do grupo (achados do simulador com o mesmo `main.c`)

- [ ] **P10 regrediu:** restaurar `sentidoHorizontal` no `main.c` do ESP32?
- [ ] **P14:** `TOLERANCIA` de 40 → ~160 (ADC de 12 bits)?
- [ ] **P13:** espaçador de 25 mm no suporte dos LDRs?

As três correções já foram testadas em simulação (variante `esp32_tol160_p10`: +35% em junho e
+49% em dezembro sobre a placa fixa). Se aplicadas ao `main.c`, rodar `./simulator/build-firmware.sh`
e atualizar o capítulo 5.

## Para a apresentação oral

Sugestão de roteiro: problema (cosseno) → solução (rastreador + torre) → montagem e testes físicos
(fotos do cap. 4) → simulador com o mesmo código (mostrar a página do celular dentro dele) → **a
história dos erros** (P10, testes contaminados, sombra do painel, peça quebrada, regressões do ESP32)
→ resultados → próximos passos. Figuras em `docs/relatorio/figuras/`.
