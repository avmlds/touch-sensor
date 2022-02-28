#include <Stepper.h>

int TOTAL_STEPS = 0;
int VELOCITY = 170;
int STEPS = 200;

Stepper myStepper(STEPS , Epin1, Epin2, Epin3, Epin4);

void get_velocity(void) {
  Serial.println(VELOCITY);
}

int set_velocity(int velocity) {
  VELOCITY = velocity;
  myStepper.setSpeed(VELOCITY);
}

int down(int steps) {
  myStepper.step(steps);
  TOTAL_STEPS += steps;
  return 0;
}

int up(int steps) {
  myStepper.step(-steps);
  TOTAL_STEPS -= steps;
  return 0;
}

void do_init() {
  while (digitalRead(OptpPairIn) != 1) {
    up(10);
    TOTAL_STEPS = 0;
  }
  
}

void get_steps() {
  Serial.println(TOTAL_STEPS);
}
