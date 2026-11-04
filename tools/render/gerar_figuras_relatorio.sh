#!/usr/bin/env bash
# Gera os renders do relatório com poses obtidas no simulador (21/jun, lat -23,55, variante elevacaoLdr=25).
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT=docs/relatorio/figuras
R="blender -b -P tools/render/render_blender.py --"
Q="--res ${RES:-2200} --amostras ${AMOSTRAS:-160}"
$R --cam heroi       --h 126 --v 144 --sol-az 34  --sol-el 35 $Q --out $OUT/render_heroi.png
$R --cam heroi       --h 108 --v 144 --sol-az 0   --sol-el 43 $Q --out $OUT/render_seq_12h.png
$R --cam heroi       --h 72  --v 144 --sol-az 326 --sol-el 35 $Q --out $OUT/render_seq_14h.png
$R --cam lateral     --h 108 --v 144 --sol-az 0   --sol-el 43 $Q --out $OUT/render_lateral.png
$R --cam detalhe_ldr --h 126 --v 144 --sol-az 34  --sol-el 35 $Q --out $OUT/render_detalhe_ldr.png
$R --cam frente      --h 90  --v 90  --sol-az 20  --sol-el 50 $Q --out $OUT/render_pose_inicial.png
echo FIM
