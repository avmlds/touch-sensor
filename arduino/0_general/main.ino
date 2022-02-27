void setup() {
  pinMode(ledPinR, OUTPUT);
  pinMode(ledPinB, OUTPUT);
  pinMode(OptpPairIn, INPUT);
  myStepper.setSpeed(200);
  Serial.begin(9600);
}

void loop() {
  unsigned long currentMillis_ms = millis();
  if (currentMillis_ms - lastMillis_ms >= MillisDelay_ms) {
    if (digitalRead(OptpPairIn) == 1) {
      led_on();
    }
    else {
      led_off();
    }
    currentMillis_ms = lastMillis_ms;
  }
  action();
}
