# 04 — Mecânica (peças 3D)

## Arquivos

| Caminho | Conteúdo |
|---------|----------|
| `3d_material/amf/MONTAGEM_SISTEMA_SOLAR_UNIP.AMF` | Montagem completa (≈ 11 MB) — referência de encaixe. |
| `3d_material/stl/*.STL` | Peças individuais, prontas para fatiar e imprimir. |

## Peças

| Peça (STL) | Função provável |
|------------|-----------------|
| `BASE_FECHAMENTO-2` | Base/tampa inferior da caixa. |
| `PAREDE_ESTRUTURAL_01-1`, `PAREDE_ESTRUTURAL_01-2` | Paredes laterais da caixa (2×). |
| `PAREDE_ESTRUTURAL_02-1` | Parede estrutural (provavelmente com recortes para cabos/USB). |
| `PAREDE_ESTRUTURAL_03-1` | Parede estrutural menor. |
| `COLUNA_INTERNA-1` | Coluna central que sustenta o conjunto giratório. |
| `PRATO_GIRATORIO-1` | Prato do eixo horizontal (azimute), acoplado ao servo de D9. |
| `PAREDE_APOIO_MOTOR_01-1`, `PAREDE_APOIO_MOTOR_02-1` | Suportes do servo do eixo vertical sobre o prato. |
| `TRAVE-2` | Trave/eixo que inclina a placa (elevação), acoplada ao servo de D10. |
| `SUPORTE_LDR-2` | Cruz/anteparo que separa os 4 LDRs (cria sombra diferencial). |
| `SUPORTE_DO_SUPORTE_LDR-1` | Fixação do suporte dos LDRs na placa/trave. |

> As funções acima foram inferidas pelos nomes dos arquivos — confirmar com o modelo CAD original.
> Os sufixos `-1`/`-2` vêm da exportação da montagem (instância da peça), não indicam quantidade.

## Recomendações de impressão (FDM)

- Material: PLA (protótipo interno) ou PETG (exposição ao sol — PLA amolece ~55 °C).
- Camada 0,2 mm, 3 perímetros, preenchimento 20–30 %.
- Peças que recebem o eixo do servo (prato, trave): preenchimento ≥ 40 % e testar o encaixe do
  *horn* antes de imprimir a versão final.
- O anteparo dos LDRs deve ser **opaco** (filamento escuro) para a sombra funcionar.

## Montagem (ordem sugerida)

1. Base + paredes estruturais formando a caixa; Arduino e protoboard dentro.
2. Servo horizontal fixado na coluna interna; prato giratório no *horn*.
3. Paredes de apoio do motor sobre o prato; servo vertical entre elas.
4. Trave no *horn* do servo vertical; placa fotovoltaica sobre a trave.
5. Suporte dos LDRs no centro/borda da placa, com os sensores alinhados ao plano da placa.
6. Antes de fixar os *horns*, posicionar os servos em 90° (rodar o firmware) para centralizar.
