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
  long current_pid_millis = millis();

  delay(300); // пауза после всех настроек на всякий случай

}


void loop() {
  long time_ = millis();
  long pid_millis = millis();

  if (time_ - current_millis >= 10) {
    if (SHIFT == 1){
      if (MOVE_TO != 0){
        EngineMove();
      }
    }
    if (send_data == 1) {
      //get_flow();
      float diff_press_pa_aver = get_flow_pa_aver(3);

      Serial.print(MOVE_TO);
      Serial.print(" ");
      Serial.print(TOTAL_STEPS);
      Serial.print(" ");
      Serial.println(diff_press_pa_aver);

      if (USE_PID == 1){
        if (pid_millis - current_pid_millis >= PID_check_delay_ms){
          PID_flow_control(diff_press_pa_aver);
        }
      }

    }
    current_millis = time_;
    current_pid_millis = pid_millis;
  }

}
