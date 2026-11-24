# Pendências do relatório — preparação da versão 5

Última versão gerada: `PIM_Torre_Solar_v4` (37 páginas; limite 40). Toda versão sai em dois PDFs:
`.pdf` (alta resolução, impressão) e `.low.pdf` (≤ 10 MB, submissão).

## O que entra na v5 (já disponível no repositório)

- **Montagem elétrica confirmada pelo grupo:** LDRs no 3,3 V do ESP32 e GND; servos numa fonte
  externa regulada de 6 V (XL4015 #1); GND da fonte dos servos ligado ao GND do ESP32; pinos
  LDR SE/SD/IE/ID = GPIO 34/35/32/33, servos H/V = GPIO 18/19 (`docs/specs/02-hardware.md`).
- **Nova IHM do celular** (identidade UNIP, 4 LDRs com barras, diferença entre lados com zona morta,
  medidores dos servos, período dia/noite com contagem, tempo ligado, gráfico de 60 s, setas com
  repetição) — `docs/specs/03-firmware.md`, seção IHM. Captura: gerar no simulador (painel 📱).
- **Simulação do ano inteiro** no simulador (seção 📅) — `docs/specs/05-testes.md`.
- **P15 — novo erro encontrado e corrigido** (`INICIO_H = 90`): no inverno o painel acordava preso em
  H = 20° até ~meio-dia. Ganho anual sobre a placa fixa: **+34,5% → +47,1%**; erro médio
  **27,7° → 16,9°** (`docs/relatorio/dados/ano_p15.json`, tabela em `docs/specs/06-problemas-conhecidos.md`).
  Entra na história de "erros e acertos" (achado pela simulação do ano, depois da IHM).
- **Figuras do P15** (capturas do simulador — legendar como **simulação**):
  `docs/imagens_videos_testes_fisicos/ganho_anual_antes_da_correcao_p15.jpeg` (+38%, erro 27,5°) e
  `..._depois_da_correcao_p15.jpeg` (+49%, erro 16,5°). Os números das capturas são de uma rodada
  e diferem ~2–3 p.p. da tabela (ruído simulado nos LDRs): no texto, citar a faixa
  (antes +35% a +38%; depois +47% a +49%) ou explicar a diferença na legenda.
- **Vídeos de demonstração** (`docs/video/demo_ihm.mp4`, `demo_simulador.mp4`) — citar como
  material complementar; podem dar quadros para figuras.
- Texto a revisar na v4: repouso noturno agora em **90°/90°** (era 20°/90°); botão "Posição
  inicial" leva ao centro; P4 resolvido; pendência do 3V3 encerrada.

## Ainda depende do grupo

- [ ] **Custos:** valor do **ESP32 + placa de expansão** e do **filamento PLA** (Tabela 2) — hoje
      subtotal de R$ 235,04 dos itens com valor informado
- [ ] **PCI (3.7):** software e método de fabricação
- [ ] **Teste com lanterna (4.6):** repetir iluminando um lado de cada vez, agora olhando os
      indicadores de diferença da IHM (ver F-03 em `docs/specs/05-testes.md`)
- [ ] **Gravar o `main.c` atual no protótipo** e conferir: repouso noturno (F-09), manhã após o
      repouso (F-10, P15), IHM (F-08) — validação física de P10/P14/P15
- [ ] Confirmar **Campus Sorocaba**
- [ ] Fonte do **ESP32**: continua no XL4015 #2 em 6 V pela placa de expansão?

## Encerrado

Orientador (Prof. Marcelo Bellodi) · custos de servos, XL4015, bateria e painel · XL4015 ajustado de
12 V para 6 V · peça do suporte reimpressa · teste com lanterna registrado · **LDRs no 3V3
confirmado** · **pinos e alimentação confirmados** (24/11/2026).

## Para a apresentação oral

Roteiro sugerido: problema (cosseno) → solução (rastreador + torre) → montagem e testes físicos →
IHM no celular (vídeo `demo_ihm.mp4`) → simulador com o mesmo código e o ano inteiro (vídeo
`demo_simulador.mp4`) → **a história dos erros** (P10, testes contaminados, sombra do painel, peça
quebrada, regressões do ESP32, lanterna, P15 achado pela simulação do ano) → próximos passos.
