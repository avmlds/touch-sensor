void led_on(){
  if (ledStateR == LOW){
    ledStateR = HIGH;
    digitalWrite(ledPinR, ledStateR);
  }  
}
void led_off() {
  if (ledStateR == HIGH){
    ledStateR = LOW;
    digitalWrite(ledPinR, ledStateR);
  }
}

void serial_led_on(){
  if (ledStateB == LOW){
    ledStateB = HIGH;
    digitalWrite(ledPinB, ledStateB);
  }  
}

void serial_led_off() {
  if (ledStateB == HIGH){
    ledStateB = LOW;
    digitalWrite(ledPinB, ledStateB);
  }
}
