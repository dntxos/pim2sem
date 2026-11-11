# Pendências do relatório — versão 4

`PIM_Torre_Solar_v4.docx` / `.pdf` — 37 páginas (limite combinado: 40). Itens em **amarelo**
(`[PREENCHER: …]`) ainda dependem do grupo. Preencher em `tools/relatorio/gerar_relatorio.py` e
regenerar, ou editar direto no Word.

## Ainda em aberto

- [ ] **Custos:** valor do **ESP32 + placa de expansão** e do **filamento PLA** (Tabela 2) — com eles
      dá para fechar o total (hoje: subtotal de R$ 235,04 dos itens com valor informado)
- [ ] **PCI (3.7):** software e método de fabricação
- [ ] **Repouso noturno** observado no protótipo? (Tabela 3)
- [ ] **Correções P10/P14 no protótipo:** gravar o `main.c` atual e testar (Tabela 3)
- [ ] **Teste com lanterna (4.6):** o painel girou para o lado contrário — repetir iluminando um lado
      de cada vez e anotar qual eixo se move e para onde; com isso escolhemos a correção
      (sinal do eixo no `main.c`, divisor invertido, LDRs trocados ou P10)
- [ ] Confirmar **Campus Sorocaba**
- [ ] Confirmar se os divisores dos LDRs estão no **3V3** do ESP32 (entradas não toleram 5 V)

## Preenchido na v4

Orientador (Prof. Marcelo Bellodi) · custos de servos, XL4015, bateria e painel · XL4015 ajustado de
12 V para 6 V · peça do suporte da placa quebrou no encaixe dos braços e foi reimpressa mais
resistente · teste com lanterna (sentido invertido).

## Para a apresentação oral

Roteiro sugerido: problema (cosseno) → solução (rastreador + torre) → montagem e testes físicos →
simulador com o mesmo código (página do celular dentro dele) → **a história dos erros** (P10, testes
contaminados, sombra do painel, peça quebrada, regressões do ESP32, lanterna) → próximos passos.
