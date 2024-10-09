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

if(NOT MPY_PORT_DIR)
    get_filename_component(MPY_PORT_DIR ${CMAKE_CURRENT_LIST_DIR}/../.. ABSOLUTE)
endif()

if(NOT ADF_PATH)
    get_filename_component(ADF_PATH ${CMAKE_CURRENT_LIST_DIR}/../../../esp-adf ABSOLUTE)
endif()

set(ADF_COMPS ${ADF_PATH}/components)

set(MICROPY_SOURCE_BOARD
    ${MICROPY_BOARD_DIR}/main.c
    # ${MPY_PORT_DIR}/drivers/startup/00030.c
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
    # ${MPY_PORT_DIR}/builtins/modtts.c
    # ${MPY_PORT_DIR}/builtins/modasr.c
)

set(MICROPY_SOURCE_BOARD_DIR
    ${MPY_PORT_DIR}/drivers
    ${MPY_PORT_DIR}/lib
    ${MPY_PORT_DIR}/builtins
    ${MPY_PORT_DIR}/boards/labplus_classroom_kit_nanjing/audio
    ${ADF_COMPS}/esp-adf-libs/esp_audio/include
    ${ADF_COMPS}/esp-adf-libs/esp_codec/include/codec
    ${ADF_COMPS}/esp-adf-libs/esp_codec/include/processing
    ${ADF_COMPS}/esp-adf-libs/media_lib_sal/include
    ${ADF_COMPS}/esp-adf-libs/media_lib_sal/include/port
    ${ADF_COMPS}/esp-adf-libs/esp_muxer/include
    ${ADF_COMPS}/audio_pipeline/include
    ${ADF_COMPS}/audio_sal/include
    ${ADF_COMPS}/audio_stream/include
    ${ADF_COMPS}/audio_recorder/include
    ${ADF_COMPS}/esp-sr/src/include
    ${ADF_COMPS}/esp-sr/esp-tts/esp_tts_chinese/include
    # if(IDF_TARGET STREQUAL "esp32")
    ${ADF_COMPS}/esp-sr/include/esp32
    # elseif(IDF_TARGET STREQUAL "esp32s3")
    # ${ADF_COMPS}/esp-sr/include/esp32s3
    # endif()
    ${ADF_COMPS}/audio_recorder/include
    ${ADF_COMPS}/audio_hal/include
)

list(APPEND EXTRA_COMPONENT_DIRS
        ${ADF_PATH}/components/audio_pipeline
        ${ADF_PATH}/components/audio_sal
        ${ADF_PATH}/components/esp-adf-libs
        ${ADF_PATH}/components/esp-sr
        ${ADF_PATH}/components/audio_recorder
        ${MPY_PORT_DIR}/boards/labplus_classroom_kit_nanjing/audio
        )

set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
