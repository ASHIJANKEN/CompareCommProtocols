#include <SPI.h>

#define UPPER_READ 0
#define LOWER_READ 1
#define DATA_READ 2
#define ACK_SEND 3

static int status = UPPER_READ;
static byte upper_lng = 0;
static byte lower_lng = 0;
static int16_t lng = 0;
static unsigned long rcv_count = 0;
static int8_t err = 0;

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

void setup(){
  // Initialize SPI
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE1);

  // Set MISO as output
  pinMode(MISO, OUTPUT);
  // Enable SPI
  SPCR |= _BV(SPE);
  // Set SS as input
  pinMode(SS, INPUT);
  // Start interrupt function for SPI
  SPI.attachInterrupt();
}

void loop(){
  // SPI通信が終了したら変数をリセットする
  if(digitalRead(SS) == true){
    status = UPPER_READ;
    rcv_count = 0;
    err = 0;
  }
}

// SPI割り込み処理
ISR(SPI_STC_vect){
  switch(status){
    case UPPER_READ:
      upper_lng = SPDR;
      status = LOWER_READ;
      break;
    case LOWER_READ:
      lower_lng = SPDR;
      lng = (upper_lng << 0x8) | lower_lng;
      status = DATA_READ;
      break;
    case DATA_READ:
      // 受信エラーを計算
      err |= (SPDR ^ (byte)rcv_vals[rcv_count&127]);
      rcv_count++;

      // 送信処理に入る
      if(rcv_count==lng){
        SPDR = err;
        status = ACK_SEND;
      }
      break;
    case ACK_SEND:
      status = UPPER_READ;
      // リセット処理
      err = 0;
      rcv_count = 0;
      break;
  }
}