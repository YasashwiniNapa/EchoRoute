/*
  EchoRoute Hardware

  MakeOH2025
*/
// VARIABLES
int buzzer=8; // I/O pin for buzzer
int bright = 30;

int forward = 2; // green
int back = 5; // red
int left = 3; // blue
int right = 4; // yellow

bool FORWARD = 0;
bool BACKWARD = 0;
bool LEFT = 0;
bool RIGHT = 1;

void setup() {
  pinMode(buzzer,OUTPUT); // sets pin as output
  Serial.begin(115200);
  Serial.setTimeout(1);
}

// the loop function runs over and over again forever
void loop() {
    if (Serial.available() > 0) {
      String message = Serial.readStringUntil('\n');
      Serial.print("Received: ");
      Serial.println(message);
    }
    if (FORWARD){
      analogWrite(forward, bright);
    }
    else if (BACKWARD){
      analogWrite(back, bright);
    }
    else if (LEFT){
      analogWrite(left, bright);
    }
    else if (RIGHT){
      analogWrite(right, bright);
    }
    digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
    delay(500);                      // wait for a second
    digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
    delay(1000);                      // wait for a second
    unsigned char i,j; // defines variable
  while(1){
    for(i=0;i<80;i++) { // makes frequency sound
      tone(buzzer, 440);
      delay(700); // 1ms delay
      noTone(buzzer);
      delay(800); // 1ms delay
  }
}
}
