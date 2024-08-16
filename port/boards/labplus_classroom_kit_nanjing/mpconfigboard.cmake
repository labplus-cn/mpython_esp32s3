# 本文件会被顶层CMakeList.txt包含
# 可以在本文件定义一些板级源文件及目录

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    ${SDKCONFIG_IDF_VERSION_SPECIFIC}
    boards/sdkconfig.ble 
    boards/sdkconfig.240mhz
    boards/labplus_Ledong/sdkconfig.board
    boards/labplus_classroom_kit_nanjing/sdkconfig.spiram 
    boards/labplus_classroom_kit_nanjing/sdkconfig.board
)

if(NOT MPY_PORT_DIR)
    get_filename_component(MPY_PORT_DIR ${CMAKE_CURRENT_LIST_DIR}/../.. ABSOLUTE)
endif()

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
    ${MPY_PORT_DIR}/builtins/modtts.c
    ${MPY_PORT_DIR}/builtins/modasr.c
)

set(MICROPY_SOURCE_BOARD_DIR
    ${MPY_PORT_DIR}/drivers
    ${MPY_PORT_DIR}/lib
    ${MPY_PORT_DIR}/builtins

)

set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
