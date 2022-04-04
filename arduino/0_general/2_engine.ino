#include <Stepper.h>

long int TOTAL_STEPS = 0;
int VELOCITY = 640;
int STEPS = 1600;
int IS_INIT = 1;

Stepper myStepper(STEPS , Epin2, Epin3);

void get_velocity(void) {
  Serial.println(VELOCITY);
}

void set_velocity(int velocity) {
  VELOCITY = velocity;
  myStepper.setSpeed(VELOCITY);
  Serial.println("speed was updated");
}


void EngineMove(void) {
  if (MOVE_TO < 0){
    myStepper.step(-STEP);
    TOTAL_STEPS -= STEP;
    MOVE_TO += STEP;
    if (MOVE_TO > 0){
      SHIFT = 0;
      MOVE_TO = 0;
    }
  } else if (MOVE_TO > 0) {
    myStepper.step(STEP);
    TOTAL_STEPS += STEP;
    MOVE_TO -= STEP;
    if (MOVE_TO < 0){
      SHIFT = 0;
      MOVE_TO = 0;
    }
  }
  if (IS_INIT != 0){
    IS_INIT = 0;
  }
}

void do_init() {}

void get_steps() {
  Serial.println(TOTAL_STEPS);
}
