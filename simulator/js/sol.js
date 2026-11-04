// Posição aparente do Sol (modelo simplificado, suficiente para o simulador).
// Convenção da cena: Y para cima, Norte = -X, Leste = -Z (Oeste = +Z).
const GRAU = Math.PI / 180;

/**
 * @param {number} latitudeGraus ex.: -23.55 (São Paulo)
 * @param {number} diaDoAno 1..365
 * @param {number} hora hora solar (12 = meio-dia solar)
 * @returns {{azimute: number, elevacao: number}} em graus; azimute a partir do Norte, sentido horário (Leste = 90°)
 */
export function posicaoSolar(latitudeGraus, diaDoAno, hora) {
  const lat = latitudeGraus * GRAU;
  const dec = -23.44 * GRAU * Math.cos(((2 * Math.PI) / 365) * (diaDoAno + 10));
  const h = (hora - 12) * 15 * GRAU;
  const senEl = Math.sin(lat) * Math.sin(dec) + Math.cos(lat) * Math.cos(dec) * Math.cos(h);
  const el = Math.asin(senEl);
  const az = Math.atan2(
    -Math.cos(dec) * Math.sin(h),
    Math.sin(dec) * Math.cos(lat) - Math.cos(dec) * Math.sin(lat) * Math.cos(h),
  );
  return { azimute: ((az / GRAU) + 360) % 360, elevacao: el / GRAU };
}

/** Converte azimute/elevação (graus) em vetor unitário na convenção da cena. */
export function direcaoSolar(azimuteGraus, elevacaoGraus) {
  const az = azimuteGraus * GRAU;
  const el = elevacaoGraus * GRAU;
  const norte = Math.cos(el) * Math.cos(az);
  const leste = Math.cos(el) * Math.sin(az);
  return [-norte, Math.sin(el), -leste];
}

/** Inverso de direcaoSolar. */
export function azElDeDirecao([x, y, z]) {
  const el = Math.asin(Math.max(-1, Math.min(1, y)));
  const az = Math.atan2(-z, -x);
  return { azimute: ((az / GRAU) + 360) % 360, elevacao: el / GRAU };
}
