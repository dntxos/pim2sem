#include <Servo.h>

Servo servoHorizontal;
Servo servoVertical;

// LDRs
const int LDR_SE = A1;
const int LDR_SD = A2;
const int LDR_IE = A3;
const int LDR_ID = A4;

// Servos
const int PINO_HORIZONTAL = 9;
const int PINO_VERTICAL = 10;

// Posições iniciais
int anguloHorizontal = 90;
int anguloVertical = 90;

// Configurações
const int TOLERANCIA = 40;
const int PASSO = 2;

void setup() {
  Serial.begin(9600);

  servoHorizontal.attach(PINO_HORIZONTAL);
  servoVertical.attach(PINO_VERTICAL);

  servoHorizontal.write(anguloHorizontal);
  servoVertical.write(anguloVertical);

  delay(1000);
}

void loop() {

  // Leitura dos sensores
  int supEsq = analogRead(LDR_SE);
  int supDir = analogRead(LDR_SD);
  int infEsq = analogRead(LDR_IE);
  int infDir = analogRead(LDR_ID);

  // Comparação horizontal
  int esquerda = (supEsq + infEsq) / 2;
  int direita = (supDir + infDir) / 2;

  // Comparação vertical
  int superior = (supEsq + supDir) / 2;
  int inferior = (infEsq + infDir) / 2;

  // Eixo horizontal
  if (esquerda > direita + TOLERANCIA) {
    anguloHorizontal += PASSO;
  }
  else if (direita > esquerda + TOLERANCIA) {
    anguloHorizontal -= PASSO;
  }

  // Eixo vertical
  if (superior > inferior + TOLERANCIA) {
    anguloVertical -= PASSO;
  }
  else if (inferior > superior + TOLERANCIA) {
    anguloVertical += PASSO;
  }

  // Limites dos servos
  anguloHorizontal = constrain(
    anguloHorizontal, 20, 160
  );

  anguloVertical = constrain(
    anguloVertical, 20, 160
  );

  // Movimentação
  servoHorizontal.write(anguloHorizontal);
  servoVertical.write(anguloVertical);

  // Monitor Serial
  Serial.print("Esquerda: ");
  Serial.print(esquerda);

  Serial.print(" | Direita: ");
  Serial.print(direita);

  Serial.print(" | Superior: ");
  Serial.print(superior);

  Serial.print(" | Inferior: ");
  Serial.print(inferior);

  Serial.print(" | Horizontal: ");
  Serial.print(anguloHorizontal);

  Serial.print(" | Vertical: ");
  Serial.println(anguloVertical);

  delay(50);
}