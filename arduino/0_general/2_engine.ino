#include <Stepper.h> 

int STEPS = 200;
Stepper myStepper(STEPS , Epin1, Epin2, Epin3, Epin4);


int get_velocity(void){
  return 0;
}

int down(int steps){
  myStepper.step(steps); 
  return 0;
}

int up(int steps){
  myStepper.step(-steps); 
  return 0;
}
