#include <Wire.h>

#define SLAVE_ADDRESS 0x40

static int cmd = 0;
static unsigned long rcv_count = 0;
static byte err = 0;

const int8_t rcv_vals[128] =
  {241, 187, 147, 213, 106, 157, 70, 187,
  188, 22, 78, 149, 200, 185, 21, 173,
  125, 117, 105, 75, 77, 76, 201, 94,
  119, 124, 228, 177, 61, 123, 132, 18,
  186, 32, 145, 100, 20, 67, 101, 14,
  69, 61, 122, 203, 145, 212, 235, 134,
  144, 22, 192, 41, 131, 174, 140, 30,
  146, 42, 113, 18, 169, 61, 196, 124,
  249, 139, 197, 94, 192, 116, 3, 26,
  216, 72, 77, 162, 145, 240, 196, 159,
  163, 123, 170, 32, 60, 220, 1, 176,
  127, 56, 208, 141, 98, 180, 96, 28,
  44, 205, 85, 2, 94, 147, 215, 38,
  13, 25, 160, 251, 70, 131, 24, 60,
  17, 199, 15, 196, 66, 75, 244, 39,
  177, 95, 164, 175, 44, 107, 193, 208};

void setup (void) {
  // I2Cの速度を設定
  Wire.setClock(14400L);
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
  Wire.write(err);
  err = 0;

  // リセット処理
  if(cmd == 255) rcv_count = 0;
}

// 受信処理
void receive(int n){

  // cmdを受信
  cmd = Wire.read();

  // dataを受信
  for(int i = 0; i < n-1; i++){
    err |= (Wire.read() ^ (byte)rcv_vals[rcv_count%31]);
    rcv_count++;
  }
}


