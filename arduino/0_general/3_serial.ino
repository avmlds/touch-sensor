
void serialEvent() {
  String st = Serial.readStringUntil('\n');

  if (st == "led_on") {
    serial_led_on();
    return;
  } else if (st == "led_off") {
    serial_led_off();
    return;
  } else if (st == "get_steps") {
    return get_steps();
  } else if (st == "do_init") {
    return do_init();
  } else if (st == "get_velocity") {
    get_velocity();
    return;
  } else if (st == "flow") {
    get_flow();
    return;
  } else if (st == "shot") {
    turn_valve(240);
    delay(3);
    turn_valve(0);
    return;
  }

  String st_com = st.substring(0, 3);
  if (st_com == "snd"){
    st.remove(0, 3);
    int st_f = st.toInt();

    if (st_f == 1){
      send_data = 1;
      USE_PID = 1;
    } else {
      send_data = 0;
      USE_PID = 0;
    }
  } else if (st_com == "pid") {
    st.remove(0, 3);
    int st_f = st.toInt();
    USE_PID = st_f;

  } else if (st_com == "vel") {
    st.remove(0, 3);
    int st_f = st.toInt();
    set_velocity(st_f);
    return;
  } else if (st_com == "val") {

      st.remove(0, 3);
      int st_f = st.toInt();

      if (st_f > 255) {
        st_f = 255;
      } else if (st_f < 0){
        st_f = 0;
    }
    turn_valve(st_f);
    return;
  } else if (st_com == "thr"){

    st.remove(0, 3);
    float st_f = st.toFloat();
    press_aim_pa = st_f;

  } else if (st_com == "bnd"){

    st.remove(0, 3);
    float st_f = st.toFloat();
    press_shift_pa = st_f;

  } else if (st_com == "mov") {

    st.remove(0, 3);
    long int st_f = st.toInt();
    SHIFT = 1;
    MOVE_TO = st_f;
    return;

  } else {
  Serial.println("Wrong command");
  return;
  }
}
