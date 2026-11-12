#!/usr/bin/env python3
"""Gera a versão reduzida do PDF (NOME.low.pdf) para submissão em plataformas com limite de tamanho.

O PDF original (alta resolução) fica para impressão/encadernação. Aqui só as imagens são
reamostradas e recomprimidas em JPEG — texto, tabelas e fontes continuam vetoriais.
Tenta a melhor qualidade primeiro e reduz até caber no limite (padrão: 9,5 MB, margem
para o limite de 10 MB da plataforma).

Uso: python3 tools/relatorio/reduzir_pdf.py docs/relatorio/PIM_Torre_Solar_v4.pdf [limite_mb]
Requer PyMuPDF (pip install pymupdf).
"""
import os
import sys

import pymupdf

# (dpi das imagens, qualidade JPEG) — da melhor para a mais agressiva
NIVEIS = [(200, 85), (150, 80), (120, 70), (96, 60)]


def reduzir(origem: str, limite_mb: float = 9.5) -> str:
    destino = origem[:-4] + ".low.pdf"
    for dpi, qualidade in NIVEIS:
        doc = pymupdf.open(origem)
        doc.rewrite_images(dpi_threshold=dpi + 10, dpi_target=dpi, quality=qualidade)
        doc.ez_save(destino, garbage=4, deflate=True)
        doc.close()
        mb = os.path.getsize(destino) / 1e6
        if mb <= limite_mb:
            print(f"OK {destino} ({mb:.1f} MB; imagens a {dpi} dpi, JPEG {qualidade})")
            return destino
    sys.exit(f"ERRO: {destino} ficou com {mb:.1f} MB, acima de {limite_mb} MB mesmo no nível mais agressivo")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    reduzir(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 9.5)
