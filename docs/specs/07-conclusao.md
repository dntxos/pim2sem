# 07 — Conclusão do projeto

> Estado final (24/11/2026): protótipo montado com o ESP32 (ligações e alimentação em
> [02-hardware.md](02-hardware.md)), `main.c` final com as correções P10, P14 e P15, IHM pelo celular
> e simulador 3D rodando o mesmo código. Não há pendências abertas; o que segue em
> [06-problemas-conhecidos.md](06-problemas-conhecidos.md) são melhorias possíveis, não requisitos.

## O que o projeto entregou

| Entrega | Resultado |
|---------|-----------|
| Rastreador de dois eixos (4 LDR + 2 MG996R + ESP32) | Montado (ligações e alimentação confirmadas pelo grupo); controle em malha fechada com zona morta |
| Repouso noturno | Estaciona em 90°/90° com pouca luz e retoma de manhã (P7, P15; verificado no simulador) |
| IHM pelo celular | Rede `SOLAR_TOWER`, `http://192.168.4.1`: modo, dia/noite, 4 LDRs, servos, gráfico, controle manual |
| Simulador 3D | Mesmo `main.c` em WebAssembly sobre as peças reais; dia, ano inteiro e testes de falha |
| Correções achadas pela simulação | P10 (sentido horizontal), P14 (tolerância de 12 bits), P15 (preso no limite no inverno); P13 (sombra do painel nos LDRs) com correção mecânica proposta |
| Testes físicos | Fabricação, servos, quebra e reimpressão da peça, ajuste do XL4015 (12 V → 6 V), IHM no celular e teste com lanterna (girou para o lado contrário — causas e diagnóstico em [05-testes.md](05-testes.md), F-03) |

## Ganho de energia do rastreador (simulação)

Ano inteiro no simulador, `main.c` final, São Paulo (−23,55°), céu limpo, só luz direta, suporte dos
LDRs elevado 25 mm: **+47% a +49%** de energia sobre uma placa fixa voltada ao Norte e inclinada na
latitude; erro médio de apontamento ~17° (antes do P15: +35% a +38%, ~28°). Dados:
`docs/relatorio/dados/ano_p15.json`.

## Comparação com placas fixas e consulta ao mercado

O grupo consultou empresas que fornecem **postes com energia solar para uso profissional**. A
resposta foi que um rastreador **não compensa em nenhum cenário** desse porte:

1. **O painel ficou barato.** Compensa instalar mais área de painel do que ter motores girando por
   LDR.
2. **Num poste pequeno o rastreador não se paga:** motores, sensores, estrutura reforçada e
   manutenção custam mais do que a energia extra gerada — e, se um motor falha, a produção cai
   (a placa fica parada numa posição qualquer).
3. **Duas placas fixas em ângulos diferentes** — uma voltada ao **Leste** e outra ao **Oeste** —
   custam bem menos, não têm peças móveis e geram do sol da manhã ao fim da tarde por mais de
   **25 anos** sem manutenção mecânica.

Os números do próprio projeto confirmam a resposta (mesmo modelo de sol do simulador;
`tools/relatorio/comparar_fixas.py` → `docs/relatorio/dados/conclusao_fixas_vs_rastreador.json`):

| Configuração | Energia no ano × 1 placa fixa (Norte) | Custo a mais (preços pagos pelo grupo) |
|--------------|----------------------------------------|----------------------------------------|
| 1 placa fixa ao Norte | referência | — |
| **1 placa com rastreador** (`main.c` final) | **+47%** | **R$ 94,10** só em servos, XL4015 dos servos, LDRs e resistores — sem contar ESP32, estrutura reforçada e manutenção |
| **2 placas fixas, Leste e Oeste** (20° de inclinação) | **+82%** (24% a mais que o rastreador) | **R$ 39,24** (um painel de 10 W) + suporte fixo |
| 2 placas fixas ao Norte | +100% | R$ 39,24 + suporte fixo |

Por real investido, a segunda placa fixa rende cerca de **4 vezes mais** energia extra que o
rastreador (+82% por R$ 39,24 contra +47% por R$ 94,10, sem contar o ESP32 e a manutenção). E o
modelo ainda favorece o rastreador: considera céu limpo e só luz direta; com nuvens, a luz difusa
chega de todas as direções e o ganho de apontar o painel diminui.

## Conclusão

O rastreador funciona e foi um ótimo veículo de aprendizado — sensores, controle em malha fechada,
servos, alimentação, firmware, Wi-Fi/IHM, simulação e depuração de erros reais (P10, P14, P15).
**Para a torre solar de carregamento de celulares, porém, a solução recomendada é fixa:** duas placas
voltadas para Leste e Oeste (ou simplesmente mais área de painel), sem peças móveis. O rastreamento
só se justifica em usinas grandes, onde o custo da mecânica é diluído por muitos painéis.

## Trabalhos futuros (opcionais)

- Medir no protótipo a energia real de uma placa fixa × rastreador no mesmo dia (ensaio em
  [05-testes.md](05-testes.md)).
- Medir a carga da bateria na IHM (divisor no ADC1 — ver [02-hardware.md](02-hardware.md)).
- Montar a versão fixa Leste/Oeste da torre e comparar com os números acima.
