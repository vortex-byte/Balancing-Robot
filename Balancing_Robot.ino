#include <PID_v1.h>
#include <Encoder.h>
#include <Ultrasonic.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"

bool robotActive = false;
#define DEBUG 0
#define SEND_DATA 0

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

// Library Initializing
MPU6050 mpu;
Encoder encoderMotorL(encoderAMotorL, encoderBMotorL);
Encoder encoderMotorR(encoderAMotorR, encoderBMotorR);
Ultrasonic US1(trigPin[0], echoPin[0]);
Ultrasonic US2(trigPin[1], echoPin[1]);
Ultrasonic US3(trigPin[2], echoPin[2]);
Ultrasonic US4(trigPin[3], echoPin[3]);
LiquidCrystal_I2C lcd(0x27, 16, 2);
JsonDocument set;
JsonDocument get;

// LCD Initializing message
char initMsg[16] = {'I','n','i','t','i','a','l','i','z','i','n','g','.','.','.','.'};

// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64];

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         Quaternion container
VectorInt16 aa;         // [x, y, z]            Accel sensor measurements
VectorInt16 gy;         // [x, y, z]            Gyro sensor measurements
VectorInt16 aaReal;     // [x, y, z]            Gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            World-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            Gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector

// packet structure for InvenSense teapot demo
uint8_t teapotPacket[14] = { '$', 0x02, 0,0, 0,0, 0,0, 0,0, 0x00, 0x00, '\r', '\n' };

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}

// PID Variables
double KP = 50; // 60
double KI = 20; // 60
double KD = 0;  // 2

const double maxSpeed = 255, minSpeed = -255;
const double setpointPitch = 0;
double pitchAngle = 0;
double pidMotorL, pidMotorR;
double speedGainL = 0.7, speedGainR = 0.6;
double currentSpeedL = 0, currentSpeedR = 0;

PID pidMotorLeft(&pitchAngle, &pidMotorL, &setpointPitch, KP, KI, KD, DIRECT);
PID pidMotorRight(&pitchAngle, &pidMotorR, &setpointPitch, KP, KI, KD, DIRECT);

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

// GUI last message sent time
unsigned long lastSendTime = 0;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200);
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
  Serial.println(F("Initializing I2C devices..."));
  mpu.initialize();
  pinMode(INTERRUPT_PIN, INPUT);

  // verify connection
  Serial.println(F("Testing device connections..."));
  Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

  // load and configure the DMP
  Serial.println(F("Initializing DMP..."));
  devStatus = mpu.dmpInitialize();

  mpu.setXGyroOffset(29);
  mpu.setYGyroOffset(-5);
  mpu.setZGyroOffset(-3);
  mpu.setZAccelOffset(1161);

  // make sure it worked (returns 0 if so)
  if (devStatus == 0) {
    // Calibration Time: generate offsets and calibrate our MPU6050
    mpu.CalibrateAccel(6);
    mpu.CalibrateGyro(6);
    mpu.PrintActiveOffsets();

    // turn on the DMP, now that it's ready
    Serial.println(F("Enabling DMP..."));
    mpu.setDMPEnabled(true);

    // enable ESP32 interrupt detection
    Serial.println(F("Enabling interrupt detection..."));
    attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), dmpDataReady, RISING);
    mpuIntStatus = mpu.getIntStatus();

    // set our DMP Ready flag so the main loop() function knows it's okay to use it
    Serial.println(F("DMP ready! Waiting for first interrupt..."));
    dmpReady = true;

    // get expected DMP packet size for later comparison
    packetSize = mpu.dmpGetFIFOPacketSize();
    
    pidMotorLeft.SetOutputLimits(minSpeed, maxSpeed);
    pidMotorLeft.SetMode(AUTOMATIC);
    pidMotorLeft.SetSampleTime(10);

    pidMotorRight.SetOutputLimits(minSpeed, maxSpeed);
    pidMotorRight.SetMode(AUTOMATIC);
    pidMotorRight.SetSampleTime(10);
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
  if (robotActive) runRobot();

  if(READ_BUTTON1 && !robotActive){
    robotActive = true;
    BuzzON Led2ON
    delay(200);
    BuzzOFF
  } else if (READ_BUTTON2 && robotActive) {
    robotActive = false;
    BuzzOFF Led1OFF Led2OFF
    controlMotors(0, 0, 0);
  }

  // Read Ultrasonic
  readUS1 = US1.read();
  readUS2 = US2.read();
  readUS3 = US3.read();
  readUS4 = US4.read();

  // Send data to GUI each 100 ms
  if (SEND_DATA && !DEBUG && millis() - lastSendTime >= 100) {
    get["yaw"] = ypr[0] * 180/M_PI;
    get["pitch"] = ypr[1] * 180/M_PI;
    get["roll"] = ypr[2] * 180/M_PI;
    get["speed"] = (actualSpeedLeft + actualSpeedRight) / 2; // Average of speed motor left and right (m/s)
    get["kp"] = KP;
    get["ki"] = KI;
    get["kd"] = KD;
    get["pid"] = pidMotorL;
    get["error"] = setpointPitch - pidMotorL;
    get["distance"] = (lastPositionLeft + lastPositionRight) / 2; // Average of distance motor left and right (m)
    get["usfl"] = (readUS3 <= 20) ? 1 : 0; // If there is obstacle (in distance less or equal to 20) will return true
    get["usfr"] = (readUS4 <= 20) ? 1 : 0;
    get["usbl"] = (readUS1 <= 20) ? 1 : 0;
    get["usbr"] = (readUS2 <= 20) ? 1 : 0;
    serializeJson(get, Serial2);
    Serial2.println();
    lastSendTime = millis();
  }

  // Read message from GUI
  if (Serial2.available() > 0) {
    String data = Serial2.readStringUntil('\n');
    deserializeJson(set, data);
    KP = set["kp"];
    KI = set["ki"];
    KD = set["kd"];
    pidMotorLeft.SetTunings(KP, KI, KD);
    pidMotorRight.SetTunings(KP, KI, KD);
  }

  // Read message from Serial0
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    message.trim();
    String command = message.substring(0, message.indexOf(':'));
    String value = message.substring(message.indexOf(':') + 1);
    runCommand(command, value);
  }

  // Debugging
  if (DEBUG && !SEND_DATA) debug();
}

void runRobot() {
  // Check if DMP is ready before proceeding
  if (!dmpReady) return;

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

  pidMotorLeft.Compute();
  pidMotorRight.Compute();
  controlMotors(pitchAngle, pidMotorL, pidMotorR);

  // Reset interrupt flag and get INT_STATUS byte
  mpuInterrupt = false;
  mpuIntStatus = mpu.getIntStatus();
  fifoCount = mpu.getFIFOCount();

  // Check for overflow (this should never happen unless our code is too inefficient)
  if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
      mpu.resetFIFO();
  } else if (mpuIntStatus & 0x02) {
    // wait for correct available data length, should be a VERY short wait
    while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();

    // read a packet from FIFO
    mpu.getFIFOBytes(fifoBuffer, packetSize);

    // track FIFO count here in case there is > 1 packet available
    fifoCount -= packetSize;

    // Get current orientation from MPU6050
    mpu.dmpGetQuaternion(&q, fifoBuffer); //get value for q
    mpu.dmpGetGravity(&gravity, &q); //get value for gravity
    mpu.dmpGetYawPitchRoll(ypr, &q, &gravity); //get value for ypr
    pitchAngle = ypr[1] * 180/M_PI;
  }
}

void runCommand(String command, String value) {
  Serial.print("command ");
  Serial.print(command);
  Serial.print("\t");
  Serial.print("value ");
  Serial.println(value);
  if (command == "KP") {
    KP = value.toDouble();
  } else if (command == "KI") {
    KI = value.toDouble();
  } else if (command == "KD") {
    KD = value.toDouble();
  } else if (command == "A") {
    if (value == "F") {
      // Forward
    } else if (value == "B") {
      // Backward
    } else if (value == "R") {
      // Right
    } else if (value == "L") {
      // Left
    } else if (value == "G") {
      // Grab
    } else if (value == "P") {
      // Put
    }
  }

  if (command == "KP" || command == "KI" || command == "KD") {
    Serial.print("KP: ");Serial.print(KP);Serial.print("\t KI: ");Serial.print(KI);Serial.print("\t KD: ");Serial.println(KD);
    pidMotorLeft.SetTunings(KP, KI, KD);
    pidMotorRight.SetTunings(KP, KI, KD);
  }
}

void controlMotors(double angle, double speedL, double speedR) {
  if (angle < -50 || angle > 50.0) { // pitch higher than 50 or lower than -50 mean robot is falling down
    speedL = 0;
    speedR = 0;
  } else {
    speedGainL = 0.7;
    speedGainR = 0.7;
  }

  if (speedL == currentSpeedL && speedR == currentSpeedR) return;

  if (speedL > 0) { // forward
    digitalWrite(motorLPin1, HIGH);
    digitalWrite(motorLPin2, LOW);
  } else if (speedL < 0) { // reverse
    speedL = speedL * -1;
    digitalWrite(motorLPin1, LOW);
    digitalWrite(motorLPin2, HIGH);
  } else {
    digitalWrite(motorLPin1, LOW);
    digitalWrite(motorLPin2, LOW);
  }

  if (speedR > 0) { // forward
    digitalWrite(motorRPin1, LOW);
    digitalWrite(motorRPin2, HIGH);
  } else if (speedR < 0) { // reverse
    speedR = speedR * -1;
    digitalWrite(motorRPin1, HIGH);
    digitalWrite(motorRPin2, LOW);
  } else {
    digitalWrite(motorRPin1, LOW);
    digitalWrite(motorRPin2, LOW);
  }

  analogWrite(motorLPWM, speedGainL * speedL);
  analogWrite(motorRPWM, speedGainR * speedR);

  currentSpeedL = speedL;
  currentSpeedR = speedR;
}

void debug() {
  Serial.print("Pitch: ");
  Serial.print(pitchAngle);
  Serial.print("\t pidMotorL: ");
  Serial.print(pidMotorL);
  Serial.print("\t pidMotorR: ");
  Serial.print(pidMotorR);
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
