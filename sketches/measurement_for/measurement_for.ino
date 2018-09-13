#define REPEAT 10000000

void setup() {
Serial.begin(9600);
}

void loop() {
  unsigned long start_all = micros();
  unsigned long end_all = micros();
  unsigned long start_for = micros();
  unsigned long end_for = micros();
  //何らかの文字の入力があるまで待機
  while(!Serial.available()){
  }
  //入力文字列を読みだしてバッファを空にする
  while(Serial.available()){
    Serial.read();
  }
  //ちょっと待つ(特に意味はないけどシリアル通信を休憩)
  delay(1000);

  //*******************************
  // 計測開始
  //*******************************

  //forループREPEAT回+for文をREPEAT回またぐ時間を計測
  Serial.println("start");
  start_all = micros();
  for(long i=0;i<REPEAT;i++){
    for(int i=0; i<0;i++){
    }
  }
  end_all = micros();

  //forループREPEAT回にかかる時間を計測
  start_for = micros();
  for(long i=0;i<REPEAT;i++){
  }
  end_for = micros();

  //for文をREPEAT回またぐ時間を計算
  unsigned long proc_for = (end_all - start_all) - (end_for - start_for);
  Serial.print("for文を");
  Serial.print(REPEAT);
  Serial.print("回またぐ時間: ");
  Serial.println(proc_for);
  Serial.print("受信から送信の間にかかる時間: ");
  Serial.println((float)proc_for / REPEAT);
  
  //計測終了
  Serial.println("end");
  while(true){
  }
}
