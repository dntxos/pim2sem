# Relatório — versão 5 (final): sem pendências

O projeto está concluído (24/11/2026): protótipo montado, `main.c` final, conclusão definida.
A v5 é a versão final, **sem marcadores `[PREENCHER]`**. Gerar com `gerar_relatorio.py` →
`exportar_pdf.sh PIM_Torre_Solar_v5` (sai `.pdf` para impressão e `.low.pdf` ≤ 10 MB para
submissão). Limite: 40 páginas.

## O que muda da v4 para a v5

| Seção / item | Conteúdo da v5 | Fonte |
|--------------|----------------|-------|
| Hardware e ligações | LDRs no 3,3 V do ESP32 e GND; servos em fonte regulada de 6 V; GND comum; GPIO 34/35/32/33 e 18/19 (confirmado pelo grupo) | `docs/specs/02-hardware.md` |
| IHM | Nova IHM (identidade UNIP, 4 LDRs, diferença entre lados, medidores, período dia/noite, gráfico 60 s, setas) — figura capturada do simulador | `docs/specs/03-firmware.md` |
| Repouso noturno | Estaciona em **90°/90°** (era 20°/90°); "Posição inicial" leva ao centro | `main.c`, `03-firmware.md` |
| Simulação do ano | Novo recurso do simulador; ganho anual e erro médio | `05-testes.md`, `dados/ano_p15.json` |
| História de erros e acertos | **P15**: preso em H = 20° nas manhãs de inverno, achado pela simulação do ano; +34,5% → +47,1% (erro 27,7° → 16,9°) | `06-problemas-conhecidos.md` |
| Figuras do P15 | `docs/imagens_videos_testes_fisicos/ganho_anual_{antes,depois}_da_correcao_p15.jpeg` — legenda: **simulação**; números de uma rodada (+38% → +49%), citar a faixa no texto | — |
| **Conclusão** | Consulta a fornecedores de postes solares profissionais + comparação placas fixas × rastreador: rastreador +47%, **2 placas fixas Leste/Oeste +82%** por R$ 39,24 contra R$ 94,10 só nos extras do rastreador → recomendação: placas fixas | `docs/specs/07-conclusao.md`, `dados/conclusao_fixas_vs_rastreador.json` |
| Material complementar | Vídeos `docs/video/demo_ihm.mp4` e `demo_simulador.mp4` | — |

## Itens que eram `[PREENCHER]` na v4 — como ficam

| Item da v4 | Texto da v5 |
|------------|-------------|
| PCI (3.7): software e fabricação | Apresentada como **proposta de leiaute** da placa, desenhada pelo grupo em ferramenta vetorial (script Python) |
| Custos: ESP32 + placa de expansão e filamento PLA | Linhas retiradas; nota na fonte da tabela: "não inclui o ESP32 com placa de expansão e o filamento PLA" — total = itens com valor pago |
| Resultados: repouso noturno e P10/P14 no protótipo | "Validado em simulação" (P10, P14 e P15 aplicados ao `main.c` final); protótipo montado com as ligações confirmadas |
| Teste com lanterna | Resultado registrado (girou ao contrário, firmware anterior às correções) + causas e roteiro de diagnóstico pela IHM |
| 3V3 dos LDRs, campus | Confirmado (3V3) · Campus Sorocaba (como na v4) |

## Para a apresentação oral

Roteiro: problema (cosseno) → solução (rastreador + torre) → montagem e testes físicos → IHM no
celular (`demo_ihm.mp4`) → simulador com o mesmo código e o ano inteiro (`demo_simulador.mp4`) →
**a história dos erros** (P10, testes contaminados, sombra do painel, peça quebrada, regressões do
ESP32, lanterna, P15) → **conclusão: o rastreador funciona, mas duas placas fixas Leste/Oeste
compensam mais** (consulta ao mercado + números).
