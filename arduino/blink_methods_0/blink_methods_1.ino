void setup() {
  pinMode(ledPinR, OUTPUT);
  pinMode(PairIn, INPUT);
}

void loop() {
  unsigned long currentMillis_ms = millis();
  if (currentMillis_ms - lastMillis_ms >= MillisDelay_ms) {
    if (digitalRead(2) == 1) {
      led_on();
    }
    else {
      led_off();
    }
    currentMillis_ms = lastMillis_ms;
  }
}
