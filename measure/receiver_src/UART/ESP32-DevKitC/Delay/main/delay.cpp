void setup(){
  // シリアル通信を設定
  Serial.begin();
}

void loop(){
  // シリアル割り込み処理
  if(Serial.available()){
    int8_t rcv = Serial.read();
    Serial.write(rcv);
  }
}
