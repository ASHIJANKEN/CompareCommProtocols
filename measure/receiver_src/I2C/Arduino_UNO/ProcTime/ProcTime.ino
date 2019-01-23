#include <Wire.h>

#define SLAVE_ADDRESS 0x40

static int8_t cmd;
static int send_bytes_length = 0;
static byte rcv[40];
volatile static unsigned long start_time;
volatile static unsigned long end_time;

void setup(){
  // シリアル通信を設定
  Serial.begin(9600);
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
  end_time = micros();
  Wire.write(array_ptr, send_bytes_length);
  Serial.println(end_time - start_time);
}

// 受信処理
void receive(int n){

  // cmdを受信
  send_bytes_length = Wire.read();

  // dataを受信
  for(int i = 0; i < n-1; i++){
    rcv[i] = Wire.read();
    start_time = micros();
  }
}


