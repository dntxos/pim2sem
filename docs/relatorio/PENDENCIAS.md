# Pendências do relatório — versão 1

Itens marcados em **amarelo** (`[PREENCHER: …]`) no `PIM_Torre_Solar_v1.docx`. Preencher no
`tools/relatorio/gerar_relatorio.py` e regenerar (ou editar direto no Word, se o grupo preferir
trabalhar no .docx a partir daqui).

## Dados do grupo (capa e folha de rosto)

- [ ] Nomes completos e RAs dos 4 integrantes
- [ ] Nome do professor orientador
- [ ] Confirmar **Campus Sorocaba** e o nome do curso ("Curso Superior de Tecnologia em Automação Industrial")

## Dados técnicos a medir/conferir

- [ ] Etiqueta do painel de 10 W: **Vmp, Imp, Voc** (seção 4.3)
- [ ] **Peso e medidas** do painel (seção 4.2 — cálculo de torque; o CAD supõe 280 × 250 mm e ~1 kg)
- [ ] **Capacidade da bateria** em Ah (seção 3.3)
- [ ] Solução de **torre** adotada: tubo de 5″ como no roteiro? Onde ficam bateria e conversores? (seção 4.2)
- [ ] Já existe **controlador de carga, fusível, módulo USB**? Modelos? (seções 4.3, 5.9)
- [ ] Software e método de fabricação da **PCI** (seção 4.8)

## Cronograma e custos

- [ ] Períodos (semanas/datas) de cada etapa da Tabela 1 e situação da impressão 3D
- [ ] Valores pagos: Nano, MG996R, XL4015, bateria, painel, filamento (Tabela 3) — os itens da loja
      de componentes (LDR, resistores, jumpers) já estão preenchidos

## Decisões do grupo

- [ ] **P1 — pinos dos LDRs:** a montagem real usa A0–A3 (diagrama) ou A1–A4 (código)?
- [ ] **P13 — elevar o suporte dos LDRs 25 mm?** Simulação indica que sim (junho: −74% → +33%).
      Confirmar no protótipo com lanterna rasante vinda do lado inferior do painel.
- [ ] **P7 — retorno noturno:** implementar no firmware?

## Testes físicos (Tabela 2) — preencher a coluna "Resultado" quando realizados

F-00 ajuste dos XL4015 · F-01 tensão do painel · F-02 carga da bateria · F-03/F-04 lanterna ·
F-05 torque · F-06 reinícios · F-07/F-08 saídas USB · F-09 sol real.

**Regra:** só registrar resultados realmente obtidos; o que for simulação continua rotulado como simulação.

## Conclusão

- [ ] Atualizar o primeiro parágrafo da Conclusão conforme o andamento real da montagem.

## Para a apresentação oral

As figuras em `docs/relatorio/figuras/` (renders, gráficos, linha do tempo) servem diretamente para os
slides. Sugestão de roteiro: problema (cosseno) → solução (rastreador) → simulador → **a história dos
erros** (P10, testes contaminados, sombra do painel, noite) → resultados → próximos passos.
