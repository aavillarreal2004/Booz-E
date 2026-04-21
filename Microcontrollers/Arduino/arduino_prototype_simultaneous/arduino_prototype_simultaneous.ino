// Setting all peripheral pins
const int motorPin1 = 2;
const int Sol1 = 3;
const int motorPin2 = 5;
const int Sol2 = 6;

// Data pins for receiving drink information
const int nozzle_1 = 0;
const int nozzle_2 = 0;
const int drink_code_1 = 0;
const int drink_code_2 = 0;
const int drink_code_3 = 0;

// Output pin for when drink is done
const int output_1 = 0;
const int output_2 = 0;

// Calibrating the load cell
#include "HX711.h"

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 7;
const int LOADCELL_SCK_PIN = 11;

HX711 scale;
float calibration_number = 56755 / 157.9;
// 157.9 is calibration object weight, 56755 was output

void setup() {
  // Configuring all inputs and outputs
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(Sol1, OUTPUT);
  pinMode(Sol2, OUTPUT);
  pinMode(Input1, INPUT);
  pinMode(Input2, INPUT);
  pinMode(Input3, INPUT);
  pinMode(Output, OUTPUT);

  // HX711 Scale reading
  Serial.begin(38400);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
}

void loop() {
  delay(100);

  // put your main code here, to run repeatedly:
  Red = digitalRead(Input1);
  Purple = digitalRead(Input2);
  Mix = digitalRead(Input3);

  if ((Red == HIGH) && (Purple == HIGH) && (Mix == HIGH)) {
    digitalWrite(Sol1, HIGH);
    digitalWrite(Sol2, HIGH);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, HIGH);
    delay(6200);
    digitalWrite(Sol1, LOW);
    digitalWrite(Sol2, LOW);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
  }

  if ((Red == HIGH) && (Purple == LOW)) {
    digitalWrite(Sol1, HIGH);
    digitalWrite(Sol2, LOW);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, LOW);
    delay(6000);
    digitalWrite(Sol1, LOW);
    digitalWrite(Sol2, LOW);
    delay(200);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    delay(50);
    digitalWrite(Output, HIGH);
    delay(500);
    digitalWrite(Output, LOW);
  }

  if ((Purple == HIGH) && (Red == LOW)) {
    digitalWrite(Sol1, HIGH);
    digitalWrite(Sol2, HIGH);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, HIGH);
    delay(3000);
    digitalWrite(Sol1, LOW);
    digitalWrite(Sol2, LOW);
    delay(500);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    delay(50);
    digitalWrite(Output, HIGH);
    delay(500);
    digitalWrite(Output, LOW);
  }

  if ((Mix == HIGH) && (Red == LOW)) {
    digitalWrite(Sol1, HIGH);
    digitalWrite(Sol2, HIGH);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, HIGH);
    delay(2000);
    digitalWrite(Sol1, LOW);
    delay(50);
    digitalWrite(motorPin1, LOW);
    delay(4000);
    digitalWrite(Sol2, LOW);
    delay(50);
    digitalWrite(motorPin2, LOW);
    delay(50);
    digitalWrite(Output, HIGH);
    delay(500);
    digitalWrite(Output, LOW);
  }

  // Future load cell code
  //
  //
}
