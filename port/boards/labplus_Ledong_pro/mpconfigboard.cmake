set(IDF_TARGET esp32s3)

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    ${SDKCONFIG_IDF_VERSION_SPECIFIC}
    boards/labplus_Ledong_pro/sdkconfig.usb
    boards/sdkconfig.ble
    boards/sdkconfig.240mhz
    # boards/sdkconfig.spiram
    boards/labplus_Ledong_pro/sdkconfig.spiram_sx
    boards/labplus_Ledong_pro/sdkconfig.board
)

if(MICROPY_BOARD_VARIANT STREQUAL "SPIRAM_OCT")
    set(SDKCONFIG_DEFAULTS
        ${SDKCONFIG_DEFAULTS}
        boards/sdkconfig.240mhz
        boards/sdkconfig.spiram_oct
    )

    list(APPEND MICROPY_DEF_BOARD
        MICROPY_HW_BOARD_NAME="Generic ESP32S3 module with Octal-SPIRAM"
    )
endif()

if(MICROPY_BOARD_VARIANT STREQUAL "FLASH_4M")
    set(SDKCONFIG_DEFAULTS
        ${SDKCONFIG_DEFAULTS}
        boards/ESP32_GENERIC_S3/sdkconfig.flash_4m
    )
endif()

if(NOT MPY_PORT_DIR)
    get_filename_component(MPY_PORT_DIR ${CMAKE_CURRENT_LIST_DIR}/../.. ABSOLUTE)
endif()

if(NOT ADF_PATH)
    get_filename_component(ADF_PATH ${CMAKE_CURRENT_LIST_DIR}/../../../esp-adf ABSOLUTE)
endif()

set(ADF_COMPS ${ADF_PATH}/components)

set(MICROPY_SOURCE_BOARD
    ${MICROPY_BOARD_DIR}/main.c
    ${MPY_PORT_DIR}/drivers/startup/00030.c
    ${MPY_PORT_DIR}/drivers/startup/i2c_master.c
    ${MPY_PORT_DIR}/drivers/startup/oled.c
    ${MPY_PORT_DIR}/drivers/startup/startup.c 
    ${MPY_PORT_DIR}/lib/utils/pyexec.c
    ${MPY_PORT_DIR}/builtins/modmusictunes.c
    ${MPY_PORT_DIR}/builtins/modmusic.c
    ${MPY_PORT_DIR}/builtins/esp32_nvs.c
    ${MPY_PORT_DIR}/builtins/machine_pin.c
    ${MPY_PORT_DIR}/builtins/machine_touchpad.c
    ${MPY_PORT_DIR}/builtins/modframebuf.c
)

set(MICROPY_SOURCE_BOARD_DIR
    ${MPY_PORT_DIR}/drivers
    ${MPY_PORT_DIR}/lib
    ${MPY_PORT_DIR}/builtins
    ${MPY_PORT_DIR}/boards/labplus_Ledong_pro/audio
)

list(APPEND EXTRA_COMPONENT_DIRS
        ${ADF_PATH}/components/audio_pipeline
        ${ADF_PATH}/components/audio_sal
        ${ADF_PATH}/components/esp-adf-libs
        ${ADF_PATH}/components/esp-sr
        ${MPY_PORT_DIR}/boards/labplus_Ledong_pro/audio
        )

set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)