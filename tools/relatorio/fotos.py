"""Monta os painéis de fotos dos testes físicos a partir de docs/imagens_videos_testes_fisicos/.

Extrai quadros dos vídeos (ffmpeg) nos instantes escolhidos e monta painéis rotulados (a), (b), (c).
Uso: python tools/relatorio/fotos.py   (requer ffmpeg e Pillow)
"""
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MIDIA = os.path.join(RAIZ, 'docs', 'imagens_videos_testes_fisicos')
FIG = os.path.join(RAIZ, 'docs', 'relatorio', 'figuras')
TMP = tempfile.mkdtemp()

# (arquivo, instante em s) — None = foto
PAINEIS = {
    'f_fabricacao.png': [('algumas_peças_impressas.jpeg', None), ('pre_montado_1.jpeg', None)],
    'f_teste_servos.png': [('pre_montagem_testando_servo_motores.mp4', 5), ('pre_montagem_testando_servo_motores.mp4', 13),
                           ('pre_montagem_testando_servo_motores.mp4', 26)],
    'f_quebra.png': [('problema_peça_impressa_quebrou_na_montagem.mp4', 19), ('problema_peça_impressa_quebrou_na_montagem.mp4', 22.5),
                     ('problema_peça_impressa_quebrou_na_montagem.mp4', 36)],
    'f_esp32.png': [('mudança_para_esp32.mp4', 2), ('mudança_para_esp32.mp4', 22), ('mudança_para_esp32.mp4', 12.5)],
    'f_celular.png': [('screenshot_interface_no_celular.jpeg', None), ('testando_pela_interface_no_celular.mp4', 25)],
    'f_versao_final.png': [('versao_final_adesivado.jpeg', None), ('video_versao_final_funcionando.mp4', 9),
                           ('video_versao_final_funcionando.mp4', 19), ('video_versao_final_funcionando.mp4', 31)],
    'f_p15.png': [('ganho_anual_antes_da_correcao_p15.jpeg', None), ('ganho_anual_depois_da_correcao_p15.jpeg', None)],
}


def ihm():
    """Painel da IHM final: captura de tools/relatorio/capturar_ihm.mjs dividida em duas colunas."""
    im = Image.open(os.path.join(FIG, 'ihm_captura.png')).convert('RGB')
    k = im.width / 390  # px por pixel CSS
    cortes = [(0, 905), (905, 1580)]
    partes = [im.crop((0, int(a * k), im.width, int(b * k))) for a, b in cortes]
    alt = max(p.height for p in partes)
    caminhos = []
    for i, p in enumerate(partes):
        topo = int(alt * 0.06)  # faixa para o rótulo (a)/(b) não cobrir a página
        tela = Image.new('RGB', (p.width, alt + topo), (238, 241, 246))
        tela.paste(p, (0, topo))
        c = os.path.join(TMP, f'ihm_{i}.png'); tela.save(c); caminhos.append(c)
    painel('f_ihm.png', [(c, None) for c in caminhos], altura=1600)


def fonte(tam):
    for f in ('/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf', '/Library/Fonts/Times New Roman Bold.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def abrir(arquivo, t):
    caminho = arquivo if os.path.isabs(arquivo) else os.path.join(MIDIA, arquivo)
    if t is None:
        return Image.open(caminho).convert('RGB')
    saida = os.path.join(TMP, f'{abs(hash((arquivo, t)))}.jpg')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', caminho, '-frames:v', '1', '-q:v', '2', saida], check=True)
    return Image.open(saida).convert('RGB')


def painel(nome, itens, altura=1100, espaco=24):
    ims = [abrir(a, t) for a, t in itens]
    ims = [i.resize((int(i.width * altura / i.height), altura), Image.LANCZOS) for i in ims]
    largura = sum(i.width for i in ims) + espaco * (len(ims) - 1)
    tela = Image.new('RGB', (largura, altura), 'white')
    d = ImageDraw.Draw(tela)
    f = fonte(int(altura * 0.055))
    x = 0
    for k, im in enumerate(ims):
        tela.paste(im, (x, 0))
        rot = f'({chr(97 + k)})'
        caixa = d.textbbox((0, 0), rot, font=f)
        w, h = caixa[2] - caixa[0], caixa[3] - caixa[1]
        d.rectangle([x + 14, 14, x + 14 + w + 22, 14 + h + 26], fill='white')
        d.text((x + 25, 18), rot, fill='black', font=f)
        x += im.width + espaco
    tela.save(os.path.join(FIG, nome), dpi=(300, 300))
    print('ok', nome, tela.size)


if __name__ == '__main__':
    for nome, itens in PAINEIS.items():
        painel(nome, itens)
    ihm()
