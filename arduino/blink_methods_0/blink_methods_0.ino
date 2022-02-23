int led_on(int pin, int state){
  if (state == LOW){
    state = HIGH;
    digitalWrite(pin, state);
  }  
  return state;
}
int led_off(int pin, int state) {
  if (state == HIGH){
    state = LOW;
    digitalWrite(pin, state);
  }
}
