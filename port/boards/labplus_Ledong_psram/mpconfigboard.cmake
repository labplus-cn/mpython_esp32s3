# 本文件会被顶层CMakeList.txt包含
# 可以在本文件定义一些板级源文件及目录

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    ${SDKCONFIG_IDF_VERSION_SPECIFIC}
    boards/sdkconfig.ble 
    boards/sdkconfig.240mhz
    boards/labplus_Ledong_psram/sdkconfig.spiram 
    boards/labplus_Ledong_psram/sdkconfig.board
)

if(NOT MPY_PORT_DIR)
    get_filename_component(MPY_PORT_DIR ${CMAKE_CURRENT_LIST_DIR}/../.. ABSOLUTE)
endif()

if(NOT ADF_PATH)
    get_filename_component(ADF_PATH ${CMAKE_CURRENT_LIST_DIR}/../../../esp-adf ABSOLUTE)
endif()

set(ADF_COMPS ${ADF_PATH}/components)

set(MICROPY_SOURCE_BOARD
    ${MICROPY_BOARD_DIR}/main.c
    # ${MPY_PORT_DIR}/drivers/startup/logo.c
    # ${MPY_PORT_DIR}/drivers/startup/i2c_master.c
    # ${MPY_PORT_DIR}/drivers/startup/oled.c
    # ${MPY_PORT_DIR}/drivers/startup/startup.c 
    ${MPY_PORT_DIR}/lib/utils/pyexec.c
    ${MPY_PORT_DIR}/builtins/modmusictunes.c
    ${MPY_PORT_DIR}/builtins/modmusic.c
    ${MPY_PORT_DIR}/builtins/esp32_nvs.c
    ${MPY_PORT_DIR}/builtins/machine_pin.c
    ${MPY_PORT_DIR}/builtins/machine_touchpad.c
    ${MPY_PORT_DIR}/builtins/modframebuf.c
    ${MPY_PORT_DIR}/builtins/mod_audio/audio_player.c
    ${MPY_PORT_DIR}/builtins/mod_audio/audio_recorder.c 
    ${MPY_PORT_DIR}/builtins/mod_audio/vfs_stream.c 
    ${MPY_PORT_DIR}/builtins/mod_audio/modaudio.c 
)

set(MICROPY_SOURCE_BOARD_DIR
    ${MPY_PORT_DIR}/drivers
    ${MPY_PORT_DIR}/lib
    ${MPY_PORT_DIR}/builtins
    ${MPY_PORT_DIR}/boards/labplus_classroom_kit_nanjing/audio
)

# if(CONFIG_LABPLUS_CLASSROOM_KIT_NANJING_BOARD)
set(ADF_COMPONENTS 
    ${MPY_PORT_DIR}/adf_components/adf_utils
    ${MPY_PORT_DIR}/adf_components/audio_board
    ${MPY_PORT_DIR}/adf_components/audio_hal
    ${MPY_PORT_DIR}/adf_components/audio_pipeline
    ${MPY_PORT_DIR}/adf_components/audio_recorder
    ${MPY_PORT_DIR}/adf_components/audio_sal
    ${MPY_PORT_DIR}/adf_components/audio_stream
    ${MPY_PORT_DIR}/adf_components/clouds
    ${MPY_PORT_DIR}/adf_components/display_service
    ${MPY_PORT_DIR}/adf_components/dueros_service
    ${MPY_PORT_DIR}/adf_components/esp_actions
    ${MPY_PORT_DIR}/adf_components/esp_dispatcher
    ${MPY_PORT_DIR}/adf_components/esp_peripherals
    ${MPY_PORT_DIR}/adf_components/esp-adf-libs
    ${MPY_PORT_DIR}/adf_components/esp-sr 
    ${MPY_PORT_DIR}/adf_components/tone_partition 
    ${MPY_PORT_DIR}/adf_components/wifi_service)
# endif()

list(APPEND EXTRA_COMPONENT_DIRS
    ${ADF_COMPONENTS}
    ${MPY_PORT_DIR}/boards/labplus_classroom_kit_nanjing/audio)

set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
