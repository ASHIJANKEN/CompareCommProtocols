#include <Wire.h>

#define SLAVE_ADDRESS 0x40

static int send_bytes_length = 0;
static byte rcv[40];

void setup(){
  // I2Cの速度を設定
  Wire.setClock(L);
  // I2Cパスにスレーブとして接続
  Wire.begin(SLAVE_ADDRESS);
  // マスタからデータが送られてきたときのハンドラを設定
  Wire.onReceive(receive);
  // マスタからリクエストが来たときのハンドラを設定
  Wire.onRequest(send);
}

void loop(){
}

// 送信処理
void send(){
  byte *array_ptr = rcv;
  Wire.write(array_ptr, send_bytes_length);
}

// 受信処理
void receive(int n){

  // cmdを受信
  send_bytes_length = Wire.read();

  // dataを受信
  for(int i = 0; i < n-1; i++){
    rcv[i] = Wire.read();
  }
}


