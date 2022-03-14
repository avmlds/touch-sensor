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
  Serial.begin(115200);

  Wire.begin();  // i2c master
  i2c_write_reg16(D6F_ADDR, 0x0B00, NULL, 0);
}

void loop() {
}
