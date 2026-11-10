// Adaptador do firmware ESP32: o MESMO main.c, compilado para WebAssembly com o núcleo ESP32
// simulado (simulator/esp32/nucleo), exposto com a mesma interface usada para o Arduino Nano
// emulado (setAnalog / run / anguloServo / segundos), para o resto do simulador não mudar.
import { FREQ_HZ } from './arduino.js';

export class Esp32Simulado {
  /**
   * @param {object} modulo instância do esp32.mjs (Emscripten)
   * @param {object} cfg firmware.json (pinos, adcBits, vref)
   * @param {{onSerialLine?: (linha: string) => void}} [opcoes]
   */
  constructor(modulo, cfg, opcoes = {}) {
    const f = (n, r, a) => modulo.cwrap(n, r, a);
    this._avancar = f('sim_avancar', null, ['number']);
    this._tempo = f('sim_tempo_ms', 'number', []);
    this._adc = f('sim_adc', null, ['number', 'number']);
    this._servo = f('sim_servo_angulo', 'number', ['number']);
    this._serial = f('sim_serial', 'string', []);
    this._http = f('sim_http', 'string', ['string']);
    this.ssid = () => f('sim_wifi_ssid', 'string', [])();
    this.cfg = cfg;
    this.placa = 'esp32';
    this.onSerialLine = opcoes.onSerialLine ?? (() => {});
    this._buffer = '';
    this._resto = 0;
    // canal do simulador (1..4 = SE, SD, IE, ID) -> GPIO do main.c
    const p = cfg.pinos;
    this.gpioDoCanal = { 1: p.SE, 2: p.SD, 3: p.IE, 4: p.ID };
    f('sim_setup', null, [])();
    queueMicrotask(() => this._lerSerial()); // entrega "Torre iniciada!" depois de o simulador guardar a instância
  }

  static async criar(urlModulo, cfg, opcoes) {
    const { default: fabrica } = await import(`${urlModulo}?v=${Date.now()}`);
    return new Esp32Simulado(await fabrica(), cfg, opcoes);
  }

  /** Tensão do divisor (escala de 5 V do modelo) -> leitura de 12 bits. Com o divisor alimentado
   *  em 3,3 V a proporção é a mesma; a não linearidade do ADC do ESP32 não é modelada. */
  setAnalog(canal, volts) {
    const gpio = this.gpioDoCanal[canal];
    if (gpio == null) return;
    const max = (1 << (this.cfg.adcBits ?? 12)) - 1;
    this._adc(gpio, Math.round(Math.max(0, Math.min(1, volts / 5)) * max));
  }

  /** Pinos 9/10 do simulador = servo horizontal/vertical. */
  anguloServo(pino) {
    const gpio = pino === 9 ? this.cfg.pinos.servoH : this.cfg.pinos.servoV;
    const a = this._servo(gpio);
    return a < 0 ? null : a;
  }

  get segundos() {
    return this._tempo() / 1000;
  }

  run(ciclos) {
    const ms = ciclos / (FREQ_HZ / 1000) + this._resto;
    const inteiro = Math.floor(ms);
    this._resto = ms - inteiro;
    if (inteiro > 0) this._avancar(inteiro);
    this._lerSerial();
  }

  /** Requisição HTTP ao servidor web do main.c -> {status, tipo, corpo}. */
  http(url) {
    const [status, tipo, ...resto] = this._http(url).split('\t');
    return { status: Number(status), tipo, corpo: resto.join('\t') };
  }

  _lerSerial() {
    this._buffer += this._serial();
    let i;
    while ((i = this._buffer.indexOf('\n')) >= 0) {
      this.onSerialLine(this._buffer.slice(0, i));
      this._buffer = this._buffer.slice(i + 1);
    }
  }
}
