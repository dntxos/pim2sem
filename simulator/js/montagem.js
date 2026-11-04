// Dados da montagem mecânica, extraídos dos STLs em 3d_material/stl/.
// Os STLs foram exportados do SolidWorks já nas coordenadas da montagem (mm, eixo Y para cima),
// então basta agrupá-los pelo que gira com cada servo.

export const PASTA_STL = '../3d_material/stl/';
const PREFIXO = 'MONTAGEM_SISTEMA_SOLAR_UNIP - ';

// Grupo: 'fixo' (base), 'azimute' (gira com o servo horizontal, D9),
//        'elevacao' (inclina com o servo vertical, D10, e também gira com o azimute).
export const PECAS = [
  { arquivo: 'BASE_FECHAMENTO-2', grupo: 'fixo', cor: 0xe4e4e4 },
  { arquivo: 'COLUNA_INTERNA-1', grupo: 'fixo', cor: 0xd0d0d0 },
  { arquivo: 'PAREDE_ESTRUTURAL_01-1', grupo: 'fixo', cor: 0xf2f2f2 },
  { arquivo: 'PAREDE_ESTRUTURAL_01-2', grupo: 'fixo', cor: 0xf2f2f2 },
  { arquivo: 'PAREDE_APOIO_MOTOR_01-1', grupo: 'fixo', cor: 0xf2f2f2 },
  { arquivo: 'PRATO_GIRATORIO-1', grupo: 'azimute', cor: 0xf7f7f7 },
  { arquivo: 'PAREDE_ESTRUTURAL_02-1', grupo: 'azimute', cor: 0xf2f2f2 },
  { arquivo: 'PAREDE_ESTRUTURAL_03-1', grupo: 'azimute', cor: 0xf2f2f2 },
  { arquivo: 'PAREDE_APOIO_MOTOR_02-1', grupo: 'azimute', cor: 0xf2f2f2 },
  { arquivo: 'TRAVE-2', grupo: 'elevacao', cor: 0xe8e8e8 },
  { arquivo: 'SUPORTE_DO_SUPORTE_LDR-1', grupo: 'elevacao', cor: 0x2a2a2a },
  { arquivo: 'SUPORTE_LDR-2', grupo: 'elevacao', cor: 0x1e1e1e },
].map((p) => ({ ...p, url: PASTA_STL + encodeURIComponent(PREFIXO + p.arquivo + '.STL') }));

// Eixo do azimute: vertical, passando pelo centro do prato giratório.
export const EIXO_AZIMUTE = { x: 129.34, z: 132.65 };
// Eixo da elevação: paralelo a Z, passando pelo pino da trave (ajuste de círculo no STL).
export const EIXO_ELEVACAO = { x: 129.34, y: 133.1 };

// Na exportação, a placa está inclinada 56,252° em relação à horizontal (normal apontando para -X).
export const INCLINACAO_EXPORTADA_GRAUS = 56.252;
const t0 = (INCLINACAO_EXPORTADA_GRAUS * Math.PI) / 180;
// Referencial da placa na pose exportada:
//   n = normal da placa (para onde ela "olha"),  u = "para cima" ao longo da placa,  z = lateral.
export const N0 = [-Math.sin(t0), Math.cos(t0), 0];
export const U0 = [Math.cos(t0), Math.sin(t0), 0];

// Coordenadas no referencial da placa: ponto = u*U0 + n*N0 + z*(0,0,1).
function doReferencialDaPlaca(u, n, z) {
  return [u * U0[0] + n * N0[0], u * U0[1] + n * N0[1], z];
}

// Divisor em cruz (SUPORTE_LDR): 30 × 30 mm, centro em u = 327,5 / z = 141,3, base em n ≈ 17.
// Os LDRs ficam no centro de cada quadrante (±7,5 mm), cabeça ~2 mm acima da base.
// "Esquerda" é -Z (vista de frente para a placa, com "cima" = U0).
const CRUZ = { u: 327.55, z: 141.3, nBase: 17.0, meio: 7.5 };
export const LDRS = [
  { id: 'SE', nome: 'Superior esquerdo', du: +1, dz: -1 },
  { id: 'SD', nome: 'Superior direito', du: +1, dz: +1 },
  { id: 'IE', nome: 'Inferior esquerdo', du: -1, dz: -1 },
  { id: 'ID', nome: 'Inferior direito', du: -1, dz: +1 },
].map((l) => ({
  ...l,
  posicao: doReferencialDaPlaca(CRUZ.u + l.du * CRUZ.meio, CRUZ.nBase + 2, CRUZ.z + l.dz * CRUZ.meio),
}));
export const RAIO_LDR = 2.5;

// Placa fotovoltaica: não existe nos STLs; dimensões (280 × 250 mm) vêm do AMF.
// Assentada sobre a face superior da trave (n = 29,3), centrada nela.
export const PLACA = {
  centro: doReferencialDaPlaca(179.8, 29.3 + 1.5, 140.2),
  largura: 280, // ao longo de Z
  altura: 250, // ao longo de U0
  espessura: 3,
};
