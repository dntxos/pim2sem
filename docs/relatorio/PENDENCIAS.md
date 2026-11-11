# Pendências do relatório — versão 3 (ESP32 + testes físicos + correções P10/P14)

Itens marcados em **amarelo** (`[PREENCHER: …]`) no `PIM_Torre_Solar_v3.docx` (36 páginas; limite
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

## Firmware

- [x] **P10** (`sentidoHorizontal`) e **P14** (`TOLERANCIA = 160`) aplicados ao `main.c` em 11/11/2026
      e validados em simulação (+35% em junho, +49% em dezembro sobre a placa fixa).
- [ ] **Gravar o `main.c` corrigido no ESP32 e testar no protótipo** (lanterna em arco com o painel
      dos dois lados da vertical; conferir se o painel não "foge" com pouca luz). Preencher a linha
      "Correções P10 e P14 no protótipo" da Tabela 3.
- [ ] **P13:** espaçador de 25 mm no suporte dos LDRs?

## Para a apresentação oral

Sugestão de roteiro: problema (cosseno) → solução (rastreador + torre) → montagem e testes físicos
(fotos do cap. 4) → simulador com o mesmo código (mostrar a página do celular dentro dele) → **a
história dos erros** (P10, testes contaminados, sombra do painel, peça quebrada, regressões do ESP32)
→ resultados → próximos passos. Figuras em `docs/relatorio/figuras/`.
