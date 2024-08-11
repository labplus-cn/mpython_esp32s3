# 本文件会被顶层CMakeList.txt包含
# 可以在本文件定义一些板级源文件及目录

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    ${SDKCONFIG_IDF_VERSION_SPECIFIC}
    boards/sdkconfig.ble 
    boards/sdkconfig.240mhz
    boards/labplus_classroom_kit_nanjing/sdkconfig.spiram 
    boards/labplus_classroom_kit_nanjing/sdkconfig.board
)

set(MICROPY_SOURCE_BOARD
    ${MICROPY_BOARD_DIR}/main.c
)

set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
