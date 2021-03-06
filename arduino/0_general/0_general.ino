// Optopair pin
const int OptpPairIn = 2;

// Leds configuration
int ledStateR = LOW;
int ledStateB = LOW;

// Led pins
const int ledPinR =  12;
const int ledPinB =  7;

// Delay millis
unsigned long lastMillis_ms = 0;
const int MillisDelay_ms = 100;

// Engine pins
const int Epin2 = 2;
const int Epin3 = 3;

const int STEP = 640;

long int SHIFT = 0;
long int MOVE_TO = 0;
int INIT = 0;

// Valve pins
const int ValENA = 6;
const int ValIn1 = 5;
const int ValIn2 = 4;

long current_millis = 0;
long current_pid_millis = 0;

// Variable for storing state, send data to serial port or not
int send_data = 0;

// Переменные для ПИД регулятора
int USE_PID = 0;
int valve_open_pwm_bit = 0; // переменная для хранения значения открытия клапана, нужна для ПИД регулятора
float press_aim_pa = 5; // целевое давление в Па
float press_shift_pa = 1; // допустимый сдвиг давления от целевого
int PID_check_delay_ms = 100; // пауза между проверками и коррекции клапана для ПИД
int is_flow_start = 0; // флаг, запустили ли поток газа или он пока около нуля. Нужен для быстрой регуляции ПИД в начале
