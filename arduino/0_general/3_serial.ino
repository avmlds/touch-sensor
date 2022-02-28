
void serialEvent() {
  String st = Serial.readStringUntil('\n');
  if (st == "up") {
    up(2000);
    return;
  } else if (st == "down") {
    down(2000);
    return;
  } else if (st == "led_on") {
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
  } else if (st == "set_velocity") {
    set_velocity(200);
    return;
  }

  Serial.println("Wrong command");
  return;
}
