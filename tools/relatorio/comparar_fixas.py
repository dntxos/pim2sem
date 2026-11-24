#!/usr/bin/env python3
"""Compara, no ano, o rastreador com placas fixas (1 voltada ao Norte; 2 em Leste/Oeste).

Usa o MESMO modelo do simulador (simulator/js/sol.js: posição solar simplificada, céu limpo, só luz
direta, energia ∝ cos do ângulo de incidência) e o ganho do rastreador medido no simulador com o
main.c final (docs/relatorio/dados/ano_p15.json, variante INICIO_H=90). Custos: notas de compra do
grupo (docs/specs/02-hardware.md e Tabela de custos do relatório).

Saída: docs/relatorio/dados/conclusao_fixas_vs_rastreador.json
Uso: python3 tools/relatorio/comparar_fixas.py
"""
import json
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "docs/relatorio/dados"
G = math.pi / 180
LAT = -23.55          # São Paulo (mesma do simulador)
INCL_LO = 20          # inclinação das placas Leste/Oeste (°)
DIAS = list(range(1, 366, 15))  # mesma amostragem da simulação do ano

# Preços pagos pelo grupo (R$)
PAINEL_10W = 39.24
EXTRAS_RASTREADOR = {"2 servos MG996R": 73.60, "XL4015 dos servos": 18.50, "4 LDR": 1.80, "4 resistores 10 kΩ": 0.20}


def sol(dia, hora):
    dec = -23.44 * G * math.cos(2 * math.pi / 365 * (dia + 10))
    h = (hora - 12) * 15 * G
    lat = LAT * G
    el = math.asin(math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(h))
    az = math.atan2(-math.cos(dec) * math.sin(h), math.sin(dec) * math.cos(lat) - math.cos(dec) * math.sin(lat) * math.cos(h))
    return az, el


def normal(azimute, inclinacao):  # (Norte, Leste, Cima)
    a, t = azimute * G, inclinacao * G
    return (math.sin(t) * math.cos(a), math.sin(t) * math.sin(a), math.cos(t))


def energia_dia(dia, normais, dt=1 / 60):
    e = [0.0] * len(normais)
    hora = 0.0
    while hora < 24:
        az, el = sol(dia, hora + dt / 2)
        if el > 0:
            s = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
            for i, n in enumerate(normais):
                e[i] += max(0.0, sum(a * b for a, b in zip(n, s))) * dt
        hora += dt
    return e


def main():
    ano = json.loads((DADOS / "ano_p15.json").read_text())
    porDia = ano["variantes"]["INICIO_H=90 (aplicada)"]["porDia"].split()
    ganho = {int(x.split("/")[0]): int(x.split("/")[2]) / 100 for x in porDia}

    norte, leste, oeste = normal(0, abs(LAT)), normal(90, INCL_LO), normal(270, INCL_LO)
    tot = {"fixa_norte": 0.0, "leste": 0.0, "oeste": 0.0, "rastreador": 0.0}
    for d in DIAS:
        f, l, o = energia_dia(d, [norte, leste, oeste])
        tot["fixa_norte"] += f
        tot["leste"] += l
        tot["oeste"] += o
        tot["rastreador"] += f * (1 + ganho[d])
    base = tot["fixa_norte"]
    lo = tot["leste"] + tot["oeste"]
    extras = sum(EXTRAS_RASTREADOR.values())
    saida = {
        "descricao": "Energia relativa no ano (horas-equivalentes de sol pleno), modelo do simulador "
                     "(céu limpo, só luz direta), lat -23,55, amostragem a cada 15 dias.",
        "energia_relativa_ano": {k: round(v * 15) for k, v in tot.items()},
        "ganho_sobre_1_placa_fixa_pct": {
            "rastreador (1 placa, main.c final)": round((tot["rastreador"] / base - 1) * 100),
            f"2 placas fixas Leste/Oeste ({INCL_LO}°)": round((lo / base - 1) * 100),
            "2 placas fixas ao Norte": 100,
        },
        "duas_LO_vs_rastreador_pct": round((lo / tot["rastreador"] - 1) * 100),
        "custos_R$": {
            "painel 10 W adicional": PAINEL_10W,
            "itens extras do rastreador (sem ESP32, estrutura e manutenção)": round(extras, 2),
            "itens extras detalhados": EXTRAS_RASTREADOR,
        },
    }
    (DADOS / "conclusao_fixas_vs_rastreador.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1))
    print(json.dumps(saida, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
