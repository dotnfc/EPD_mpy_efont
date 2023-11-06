#define MICROPY_HW_BOARD_NAME               "EFORE"
#define MICROPY_HW_MCU_NAME                 "ESP32-S3-N8R2"
#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT "EFORE"

#define MICROPY_PY_MACHINE_DAC              (0)

#define MICROPY_HW_I2C0_SCL                 (9)
#define MICROPY_HW_I2C0_SDA                 (8)

#define MICROPY_HW_SPI1_MOSI                (35)
#define MICROPY_HW_SPI1_MISO                (37)
#define MICROPY_HW_SPI1_SCK                 (36)

// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (1)

// MicroPython Task Stack Size
#define MICROPY_TASK_STACK_SIZE             (32 * 1024)

// 
#define MICROPY_HW_ENABLE_SDCARD            (1)
#define MICROPY_HW_SDMMC_SLOT_CONFIG() {\
    .clk = GPIO_NUM_41, \
    .cmd = GPIO_NUM_40, \
    .d0 = GPIO_NUM_42, \
    .d1 = GPIO_NUM_NC, \
    .d2 = GPIO_NUM_NC, \
    .d3 = GPIO_NUM_NC, \
    .d4 = GPIO_NUM_NC, \
    .d5 = GPIO_NUM_NC, \
    .d6 = GPIO_NUM_NC, \
    .d7 = GPIO_NUM_NC, \
    .cd = GPIO_NUM_NC, \
    .wp = GPIO_NUM_NC, \
    .width   = 1, \
    .flags = 0, \
}
