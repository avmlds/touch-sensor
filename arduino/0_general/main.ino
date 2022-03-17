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
  analogWrite(ValENA, 0);
  Serial.begin(115200);

  Wire.begin();  // i2c master
  i2c_write_reg16(D6F_ADDR, 0x0B00, NULL, 0);
  long current_millis = millis();

  delay(300); // пауза после всех настроек на всякий случай
  
}

void loop() {
  long time_ = millis();
  long current_millis_temp = 0;

  long current_millis_PID = 0;
  
  if (time_ - current_millis >= 10) {
    if (send_data == 1) {
      //get_flow();
      float diff_press_pa_aver = get_flow_pa_aver(3);
      
      Serial.print(0);
      Serial.print(" ");
      Serial.print(is_flow_start);
      Serial.print(" ");
      Serial.println(diff_press_pa_aver);
      
      //PID_flow_control(diff_press_pa_aver);
      
      
    }
    current_millis = time_;
  }
  
}
