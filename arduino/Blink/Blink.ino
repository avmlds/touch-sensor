int operate_led(int pin, int state) {
  if (state == LOW) {
    state = HIGH;
  } else {
    state = LOW;
  }
  digitalWrite(pin, state);
  return state;
}
