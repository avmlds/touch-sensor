int engineTarget = 0;

void action() {
 if (Serial.available() > 0) {
  char receivedChar = Serial.read();
  switch (receivedChar) {
      case '1': serial_led_on(); break;
      case '0': serial_led_off(); break;
      case '2': up(2000); break;
      case '3': down(2000); break;
  }
  Serial.println(receivedChar);
  
 }
}
