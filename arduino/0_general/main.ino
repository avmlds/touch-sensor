void setup() {
  pinMode(ledPinR, OUTPUT);
  pinMode(ledPinB, OUTPUT);
  pinMode(OptpPairIn, INPUT);
  myStepper.setSpeed(VELOCITY);
  pinMode(Epin2, OUTPUT);
  pinMode(Epin3, OUTPUT);
  pinMode(ValIn1, OUTPUT);
  pinMode(ValIn2, OUTPUT);
  pinMode(ValENA, OUTPUT);
  digitalWrite(ValIn1, HIGH);
  digitalWrite(ValIn2, LOW);
  analogWrite(ValENA, 255);
  Serial.begin(9600);

  Wire.begin();  // i2c master
  i2c_write_reg16(D6F_ADDR, 0x0B00, NULL, 0);
}

void loop() {
  /* unsigned long currentMillis_ms = millis();
  if (currentMillis_ms - lastMillis_ms >= MillisDelay_ms) {
    if (digitalRead(OptpPairIn) == 1) {
      led_on();
    }
    else {
      led_off();
    }
    currentMillis_ms = lastMillis_ms;
  }
 */ 

    delay(90);
    
    // 2. Trigger getting data (00h, D0h, 40h, 18h, 06h)
    uint8_t send0[] = {0x40, 0x18, 0x06};
    i2c_write_reg16(D6F_ADDR, 0x00D0, send0, 3);

    delay(50);  // wait 50ms
    
    // 3. Read data (00h, D0h, 51h, 2Ch) (07h)
    uint8_t send1[] = {0x51, 0x2C};
    i2c_write_reg16(D6F_ADDR, 0x00D0, send1, 2);
    uint8_t rbuf[2];
    if (i2c_read_reg8(D6F_ADDR, 0x07, rbuf, 2)) {  // read from [07h]
        return;
    }
    uint16_t rd_flow = conv8us_u16_be(rbuf);
    float flow_rate;
    
    // calculation for +/-50[Pa] range
    flow_rate = ((float)rd_flow - 1024.0) * 100.0 / 60000.0 - 50.0;

    Serial.print(flow_rate, 2);  // print converted flow rate
    Serial.println(" [Pa]");

}
