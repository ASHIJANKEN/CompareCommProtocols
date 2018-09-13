#define INPUT_PIN 4
#define OUTPUT_PIN 7

void setup() {
  Serial.begin(9600);
  pinMode(INPUT_PIN, INPUT_PULLUP);
  pinMode(OUTPUT_PIN, OUTPUT);
  digitalWrite(OUTPUT_PIN, HIGH);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  //リセットピンの立ち下がりを検知
  if(digitalRead(INPUT_PIN)==LOW){
    //Arduinoに立ち下がり信号を送る
    digitalWrite(OUTPUT_PIN, LOW);
    digitalWrite(LED_BUILTIN, LOW);    
    delay(100);
    digitalWrite(OUTPUT_PIN, HIGH);
    digitalWrite(LED_BUILTIN, HIGH);    

    //RPiの信号がHIGHに戻るまで待機
    while(digitalRead(INPUT_PIN)==LOW){
      ;
    }
  }
}
