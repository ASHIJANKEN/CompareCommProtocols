#include <SPI.h>

void setup (void) {
  // Initialize SPI
  SPISettings settings(, MSBFIRST, SPI_MODE1);

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
}

// Interrupt function for SPI
ISR (SPI_STC_vect) {
}
