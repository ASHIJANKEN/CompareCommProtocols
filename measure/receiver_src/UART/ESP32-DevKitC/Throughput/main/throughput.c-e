#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"

#define EX_UART_NUM UART_NUM_0
#define TXD_PIN  (UART_PIN_NO_CHANGE)
#define RXD_PIN  (UART_PIN_NO_CHANGE)
#define RTS_PIN  (UART_PIN_NO_CHANGE)
#define CTS_PIN  (UART_PIN_NO_CHANGE)

#define BUF_SIZE 65

const int8_t rcv_vals[128] ={
    241, 187, 147, 213, 106, 157, 70, 187,
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
    177, 95, 164, 175, 44, 107, 193, 208
};

static void echo_task()
{
    /* Configure parameters of an UART driver,
     * communication pins and install the driver */
    uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };
    uart_param_config(EX_UART_NUM, &uart_config);
    uart_set_pin(EX_UART_NUM, TXD_PIN, RXD_PIN, RTS_PIN, CTS_PIN);
    uart_driver_install(EX_UART_NUM, BUF_SIZE * 2, 0, 0, NULL, 0);

    // Configure a temporary buffer for the incoming data
    uint8_t *data = (uint8_t *) malloc(BUF_SIZE);

    while (1) {
        // Check if any data has arrived
        int length = 0;
        uart_get_buffered_data_len(EX_UART_NUM, (size_t*)&length);
        if(length < 1){
            continue;
        }

        // Read data from the UART
        uart_read_bytes(EX_UART_NUM, data, length, 1000 / portTICK_RATE_MS);
//        uart_flush_input(EX_UART_NUM);

        // Check data
        uint8_t err = 0;
        for(int i = 0; i < length; i++){
            err |= (data[i] ^ (uint8_t)rcv_vals[i&127]);
        }

        // Write data back to the UART
        uart_write_bytes(EX_UART_NUM, (const char *)&err, 1);
    }
}

void app_main()
{
    xTaskCreate(echo_task, "uart_echo_task", 1024, NULL, 10, NULL);
}
