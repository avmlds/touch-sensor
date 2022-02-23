const int ledPinB =  11;
const int PairIn = 2;

unsigned long lastMillis = 0;
const int MillisDelay = 100;

int ledStateB = LOW;

void setup() {
  pinMode(ledPinB, OUTPUT);
  pinMode(PairIn, INPUT);
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - lastMillis >= MillisDelay) {
    if (digitalRead(2) == 1) {
      ledStateB = led_on(ledPinB, ledStateB);
    }
    else {
      ledStateB = led_off(ledPinB, ledStateB);
    }
    currentMillis = lastMillis;
  }
}
