const int ledPinR =  13;
const int ledPinG =  12;
const int ledPinB =  11;

int ledStateR = LOW;             // состояние светодиода
int ledStateG = LOW;
int ledStateB = LOW;

unsigned long previousMillisR = 0;
unsigned long previousMillisG = 0;
unsigned long previousMillisB = 0;

const long intervalR = 1000;           // интервал между миганиями (миллисекунды)
const long intervalG = 500;           // интервал между миганиями (миллисекунды)
const long intervalB = 300;           // интервал между миганиями (миллисекунды)

// Я в своем коде указываю сразу в названии переменной, какая размерность, чтобы потом не искать и не ошибиться
// например, я бы назвал intervalR_ms

void setup() {
  pinMode(ledPinR, OUTPUT);
  pinMode(ledPinG, OUTPUT);
  pinMode(ledPinB, OUTPUT);
}

void loop() {
  unsigned long currentMillisR = millis();
  unsigned long currentMillisG = millis();  // Посмотри, можно ли исопльзовать одну переменную currentMillis для всех процессов?
  unsigned long currentMillisB = millis();
  
  if (currentMillisR - previousMillisR >= intervalR) {
    previousMillisR = currentMillisR;
    ledStateR = operate_led(ledPinR, ledStateR);
  }
  
  if (currentMillisG - previousMillisG >= intervalG) {
    previousMillisG = currentMillisG;
    ledStateG = operate_led(ledPinG, ledStateG);
  }
  
  if (currentMillisB - previousMillisB >= intervalB) {
    previousMillisB = currentMillisB;
    ledStateB = operate_led(ledPinB, ledStateB);
  }
}
