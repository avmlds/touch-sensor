#include <Stepper.h>

long int TOTAL_STEPS = 0;
int VELOCITY = 200;
int STEPS = 3200;
int IS_INIT = 1;

Stepper myStepper(STEPS , Epin2, Epin3);

void get_velocity(void) {
  Serial.println(VELOCITY);
}

void set_velocity(int velocity) {
  VELOCITY = velocity;
  myStepper.setSpeed(VELOCITY);
  //Serial.println("speed was updated");
}

int down(int steps) {
  myStepper.step(steps);
  TOTAL_STEPS += steps;
  if (IS_INIT != 0){
    IS_INIT = 0;
  }
  return 0;
}

int up(int steps) {
  myStepper.step(-steps);
  TOTAL_STEPS -= steps;
  if (IS_INIT != 0){
    IS_INIT = 0;
  }
  return 0;
}

void do_init() {
  while (digitalRead(OptpPairIn) != 1) {
    up(10);
  TOTAL_STEPS = 0;
  IS_INIT = 1;
  }
  
}

void get_steps() {
  Serial.println(TOTAL_STEPS);
}
