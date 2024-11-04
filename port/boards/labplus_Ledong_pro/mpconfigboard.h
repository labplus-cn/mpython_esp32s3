#ifndef MICROPY_HW_BOARD_NAME
// Can be set by mpconfigboard.cmake.
#define MICROPY_HW_BOARD_NAME               "labplus Ledong pro"
#endif
#define MICROPY_HW_MCU_NAME                 "ESP32S3"

// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (1)

#define MICROPY_HW_I2C0_SCL                 (35)
#define MICROPY_HW_I2C0_SDA                 (34)

#ifndef MICROPY_PY_ESP_MUSIC
#define MICROPY_PY_ESP_MUSIC                   (1)
#endif

#ifndef MICROPY_PY_AUDIO
#define MICROPY_PY_AUDIO                    (1)
#endif