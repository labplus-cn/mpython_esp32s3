# 本文件会被顶层CMakeList.txt包含
# 可以在本文件定义一些板级源文件及目录
set(IDF_TARGET esp32s3)

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    ${SDKCONFIG_IDF_VERSION_SPECIFIC}
    boards/sdkconfig.ble 
    boards/sdkconfig.240mhz
    boards/labplus_Ledong_v2/sdkconfig.spiram 
    boards/labplus_Ledong_v2/sdkconfig.board
    # boards/labplus_Ledong_v2/sdkconfig.usb
)

if(NOT MPY_PORT_DIR)
    get_filename_component(MPY_PORT_DIR ${CMAKE_CURRENT_LIST_DIR}/../.. ABSOLUTE)
endif()

if(NOT ADF_PATH)
    get_filename_component(ADF_PATH ${CMAKE_CURRENT_LIST_DIR}/../../../esp-adf ABSOLUTE)
endif()

set(ADF_COMPS ${ADF_PATH}/components)

set(MICROPY_SOURCE_BOARD
    # ${MICROPY_BOARD_DIR}/main.c
    ${MICROPY_BOARD_DIR}/bsp_audio_board.c
    ${MPY_PORT_DIR}/drivers/audio/vfs_lfs2.c
    ${MPY_PORT_DIR}/drivers/audio/wave_head.c
    ${MPY_PORT_DIR}/drivers/audio/vfs_fatfs.c
    ${MPY_PORT_DIR}/drivers/audio/wav_codec.c
    ${MPY_PORT_DIR}/drivers/audio/player.c
    ${MPY_PORT_DIR}/drivers/audio/recorder.c
    ${MPY_PORT_DIR}/drivers/audio/audio.c
    ${MPY_PORT_DIR}/drivers/audio/ringbuf.c
    ${MPY_PORT_DIR}/drivers/audio/audio_mem.c
    ${MPY_PORT_DIR}/drivers/audio/simple_file_decoder.c
    ${MPY_PORT_DIR}/drivers/audio/http_stream.c
    ${MPY_PORT_DIR}/drivers/audio/simple_http_decoder.c
    # ${MPY_PORT_DIR}/drivers/startup/logo.c
    # ${MPY_PORT_DIR}/drivers/startup/i2c_master.c
    # ${MPY_PORT_DIR}/drivers/startup/oled.c
    # ${MPY_PORT_DIR}/drivers/startup/startup.c 
    # ${MPY_PORT_DIR}/drivers/rfid/mfrc522.c
    # ${MPY_PORT_DIR}/lib/utils/pyexec.c
    ${MPY_PORT_DIR}/builtins/main.c
    ${MPY_PORT_DIR}/builtins/modmusictunes.c
    ${MPY_PORT_DIR}/builtins/modmusic.c
    ${MPY_PORT_DIR}/builtins/esp32_nvs.c
    ${MPY_PORT_DIR}/builtins/machine_pin.c
    ${MPY_PORT_DIR}/builtins/machine_touchpad.c
    ${MPY_PORT_DIR}/builtins/modframebuf.c
    ${MPY_PORT_DIR}/builtins/modaudio.c
    # ${MPY_PORT_DIR}/builtins/modrfid.c
    # ${MPY_PORT_DIR}/builtins/mod_audio/audio_player.c
    # ${MPY_PORT_DIR}/builtins/mod_audio/audio_recorder.c 
    # ${MPY_PORT_DIR}/builtins/mod_audio/vfs_stream.c 
    # ${MPY_PORT_DIR}/builtins/mod_audio/modaudio.c
)

set(MICROPY_SOURCE_BOARD_DIR
    ${MPY_PORT_DIR}/drivers
    ${MPY_PORT_DIR}/drivers/audio/include
    ${MPY_PORT_DIR}/lib
    ${MPY_PORT_DIR}/builtins
    ${MPY_PORT_DIR}/boards
)

set(LABPLUS_LEDONG_V2_BOARD ON)

list(APPEND EXTRA_COMPONENT_DIRS ${MPY_PORT_DIR}/usercmodule/esp-who/esp-who/components/esp-code-scanner)
list(APPEND EXTRA_COMPONENT_DIRS ${MPY_PORT_DIR}/usercmodule/esp-who/esp-who/components/esp-dl)
list(APPEND EXTRA_COMPONENT_DIRS ${MPY_PORT_DIR}/usercmodule/esp-who/esp-who/components/modules)
list(APPEND EXTRA_COMPONENT_DIRS ${MPY_PORT_DIR}/usercmodule/esp-who/esp-who/components/fb_gfx)
list(APPEND EXTRA_COMPONENT_DIRS ${MPY_PORT_DIR}/usercmodule/esp-who/esp-who/components/esp32-camera)

set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
