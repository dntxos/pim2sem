#!/usr/bin/env python3
"""Estima o filamento gasto nas peças impressas a partir dos STLs (o grupo não anotou o consumo).

Modelo de fatiador simplificado, com as recomendações de docs/specs/04-mecanica.md:
  massa = densidade × [casca + preenchimento × (volume − casca)]
  casca = área da superfície × 1,2 mm (3 perímetros de 0,4 mm; topo/fundo equivalentes),
          limitada ao volume da peça
  preenchimento: 25% (prato giratório e trave: 40%, recebem o eixo do servo)
  + 10% de perdas (saia, suportes, purga)
  + reimpressão da peça que quebrou na montagem (a trave que segura a placa).
Preço: rolo de PLA de 1 kg, 1,75 mm, R$ 80,00 (informado pelo grupo).

Saída: docs/relatorio/dados/filamento.json
Uso: python3 tools/relatorio/estimar_filamento.py
"""
import json
import struct
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
STL = RAIZ / "3d_material/stl"
DENSIDADE = 1.24        # g/cm³ (PLA)
PAREDE_MM = 1.2
INFILL = 0.25
INFILL_EIXO = 0.40
PERDAS = 0.10
PRECO_KG = 80.00
REIMPRESSA = "TRAVE-2"  # peça do suporte da placa que quebrou no encaixe dos braços


def ler_stl(caminho):
    dados = caminho.read_bytes()
    n = struct.unpack_from("<I", dados, 80)[0]
    if 84 + n * 50 != len(dados):
        raise ValueError(f"{caminho.name}: STL ASCII não suportado")
    vol = area = 0.0
    for i in range(n):
        v = struct.unpack_from("<12f", dados, 84 + i * 50)
        a, b, c = v[3:6], v[6:9], v[9:12]
        # volume com sinal (tetraedro com a origem) e área do triângulo
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
        u = [b[k] - a[k] for k in range(3)]
        w = [c[k] - a[k] for k in range(3)]
        cx = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
        area += (cx[0] ** 2 + cx[1] ** 2 + cx[2] ** 2) ** 0.5 / 2
    return abs(vol), area  # mm³, mm²


def main():
    pecas = []
    for f in sorted(STL.glob("*.STL")):
        nome = f.stem.split(" - ")[-1]
        vol, area = ler_stl(f)
        casca = min(vol, area * PAREDE_MM)
        infill = INFILL_EIXO if ("PRATO" in nome or "TRAVE" in nome) else INFILL
        massa = DENSIDADE * (casca + infill * (vol - casca)) / 1000  # g
        copias = 2 if nome == REIMPRESSA else 1
        pecas.append({"peca": nome, "volume_cm3": round(vol / 1000, 1), "massa_g": round(massa, 1), "impressoes": copias})
    impresso = sum(p["massa_g"] * p["impressoes"] for p in pecas)
    total = impresso * (1 + PERDAS)
    saida = {
        "metodo": __doc__.strip().splitlines()[0] + " Ver cabeçalho de tools/relatorio/estimar_filamento.py.",
        "pecas": pecas,
        "massa_pecas_g": round(impresso),
        "massa_com_perdas_g": round(total),
        "preco_rolo_1kg": PRECO_KG,
        "custo_R$": round(total / 1000 * PRECO_KG, 2),
    }
    (RAIZ / "docs/relatorio/dados/filamento.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1))
    print(json.dumps(saida, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
