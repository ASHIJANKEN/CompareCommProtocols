void setup (void) {
  // シリアル通信を設定
  Serial.begin(14400);
}

void loop(){
}

// シリアル割り込み処理
void serialEvent(){
  int8_t rcv = Serial.read();
  Serial.write(rcv);
}

