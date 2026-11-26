---
name: relatorio-pim
description: Redigir e gerar o relatório do PIM II (UNIP, Automação Industrial) da torre solar com rastreador — texto acadêmico em ABNT/UNIP, figuras (renders 3D do Blender, simulador, gráficos, diagramas, PCI) e o .docx final. Use quando pedirem o relatório, uma seção dele, revisão de formatação ABNT, referências, resumo/abstract, figuras para o trabalho ou material para a apresentação.
---

# Relatório do PIM II — atue como especialista em relatórios técnicos acadêmicos

Antes de escrever, leia **sempre**:
1. `references/roteiro-pim2.md` — tema oficial, exigências do guia do curso e sumário proposto.
2. `references/normas-unip-abnt.md` — formatação e citação conforme o guia da biblioteca UNIP 2025.
3. `docs/specs/` e `main.c` — fonte de verdade técnica (ESP32, MG996R, XL4015, bateria 12 V, painel 10 W).
4. `docs/relatorio/PENDENCIAS.md` — roteiro da v5 (final): o que muda da v4 e como ficam os antigos
   `[PREENCHER]`. **Projeto concluído: a v5 não tem marcadores amarelos.**
5. `docs/specs/07-conclusao.md` — conclusão oficial: rastreador +47% (simulação), mas 2 placas fixas
   Leste/Oeste +82% e mais baratas; consulta a fornecedores de postes solares profissionais.

## Regras inegociáveis

- **Nunca inventar medições, resultados, nomes, RAs, orientador ou valores pagos.** Faltou dado →
  marcador visível `[PREENCHER: …]` em amarelo e item na lista de pendências para o grupo.
- Resultado do simulador é **simulação** (dizer isso no texto e na legenda); teste físico não
  realizado é **planejado**.
- Referências **reais e verificáveis** (livros técnicos Érica/LTC/Pearson/Bookman, normas ABNT,
  datasheets oficiais, artigos com DOI, ANEEL/EPE/INPE). Conferir cada uma (WebSearch) antes de
  citar; toda citação no texto tem referência e vice-versa.
- Hardware real: **ESP32** (migrou do Arduino Nano na etapa de testes físicos), servos **MG996R**,
  4 LDR + 10 kΩ, 2 × **XL4015**, bateria **12 V** Elgin, painel **10 W**. Wi-Fi `SOLAR_TOWER` /
  `torre1234` / `http://192.168.4.1`. Integrantes: ver `INTEGRANTES` em `tools/relatorio/gerar_relatorio.py`.
- **Limite: no máximo 40 páginas no total** (v5 final: 39). Sempre gerar `.pdf` (impressão) e `.low.pdf` (≤ 10 MB, submissão). Conferir após cada mudança com `exportar_pdf.sh`.
- Capturas do simulador também ficam em `docs/imagens_videos_testes_fisicos/` (ex.:
  `ganho_anual_*_correcao_p15.jpeg`): são **simulação**, nunca legendar como teste físico.
- Testes físicos: só o que está em `docs/imagens_videos_testes_fisicos/` ou foi informado pelo grupo
  (painéis de fotos: `tools/relatorio/fotos.py`).
- Português formal, impessoal, termos estrangeiros em itálico, siglas por extenso na 1ª ocorrência.

## Figuras — o relatório deve "encher os olhos"

Gerar em `docs/relatorio/figuras/` (PNG ≥ 2000 px de largura, 300 dpi no .docx):

| Figura | Como gerar |
|--------|-----------|
| Renders fotorrealistas da estrutura (herói, frente, lateral, topo, detalhe dos LDRs) | `blender -b -P tools/render/render_blender.py -- --cam <vista> --h <°> --v <°> --sol-az <°> --sol-el <°> --res 2400 --amostras 256 --out …` (Blender 5.x, Cycles/Metal; ~2–5 min cada). Usar poses reais vindas do simulador (ex.: dia 172, 10 h → H≈108, V≈132). |
| Sequência "seguindo o sol" (manhã / meio-dia / tarde) | 3 renders com sol e pose do simulador na mesma hora — montar lado a lado |
| Capturas do simulador 3D | skill `simulador-3d` + screenshot do navegador |
| Gráficos (convergência, erro × tempo, energia fixa × rastreador ao longo do dia, curva do LDR, cos θ) | dados do simulador (`sim.estado.amostras`, energia) + matplotlib, estilo limpo, fonte serifada |
| Diagrama de blocos do sistema / fluxograma do firmware | SVG/Graphviz ou matplotlib, cores sóbrias, legível em P&B |
| Esquemático elétrico e PCI | desenhar (ex.: KiCad se instalado, ou esquemático vetorial); PCI é exigência do guia |
| Circuito Tinkercad | `docs/diagrama_tinkercad.png` |

Opcional: imagens geradas por IA **só como ilustração conceitual de aplicação** (ex.: torre numa
praça), sempre rotuladas "Ilustração conceitual gerada por IA" — nunca como foto do protótipo.

## Geração do documento

- Formato de entrega: **.docx** (o curso usa Word) gerado via skill `docx` ou python-docx, com
  estilos reais (Título 1/2/3) para o sumário automático, Times New Roman 12, margens 3/3/2/2,
  1,5 entrelinhas, numeração a partir da Introdução, legendas "Figura N –" em cima e "Fonte:" embaixo.
- Pipeline: `capturar_ihm.mjs` / `graficos.py` / `diagramas.py` / `fotos.py` → `gerar_relatorio.py` (v8;
  rodar com `uv run --with python-docx python …`) → `exportar_pdf.sh PIM_Torre_Solar_v8` (Word atualiza sumário/listas e exporta o PDF). Os números do
  texto são lidos de `docs/relatorio/dados/` — gere dados novos pelo simulador (`sim.traco`/`sim.salvar`).
- **Sempre dois PDFs:** `PIM_Torre_Solar_vN.pdf` (alta resolução, para imprimir/encadernar) e
  `PIM_Torre_Solar_vN.low.pdf` (≤ 10 MB, para submeter na plataforma). O `exportar_pdf.sh` já gera
  o `.low.pdf` via `reduzir_pdf.py` (reamostra só as imagens; texto segue vetorial). Entregar os dois.
- Salvar em `docs/relatorio/` (`PIM_Torre_Solar_vN.docx`) + exportar PDF para conferência visual;
  revisar as páginas renderizadas antes de entregar (quebras, figuras cortadas, órfãs).
- Entregar junto um `docs/relatorio/PENDENCIAS.md` com tudo que o grupo precisa preencher/medir.
