#include <SPI.h>

static unsigned long rcv_count = 0;
static boolean ss_now = true;
static boolean ss_prev = true;

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
  // 送信ポートを出力にする
  pinMode(MISO, OUTPUT);
  SPI.setBitOrder(MSBFIRST);
  // 立ち上がりでデータ読み取り
  SPI.setDataMode(SPI_MODE1);
  // SPI通信を有効化
  SPCR |= _BV(SPE);
  // SSを入力にしておく
  pinMode(SS, INPUT);
  // SPI割り込み開始
  SPI.attachInterrupt();
}

void loop(){
  // SPI通信が終了したら変数をリセットする
  ss_now = digitalRead(SS);
  if(ss_now == true && ss_prev == false){
    rcv_count = 0;
  }
  ss_prev = ss_now;
}

// SPI割り込み処理
ISR (SPI_STC_vect) {
  SPDR = (SPDR ^ (byte)rcv_vals[rcv_count&127]);
  rcv_count++;
}