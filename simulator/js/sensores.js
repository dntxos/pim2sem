// Modelo elétrico dos LDRs: iluminância (lux) -> resistência -> divisor de tensão -> volts no pino.
//
//   5V ──[LDR]──┬── Ax        V = 5 · Rf / (R_ldr + Rf)
//             [10k]           mais luz -> R_ldr menor -> V maior
//              GND
//
// Curva típica de um LDR GL5528: R = R10 · (lux / 10)^(-γ), com R10 ≈ 10–20 kΩ e γ ≈ 0,7.

export const R_FIXO = 10_000;
export const R10_NOMINAL = 15_000;
export const GAMA = 0.7;
const R_ESCURO = 1_000_000;

export function resistenciaLdr(lux, r10 = R10_NOMINAL) {
  if (lux <= 0.001) return R_ESCURO;
  return Math.min(R_ESCURO, r10 * Math.pow(lux / 10, -GAMA));
}

export function tensaoDivisor(rLdr) {
  return (5 * R_FIXO) / (rLdr + R_FIXO);
}

/** Gerador pseudoaleatório determinístico (para a variação entre LDRs ser reprodutível). */
export function rng(semente) {
  let s = semente >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Ruído gaussiano (Box–Muller). */
export function gauss() {
  const u = 1 - Math.random();
  const v = Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}
