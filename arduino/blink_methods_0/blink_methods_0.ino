const int ledPinR =  12;
const int PairIn = 2;

unsigned long lastMillis_ms = 0;
const int MillisDelay_ms = 100;

int ledStateR = LOW;

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
