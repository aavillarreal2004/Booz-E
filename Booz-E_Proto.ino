const int motorPin1 = 2;
const int Sol1 = 3;
const int motorPin2 = 5;
const int Sol2 = 6;
const int Input1 = 11;
const int Input2 = 12;
const int Input3 = 13;
int read = 0;
int Blue = 0;
int Mix = 0;
int Purple = 0;
const int Output = 8;

void setup() {
  // put your setup code here, to run once:
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(Sol1, OUTPUT);
  pinMode(Sol2, OUTPUT);
  pinMode(Input1, INPUT);
  pinMode(Input2, INPUT);
  pinMode(Input3, INPUT);
  pinMode(Output, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  Blue = digitalRead(Input1);
  Purple = digitalRead(Input2);
  Mix = digitalRead(Input3);
  if ((Blue == HIGH) && (Purple == HIGH) && (Mix == HIGH)) {
    digitalWrite(Sol1, HIGH);
    digitalWrite(Sol2, HIGH);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    delay(10000);
    digitalWrite(Sol1, LOW);
    digitalWrite(Sol2, LOW);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, HIGH);
  }

  if ((Blue == HIGH) && (Purple == LOW)) {
    digitalWrite(Sol1, HIGH);
    digitalWrite(Sol2, LOW);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, HIGH);
    delay(6000);
    digitalWrite(Sol1, LOW);
    digitalWrite(Sol2, LOW);
    delay(200);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, HIGH);
    delay(50);
    digitalWrite(Output, HIGH);
    delay(500);
    digitalWrite(Output, LOW);
  }

  if ((Purple == HIGH) && (Blue == LOW)) {
    digitalWrite(Sol1, HIGH);
    digitalWrite(Sol2, HIGH);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    delay(3000);
    digitalWrite(Sol1, LOW);
    digitalWrite(Sol2, LOW);
    delay(500);
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, HIGH);
    delay(50);
    digitalWrite(Output, HIGH);
    delay(500);
    digitalWrite(Output, LOW);
  }

  if ((Mix == HIGH) && (Blue == LOW)) {
    digitalWrite(Sol1, HIGH);
    digitalWrite(Sol2, HIGH);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    delay(2000);
    digitalWrite(Sol1, LOW);
    delay(50);
    digitalWrite(motorPin1, HIGH);
    delay(4000);
    digitalWrite(Sol2, LOW);
    delay(50);
    digitalWrite(motorPin2, HIGH);
    delay(50);
    digitalWrite(Output, HIGH);
    delay(500);
    digitalWrite(Output, LOW);
  }
}
