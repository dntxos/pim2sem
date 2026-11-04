"""Render fotorrealista da montagem do rastreador solar (Blender 5.x, Cycles).

Uso (da raiz do repositório):
  blender -b -P tools/render/render_blender.py -- \
      --h 108 --v 132 --sol-az 45 --sol-el 30 --cam heroi --out docs/relatorio/figuras/render_heroi.png

Parâmetros:
  --h / --v        ângulos dos servos horizontal (D9) e vertical (D10), como no firmware (20–160)
  --sol-az/--sol-el posição do sol (graus; azimute a partir do Norte, horário)
  --cam            heroi | frente | lateral | topo | detalhe_ldr
  --res            largura em px (altura = 3/4)   --amostras  amostras Cycles

A cinemática é a mesma do simulador (simulator/js/montagem.js): os STLs já estão nas coordenadas
da montagem (mm, Y para cima); as peças são agrupadas em fixo / azimute / elevação.
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Euler, Matrix, Vector

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
STL = os.path.join(RAIZ, '3d_material', 'stl')
PREFIXO = 'MONTAGEM_SISTEMA_SOLAR_UNIP - '

PECAS = [
    ('BASE_FECHAMENTO-2', 'fixo', 'pla_branco'),
    ('COLUNA_INTERNA-1', 'fixo', 'pla_cinza'),
    ('PAREDE_ESTRUTURAL_01-1', 'fixo', 'pla_branco'),
    ('PAREDE_ESTRUTURAL_01-2', 'fixo', 'pla_branco'),
    ('PAREDE_APOIO_MOTOR_01-1', 'fixo', 'pla_branco'),
    ('PRATO_GIRATORIO-1', 'azimute', 'pla_branco'),
    ('PAREDE_ESTRUTURAL_02-1', 'azimute', 'pla_branco'),
    ('PAREDE_ESTRUTURAL_03-1', 'azimute', 'pla_branco'),
    ('PAREDE_APOIO_MOTOR_02-1', 'azimute', 'pla_branco'),
    ('TRAVE-2', 'elevacao', 'pla_cinza'),
    ('SUPORTE_DO_SUPORTE_LDR-1', 'elevacao', 'pla_preto'),
    ('SUPORTE_LDR-2', 'elevacao', 'pla_preto'),
]
EIXO_AZ = (129.34, 132.65)          # (x, z) no referencial dos STLs
EIXO_EL = (129.34, 133.1)           # (x, y)
T0 = math.radians(56.252)           # inclinação da placa na exportação
N0 = Vector((-math.sin(T0), math.cos(T0), 0))
U0 = Vector((math.cos(T0), math.sin(T0), 0))


def args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--h', type=float, default=108)
    p.add_argument('--v', type=float, default=132)
    p.add_argument('--sol-az', type=float, default=40)
    p.add_argument('--sol-el', type=float, default=35)
    p.add_argument('--cam', default='heroi')
    p.add_argument('--res', type=int, default=1800)
    p.add_argument('--amostras', type=int, default=160)
    p.add_argument('--out', default=os.path.join(RAIZ, 'docs', 'relatorio', 'figuras', 'render.png'))
    return p.parse_args(argv)


def ref_placa(u, n, z):
    return u * U0 + n * N0 + Vector((0, 0, z))


# ------------------------------------------------------------------ materiais
def material(nome, cor, rug=0.5, metal=0.0, clearcoat=0.0):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*cor, 1)
    b.inputs['Roughness'].default_value = rug
    b.inputs['Metallic'].default_value = metal
    if clearcoat and 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = clearcoat
    return m


def material_painel():
    m = bpy.data.materials.new('painel')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexBrick')
    tex.offset = 0
    tex.inputs['Color1'].default_value = (0.010, 0.025, 0.09, 1)
    tex.inputs['Color2'].default_value = (0.014, 0.032, 0.11, 1)
    tex.inputs['Mortar'].default_value = (0.75, 0.78, 0.82, 1)
    tex.inputs['Scale'].default_value = 4.0
    tex.inputs['Mortar Size'].default_value = 0.004
    tex.inputs['Brick Width'].default_value = 0.125
    tex.inputs['Row Height'].default_value = 0.125
    coord = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(coord.outputs['UV'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.08
    b.inputs['Metallic'].default_value = 0.35
    if 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = 1.0
    return m


def montar(a):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cena = bpy.context.scene
    mats = {
        'pla_branco': material('pla_branco', (0.82, 0.82, 0.80), 0.55),
        'pla_cinza': material('pla_cinza', (0.45, 0.47, 0.50), 0.5),
        'pla_preto': material('pla_preto', (0.02, 0.02, 0.02), 0.45),
        'servo': material('servo', (0.015, 0.015, 0.018), 0.35),
        'aluminio': material('aluminio', (0.80, 0.81, 0.83), 0.25, 1.0),
        'ldr': material('ldr', (0.55, 0.22, 0.08), 0.3, 0.0, 1.0),
        'chao': material('chao', (0.10, 0.12, 0.09), 0.95),
    }

    # raiz: converte Y-para-cima (STL) em Z-para-cima (Blender) e mm -> m
    raiz = bpy.data.objects.new('raiz', None)
    cena.collection.objects.link(raiz)
    raiz.rotation_euler = (math.radians(90), 0, 0)
    raiz.scale = (0.001,) * 3

    def vazio(nome, pai, pos):
        e = bpy.data.objects.new(nome, None)
        cena.collection.objects.link(e)
        e.parent = pai
        e.location = pos
        return e

    az = vazio('azimute', raiz, (EIXO_AZ[0], 0, EIXO_AZ[1]))
    el = vazio('elevacao', az, (0, EIXO_EL[1], 0))
    grupos = {'fixo': (raiz, Vector()), 'azimute': (az, Vector(az.location)),
              'elevacao': (el, Vector(az.location) + Vector(el.location))}

    def anexar(obj, grupo):
        pai, origem = grupos[grupo]
        obj.parent = pai
        obj.data.transform(Matrix.Translation(-origem))

    for arq, grupo, mat in PECAS:
        bpy.ops.wm.stl_import(filepath=os.path.join(STL, PREFIXO + arq + '.STL'))
        o = bpy.context.selected_objects[0]
        o.data.materials.append(mats[mat])
        for p in o.data.polygons:
            p.use_smooth = False
        anexar(o, grupo)

    # painel 10 W (280 x 250 mm, medida do AMF) + moldura
    def caixa(nome, centro, tam, base, mat, grupo):
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.active_object
        o.name = nome
        o.data.transform(Matrix.Diagonal((*tam, 1)))
        o.data.transform(base.to_4x4())
        o.data.transform(Matrix.Translation(centro))
        o.data.materials.append(mat)
        o.parent = None
        anexar(o, grupo)
        return o

    base_placa = Matrix((U0, N0, (0, 0, 1))).transposed()
    c = ref_placa(179.8, 31.0, 140.2)
    caixa('moldura', c, (254, 4, 284), base_placa, mats['aluminio'], 'elevacao')
    painel = caixa('painel', c + N0 * 2.1, (246, 0.5, 276), base_placa, material_painel(), 'elevacao')
    # células: UV de cada face (0–1) x escala 4 -> grade 8 x 8
    painel.data.materials[0].node_tree.nodes['Brick Texture'].inputs['Scale'].default_value = 4.0

    # LDRs nos quadrantes do divisor em cruz
    for du in (-1, 1):
        for dz in (-1, 1):
            p = ref_placa(327.55 + du * 7.5, 19.0, 141.3 + dz * 7.5)
            bpy.ops.mesh.primitive_cylinder_add(radius=2.5, depth=2.2, vertices=32)
            o = bpy.context.active_object
            o.data.transform(Matrix.Rotation(math.radians(90), 4, 'X'))  # eixo ao longo de Y
            rot = Vector((0, 1, 0)).rotation_difference(N0).to_matrix().to_4x4()
            o.data.transform(rot)
            o.data.transform(Matrix.Translation(p))
            o.data.materials.append(mats['ldr'])
            anexar(o, 'elevacao')

    # servos MG996R ilustrativos
    caixa('servo_h', Vector((EIXO_AZ[0], 50.7, EIXO_AZ[1] + 10)), (19.7, 36, 40.7), Matrix.Identity(3), mats['servo'], 'fixo')
    caixa('servo_v', Vector((EIXO_AZ[0], EIXO_EL[1] - 10, EIXO_AZ[1])), (19.7, 40.7, 42.9), Matrix.Identity(3), mats['servo'], 'azimute')

    # pose dos servos (mesma convenção do simulador)
    az.rotation_euler = (0, -math.radians(a.h - 90), 0)
    el.rotation_euler = (0, 0, math.radians((a.v - 90) - 56.252))

    # chão
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0.13, -0.13, 0))
    bpy.context.active_object.data.materials.append(mats['chao'])

    # sol (direção na convenção da cena: Norte = -X, Leste = -Z nos STLs -> +Y no Blender)
    azr, elr = math.radians(a.sol_az), math.radians(a.sol_el)
    d_stl = Vector((-math.cos(elr) * math.cos(azr), math.sin(elr), -math.cos(elr) * math.sin(azr)))
    d = Vector((d_stl.x, -d_stl.z, d_stl.y))
    sol = bpy.data.lights.new('sol', 'SUN')
    sol.energy = 3.2
    sol.angle = math.radians(1.5)
    so = bpy.data.objects.new('sol', sol)
    cena.collection.objects.link(so)
    so.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()

    # céu
    mundo = bpy.data.worlds.new('mundo')
    cena.world = mundo
    mundo.use_nodes = True
    nt = mundo.node_tree
    bg = nt.nodes['Background']
    try:
        sky = nt.nodes.new('ShaderNodeTexSky')
        sky.sun_direction = d
        nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
        bg.inputs['Strength'].default_value = 0.12
        sky.sun_disc = False
    except Exception:
        bg.inputs['Color'].default_value = (0.55, 0.70, 0.95, 1)
        bg.inputs['Strength'].default_value = 0.8

    return cena, d


CAMERAS = {
    # posição (m) relativa ao centro da base, alvo (m)
    'heroi': ((-0.55, 0.42, 0.22), (0.13, -0.13, 0.13)),
    'frente': ((-0.75, -0.13, 0.25), (0.13, -0.13, 0.15)),
    'lateral': ((0.13, 0.62, 0.25), (0.13, -0.13, 0.15)),
    'topo': ((0.13, -0.13, 1.0), (0.13, -0.13, 0.1)),
    'detalhe_ldr': ((-0.12, 0.05, 0.42), (0.13, -0.14, 0.29)),
}


def camera(cena, nome):
    pos, alvo = CAMERAS[nome]
    pos = Vector(pos) + Vector((0.13, -0.13, 0)) * 0  # posições já absolutas
    cam = bpy.data.cameras.new('cam')
    cam.lens = 70 if nome == 'detalhe_ldr' else 50
    cam.dof.use_dof = nome == 'detalhe_ldr'
    co = bpy.data.objects.new('cam', cam)
    cena.collection.objects.link(co)
    co.location = pos
    co.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    if cam.dof.use_dof:
        cam.dof.focus_distance = (Vector(alvo) - Vector(pos)).length
        cam.dof.aperture_fstop = 2.8
    cena.camera = co


def renderizar(cena, a):
    cena.render.engine = 'CYCLES'
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'METAL'
        prefs.get_devices()
        for dev in prefs.devices:
            dev.use = True
        cena.cycles.device = 'GPU'
    except Exception:
        pass
    cena.cycles.samples = a.amostras
    cena.cycles.use_denoising = True
    cena.render.resolution_x = a.res
    cena.render.resolution_y = int(a.res * 3 / 4)
    cena.render.film_transparent = False
    cena.view_settings.view_transform = 'AgX'
    cena.view_settings.look = 'AgX - Medium High Contrast' if 'AgX - Medium High Contrast' in [
        i.identifier for i in cena.view_settings.bl_rna.properties['look'].enum_items] else 'None'
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    cena.render.filepath = a.out
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    a = args()
    cena, _ = montar(a)
    camera(cena, a.cam)
    renderizar(cena, a)
    print('OK', a.out)
