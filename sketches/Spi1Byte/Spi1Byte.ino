#include <SPI.h>

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
}

// SPI割り込み処理
ISR (SPI_STC_vect) {
}


