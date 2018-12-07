#include <stdio.h>
#include "esp_log.h"
#include "driver/i2c.h"
#include "sdkconfig.h"

static const char *TAG = "proctime";

#define DATA_LENGTH 512                        /* !< Data buffer length of test buffer */
#define RW_TEST_LENGTH 128                     /* !< Data length for r/w test, [0,DATA_LENGTH] */
#define DELAY_TIME_BETWEEN_ITEMS_MS 1000       /* !< delay time between different test items */

#define I2C_SLAVE_SCL_IO 26                    /* !< gpio number for i2c slave clock */
#define I2C_SLAVE_SDA_IO 25                    /* !< gpio number for i2c slave data */
#define SIGNAL GPIO_NUM_27                     /* !< gpio number for I2C additional signal */
#define I2C_SLAVE_NUM    0                     /* !< I2C port number for slave dev */
#define I2C_SLAVE_TX_BUF_LEN (2 * DATA_LENGTH) /* !< I2C slave tx buffer size */
#define I2C_SLAVE_RX_BUF_LEN (2 * DATA_LENGTH) /* !< I2C slave rx buffer size */

#define ESP_SLAVE_ADDR 0x40 /*!< ESP32 slave address, you can set any 7bit value */

/**
 * @brief i2c slave initialization
 */
static esp_err_t i2c_slave_init()
{
    int i2c_slave_port = I2C_SLAVE_NUM;
    i2c_config_t conf_slave;
    conf_slave.sda_io_num = I2C_SLAVE_SDA_IO;
    conf_slave.sda_pullup_en = GPIO_PULLUP_ENABLE;
    conf_slave.scl_io_num = I2C_SLAVE_SCL_IO;
    conf_slave.scl_pullup_en = GPIO_PULLUP_ENABLE;
    conf_slave.mode = I2C_MODE_SLAVE;
    conf_slave.slave.addr_10bit_en = 0;
    conf_slave.slave.slave_addr = ESP_SLAVE_ADDR;
    i2c_param_config(i2c_slave_port, &conf_slave);
    return i2c_driver_install(i2c_slave_port, conf_slave.mode,
                              I2C_SLAVE_RX_BUF_LEN,
                              I2C_SLAVE_TX_BUF_LEN, 0);
}

/**
 * @brief i2c additional signal initialization
 */
static esp_err_t i2c_signal_init()
{
    gpio_config_t io_conf;
    // disable interrupt
    io_conf.intr_type = GPIO_INTR_DISABLE;
    // set as output mode
    io_conf.mode = GPIO_MODE_OUTPUT;
    // bit mask of the pins that you want to set,
    io_conf.pin_bit_mask = ((1ULL<<(int)SIGNAL));
    // disable pull-down mode
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    // disable pull-up mode
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    // configure GPIO with the given settings
    return gpio_config(&io_conf);
}

void app_main()
{
    ESP_ERROR_CHECK(i2c_signal_init());
    ESP_ERROR_CHECK(i2c_slave_init());
    uint8_t *rcv = (uint8_t *)malloc(DATA_LENGTH);
    gpio_set_level((gpio_num_t)SIGNAL, 0);

    while(1){
        int ret = i2c_slave_read_buffer(I2C_SLAVE_NUM, rcv, 1, 1000 / portTICK_RATE_MS);

        // 受信処理
        if(ret == ESP_FAIL || ret == 0){
            continue;
        }

        uint8_t cmd = rcv[0];

        if(cmd == 0){
            // Master wrote data to slave.
            i2c_slave_read_buffer(I2C_SLAVE_NUM, rcv, 1, 1000 / portTICK_RATE_MS);

            // Prepare for master's reading event
            i2c_slave_write_buffer(I2C_SLAVE_NUM, rcv, 1, 1000 / portTICK_RATE_MS);
            gpio_set_level((gpio_num_t)SIGNAL, 1);

        }else if(cmd == 1){
            // Master read data from slave.

            gpio_set_level((gpio_num_t)SIGNAL, 0);
        }
    }
}
