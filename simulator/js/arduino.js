// Emulação do Arduino UNO (ATmega328P @ 16 MHz) rodando o firmware compilado (.hex).
// Usa avr8js: o código executado é exatamente o binário gerado a partir do main.c.
import {
  CPU, avrInstruction,
  AVRTimer, timer0Config, timer1Config, timer2Config,
  AVRIOPort, portBConfig, portCConfig, portDConfig,
  AVRUSART, usart0Config,
  AVRADC, adcConfig,
} from '../vendor/avr8js.mjs';

export const FREQ_HZ = 16_000_000;

// Biblioteca Servo: write(0..180) -> pulso de 544..2400 µs.
const SERVO_MIN_US = 544;
const SERVO_MAX_US = 2400;

/** Converte um arquivo Intel HEX em memória de programa. */
export function parseIntelHex(text) {
  const flash = new Uint8Array(32 * 1024);
  let base = 0;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line.startsWith(':')) continue;
    const bytes = line.slice(1).match(/../g).map((h) => parseInt(h, 16));
    const [len, hi, lo, type] = bytes;
    const data = bytes.slice(4, 4 + len);
    if (type === 0) flash.set(data, base + ((hi << 8) | lo));
    else if (type === 2) base = ((data[0] << 8) | data[1]) << 4;
    else if (type === 4) base = ((data[0] << 8) | data[1]) << 16;
    else if (type === 1) break;
  }
  return flash;
}

export class ArduinoUno {
  /**
   * @param {string} hexText conteúdo do .hex
   * @param {{onSerialLine?: (linha: string) => void}} [opcoes]
   */
  constructor(hexText, opcoes = {}) {
    const flash = parseIntelHex(hexText);
    this.cpu = new CPU(new Uint16Array(flash.buffer));
    this.timers = [timer0Config, timer1Config, timer2Config].map((c) => new AVRTimer(this.cpu, c));
    this.portB = new AVRIOPort(this.cpu, portBConfig);
    this.portC = new AVRIOPort(this.cpu, portCConfig);
    this.portD = new AVRIOPort(this.cpu, portDConfig);
    this.adc = new AVRADC(this.cpu, adcConfig);
    this.usart = new AVRUSART(this.cpu, usart0Config, FREQ_HZ);

    this.onSerialLine = opcoes.onSerialLine ?? (() => {});
    this.usart.onLineTransmit = (linha) => this.onSerialLine(linha);

    // Medição da largura de pulso dos servos: D9 = PB1, D10 = PB2.
    this.pulsoUs = { 9: null, 10: null };
    const subida = { 9: 0, 10: 0 };
    const bits = { 9: 1, 10: 2 };
    this.portB.addListener((valor, anterior) => {
      for (const pino of [9, 10]) {
        const m = 1 << bits[pino];
        if ((valor & m) && !(anterior & m)) subida[pino] = this.cpu.cycles;
        else if (!(valor & m) && (anterior & m)) {
          this.pulsoUs[pino] = (this.cpu.cycles - subida[pino]) / (FREQ_HZ / 1e6);
        }
      }
    });
  }

  /** Define a tensão (0–5 V) em uma entrada analógica A0..A5. */
  setAnalog(canal, volts) {
    this.adc.channelValues[canal] = Math.max(0, Math.min(5, volts));
  }

  /** Ângulo comandado (0–180°) deduzido do último pulso no pino, ou null se ainda não houve pulso. */
  anguloServo(pino) {
    const us = this.pulsoUs[pino];
    if (us == null) return null;
    return ((us - SERVO_MIN_US) * 180) / (SERVO_MAX_US - SERVO_MIN_US);
  }

  get segundos() {
    return this.cpu.cycles / FREQ_HZ;
  }

  /** Executa o firmware por `ciclos` ciclos de clock. */
  run(ciclos) {
    const cpu = this.cpu;
    const fim = cpu.cycles + ciclos;
    while (cpu.cycles < fim) {
      avrInstruction(cpu);
      cpu.tick();
    }
  }
}
