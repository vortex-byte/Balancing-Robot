#include <PID_v1.h>
#include <Encoder.h>
#include <Ultrasonic.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"

#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

bool ACTIVATE = false;
bool RUN_MOTOR = true;
#define DEBUG 0
#define SEND_DATA 1

#define BUZZER_PIN 13
#define INTERRUPT_PIN 19
#define PB1_PIN 24
#define PB2_PIN 25
#define LED1_PIN 22
#define LED2_PIN 23

const int motorLPin1 = 34;
const int motorLPin2 = 35;
const int motorRPin1 = 36;
const int motorRPin2 = 37;

const int motorLPWM = 4;
const int motorRPWM = 5;

#define encoderAMotorL 2
#define encoderBMotorL 38
#define encoderAMotorR 18
#define encoderBMotorR 39

uint8_t trigPin[4] = {26, 28, 30, 32};
uint8_t echoPin[4] = {27, 29, 31, 33};

#define Led1ON digitalWrite(LED1_PIN, HIGH);
#define Led2ON digitalWrite(LED2_PIN, HIGH);
#define BuzzON digitalWrite(BUZZER_PIN, HIGH);
#define Led1OFF digitalWrite(LED1_PIN, LOW);
#define Led2OFF digitalWrite(LED2_PIN, LOW);
#define BuzzOFF digitalWrite(BUZZER_PIN, LOW);
#define READ_BUTTON1 !digitalRead(PB1_PIN)
#define READ_BUTTON2 !digitalRead(PB2_PIN)
#define MIN_DISTANCE 20 // Minimum distance to an obstacle in cm

// LCD Initializing message
char initMsg[16] = {'I','n','i','t','i','a','l','i','z','i','n','g','.','.','.','.'};

// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64];
Quaternion q;           // [w, x, y, z]         quaternion container
VectorFloat gravity;    // [x, y, z]            gravity vector
VectorInt16 gy;			    // [x, y, z]            Gyro sensor measurements
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector
uint8_t teapotPacket[14] = { '$', 0x02, 0,0, 0,0, 0,0, 0,0, 0x00, 0x00, '\r', '\n' };
volatile bool mpuInterrupt = false;
void dmpDataReady() {
    mpuInterrupt = true;
}

// PID Variables
double KP = 26;
double KI = 0;
double KD = 0.5;
double KPy = 0.7;
double KIy = 0.4;
double KDy = 0.01;
double pidRollOut = 0, pidYawOut = 0;
double speedLeft = 0, speedRight = 0;
double speedFactor = 0.75;

// IMU Variables
const double maxPID = 255, minPID = -255;
double setpointRoll = -1.5, setpointYaw = 0.01; // Target desired angle
double prevRoll = 0, roll = 0, yaw = 0; 		// Actual angle
double currentSpeedL = 0, currentSpeedR = 0;
double motorAdjust = 0;

// Low-pass filter variables
float filteredRoll = 0.0;
float alpha = 0.8;

// Encoder variables
const double wheelCircumference = 0.2042; // meter
const int pulsePerRevolution = 160;
unsigned long lastTime = 0;
int pulseLeft, pulseRight;
long lastPositionLeft, lastPositionRight;
double rpmLeft, rpmRight;
int actualPulseLeft, actualPulseRight;
double actualSpeedLeft, actualSpeedRight;

// Ultrasonic variables
int readUS1, readUS2, readUS3, readUS4;
int obstacleSpeed = 0, obstacleThreshold = 0;

// GUI last message sent time
unsigned long lastSendTime = 0;

// Library Initializing
MPU6050 mpu;
PID pidRoll(&roll, &pidRollOut, &setpointRoll, KP, KI, KD, DIRECT);
PID pidYaw(&yaw, &pidYawOut, &setpointYaw, KPy, KIy, KDy, DIRECT);
Encoder encoderMotorL(encoderAMotorL, encoderBMotorL);
Encoder encoderMotorR(encoderAMotorR, encoderBMotorR);
Ultrasonic US1(trigPin[0], echoPin[0]);
Ultrasonic US2(trigPin[1], echoPin[1]);
Ultrasonic US3(trigPin[2], echoPin[2]);
Ultrasonic US4(trigPin[3], echoPin[3]);
LiquidCrystal_I2C lcd(0x27, 16, 2);
JsonDocument set;
JsonDocument get;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200);
  Serial2.setTimeout(10);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  pinMode(PB1_PIN, INPUT_PULLUP);
  pinMode(PB2_PIN, INPUT_PULLUP);

  // Motor PIN setup
  pinMode(motorLPin1, OUTPUT);
  pinMode(motorLPin2, OUTPUT);
  pinMode(motorRPin1, OUTPUT);
  pinMode(motorRPin2, OUTPUT);

  // join I2C bus (I2Cdev library doesn't do this automatically)
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
      Wire.begin();
      Wire.setClock(400000); // 400kHz I2C clock. Comment this line if having compilation difficulties
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
      Fastwire::setup(400, true);
  #endif

  lcd.init();
  lcd.clear();
  lcd.backlight();
  lcd.setCursor(0,0);

  for(int i = 0; i < 16; i++) {
    lcd.print(initMsg[i]);
    delay(50);
  }

  // initialize device
  mpu.initialize();
  pinMode(INTERRUPT_PIN, INPUT);

  // verify connection
  // Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

  // load and configure the DMP
  devStatus = mpu.dmpInitialize();

  mpu.setXGyroOffset(29);
  mpu.setYGyroOffset(-5);
  mpu.setZGyroOffset(-3);
  mpu.setZAccelOffset(1161);

  if (devStatus == 0) {
    mpu.setDMPEnabled(true);

    // enable ESP32 interrupt detection
    attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), dmpDataReady, RISING);
    mpuIntStatus = mpu.getIntStatus();

    // set our DMP Ready flag so the main loop() function knows it's okay to use it
    Serial.println(F("DMP ready! Waiting for first interrupt..."));
    dmpReady = true;

    // get expected DMP packet size for later comparison
    packetSize = mpu.dmpGetFIFOPacketSize();
    
    pidRoll.SetOutputLimits(minPID, maxPID);
    pidRoll.SetMode(AUTOMATIC);
    pidRoll.SetSampleTime(10);

    pidYaw.SetOutputLimits(minPID, maxPID);
    pidYaw.SetMode(AUTOMATIC);
    pidYaw.SetSampleTime(10);
    lcd.clear();
  } else {
    lcd.clear();
    lcd.print("DMP Initialization failed");
    Serial.print(F("DMP Initialization failed (code "));
    Serial.print(devStatus);
    Serial.println(F(")"));
  }

  for (int i = 0; i < 3; i++) {
    BuzzON Led1ON Led2ON
    delay(200);
    BuzzOFF Led1OFF Led2OFF
    delay(200);
  }
}

void loop() {
  if(READ_BUTTON1 && !ACTIVATE){
    ACTIVATE = true;
    RUN_MOTOR = true;
    BuzzON Led2ON
    delay(200);
    BuzzOFF
  } else if (READ_BUTTON2 && ACTIVATE) {
    ACTIVATE = false;
    RUN_MOTOR = false;
    BuzzOFF Led1OFF Led2OFF
    controlMotors(0, 0);
  }

  if (ACTIVATE) runRobot();

  // Send data to GUI each 100 ms
  if (SEND_DATA && !DEBUG && millis() - lastSendTime >= 100) {
    get["yaw"] = ypr[0] * 180/M_PI;
    get["pitch"] = ypr[1] * 180/M_PI;
    get["roll"] = ypr[2] * 180/M_PI;
    get["speed"] = (actualSpeedLeft + actualSpeedRight) / 2; // Average of speed motor left and right (m/s)
    get["kp"] = KP;
    get["ki"] = KI;
    get["kd"] = KD;
    get["pid"] = pidRollOut;
    get["setpoint"] = setpointRoll;
    get["speedfactor"] = speedFactor;
    get["error"] = setpointRoll - pidRollOut;
    get["distance"] = (lastPositionLeft + lastPositionRight) / 2; // Average of distance motor left and right (m)
    get["usfl"] = readUS3;
    get["usfr"] = readUS4;
    get["usbl"] = readUS1;
    get["usbr"] = readUS2;
    serializeJson(get, Serial2);
    Serial2.println();
    lastSendTime = millis();
  }

  // Read message from GUI
  if (Serial2.available() > 0) {
    String data = Serial2.readStringUntil("\n");
    deserializeJson(set, data);
    if (set["kp"]) {
      KP = set["kp"];
      KI = set["ki"];
      KD = set["kd"];
      setpointRoll = set["setpoint"];
      // obstacleSpeed = set["threshold"];
      // speedFactor = set["speedfactor"];
      pidRoll.SetTunings(KP, KI, KD);
    } else {
      unsigned char direction = set["direction"];
    }
  }

  if (Serial.available() > 0) {
    String data = Serial2.readStringUntil("\n");
    int limit = data.indexOf(':');
    String command = data.substring(0, limit);
    String value = data.substring(limit + 1);
    if (command == "KP") KP = value.toDouble();
    if (command == "KI") KI = value.toDouble();
    if (command == "KD") KD = value.toDouble();
    if (command == "SP") setpointRoll = value.toDouble();
    pidRoll.SetTunings(KP, KI, KD);
    Serial.println(value.toDouble());
  }

  // Debugging
  if (DEBUG && !SEND_DATA) debug();
}

void runRobot() {
  if (!dmpReady) return;
  mpuInterrupt = false;
  mpuIntStatus = mpu.getIntStatus();
  fifoCount = mpu.getFIFOCount();

  if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
    mpu.resetFIFO();
  } else if (mpuIntStatus & 0x02) {
    while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();
    mpu.getFIFOBytes(fifoBuffer, packetSize); // read a packet from FIFO
    fifoCount -= packetSize;
    mpu.dmpGetQuaternion(&q, fifoBuffer); //get value for q
    mpu.dmpGetGravity(&gravity, &q); //get value for gravity
    mpu.dmpGetYawPitchRoll(ypr, &q, &gravity); //get value for ypr
    mpu.dmpGetGyro(&gy, fifoBuffer); // get gyro rate

    yaw = abs(gy.z / 131.0); // Get yaw gyro rate
    roll = alpha * roll + (1 - alpha) * actRoll;

    pidRoll.Compute();

    speedLeft = constrain(pidRollOut + pidYawOut + motorAdjust + obstacleSpeed, -255, 255);
    speedRight = constrain(pidRollOut - pidYawOut - motorAdjust + obstacleSpeed, -255, 255);
    if (RUN_MOTOR) controlMotors(speedLeft, speedRight);
  }

  // Read Ultrasonic
  readUS1 = US1.read();
  readUS2 = US2.read();
  readUS3 = US3.read();
  readUS4 = US4.read();

  if (readUS3 || readUS4) { // Obstacle in front
    obstacleSpeed = -100;
  } else if(readUS1 || readUS2) { // Obstacle in back
    obstacleSpeed = 100;
  }

  // Read Encoder
  unsigned long currentTime = millis();
  
  if (currentTime - lastTime >= 1000) {
    pulseLeft = encoderMotorL.read();
    pulseRight = encoderMotorR.read();
    actualPulseLeft += pulseLeft;
    actualPulseRight += pulseRight;
    encoderMotorL.write(0);
    encoderMotorR.write(0);
    
    rpmLeft = (pulseLeft * 60.0) / pulsePerRevolution;
    rpmRight = (pulseRight * 60.0) / pulsePerRevolution;
    lastTime = currentTime;
  }

  int pulsePerSecLeft = (rpmLeft * pulsePerRevolution) / 60;
  int pulsePerSecRight = (rpmRight * pulsePerRevolution) / 60;
  actualSpeedLeft = (pulsePerSecLeft / pulsePerRevolution) * wheelCircumference;
  actualSpeedRight = (pulsePerSecRight / pulsePerRevolution) * wheelCircumference;
  lastPositionLeft = (actualPulseLeft / pulsePerRevolution) * wheelCircumference;
  lastPositionRight = (actualPulseRight / pulsePerRevolution) * wheelCircumference;
}

void controlMotors(double speedL, double speedR) {
  if (speedL == currentSpeedL && speedR == currentSpeedR) return;

  if (speedL > 0) { // forward
    digitalWrite(motorLPin1, LOW);
    digitalWrite(motorLPin2, HIGH);
  } else if (speedL < 0) { // reverse
    speedL = speedL * -1;
    digitalWrite(motorLPin1, HIGH);
    digitalWrite(motorLPin2, LOW);
  } else {
    digitalWrite(motorLPin1, LOW);
    digitalWrite(motorLPin2, LOW);
  }

  if (speedR > 0) { // forward
    digitalWrite(motorRPin1, HIGH);
    digitalWrite(motorRPin2, LOW);
  } else if (speedR < 0) { // reverse
    speedR = speedR * -1;
    digitalWrite(motorRPin1, LOW);
    digitalWrite(motorRPin2, HIGH);
  } else {
    digitalWrite(motorRPin1, LOW);
    digitalWrite(motorRPin2, LOW);
  }

  analogWrite(motorLPWM, speedFactor * speedL);
  analogWrite(motorRPWM, speedFactor * speedR);

  currentSpeedL = speedL;
  currentSpeedR = speedR;
}

void debug() {
  Serial.print("Roll: ");
  Serial.print(roll);
  Serial.print("\t pidMotorL: ");
  Serial.print(speedLeft);
  Serial.print("\t pidMotorR: ");
  Serial.print(speedRight);
  Serial.print("\t pulseLeft: ");
  Serial.print(pulseLeft);
  Serial.print("\t pulseRight: ");
  Serial.print(pulseRight);
  Serial.print("\t Pos L: ");
  Serial.print(lastPositionLeft);
  Serial.print("\t Pos R: ");
  Serial.print(lastPositionRight);
  Serial.print("\t US 1: ");
  Serial.print(US1.read());
  Serial.print("\t US 2: ");
  Serial.print(US2.read());
  Serial.print("\t US 3: ");
  Serial.print(US3.read());
  Serial.print("\t US 4: ");
  Serial.print(US4.read());
  Serial.print("\t Enc L: ");
  Serial.print(encoderMotorL.read());
  Serial.print("\t Enc R: ");
  Serial.print(encoderMotorR.read());
  Serial.println();
}
