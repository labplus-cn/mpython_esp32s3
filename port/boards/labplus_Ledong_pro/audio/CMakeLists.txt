if(NOT ADF_PATH)
    get_filename_component(ADF_PATH ${CMAKE_CURRENT_LIST_DIR}/../../../../esp-adf ABSOLUTE)
endif()

if(NOT MPY_PORT_DIR)
    get_filename_component(MPY_PORT_DIR ${CMAKE_CURRENT_LIST_DIR}/../../.. ABSOLUTE)
endif()

set(ADF_COMPS ${ADF_PATH}/components)

set(srcs
    board_pins_config.c
    board_init.c
    ${ADF_COMPS}/audio_hal/driver/es8388/es8388.c
    ${ADF_COMPS}/audio_hal/driver/es8388/headphone_detect.c
    ${ADF_COMPS}/audio_hal/audio_hal.c
    ${ADF_COMPS}/audio_hal/audio_volume.c
    ${ADF_COMPS}/audio_stream/http_stream.c
    ${ADF_COMPS}/audio_stream/i2s_stream_idf5.c
    ${ADF_COMPS}/audio_stream/raw_stream.c
    ${ADF_COMPS}/audio_stream/http_playlist.c
    ${ADF_COMPS}/audio_stream/lib/gzip/gzip_miniz.c
    ${ADF_COMPS}/audio_stream/lib/hls/hls_parse.c
    ${ADF_COMPS}/audio_stream/lib/hls/hls_playlist.c
    ${ADF_COMPS}/audio_stream/lib/hls/join_path.c
    ${ADF_COMPS}/audio_stream/lib/hls/line_reader.c
    ${ADF_COMPS}/esp_peripherals/driver/i2c_bus/i2c_bus.c
)

set(includes
    ${ADF_COMPS}/audio_hal/driver/es8388/
    ${MPY_PORT_DIR}/boards/labplus_classroom_kit_nanjing/audio
    ${ADF_COMPS}/audio_board/include
    ${ADF_COMPS}/audio_hal/include
    ${ADF_COMPS}/audio_hal/driver/include
    ${ADF_COMPS}/audio_hal/driver/es8388
    ${ADF_COMPS}/audio_stream/include
    ${ADF_COMPS}/audio_stream/lib/gzip/include
    ${ADF_COMPS}/audio_stream/lib/hls/include
    ${ADF_COMPS}/esp_peripherals/include
    ${ADF_COMPS}/esp_peripherals/driver/i2c_bus
    ${ADF_COMPS}/display_service/include
    ${ADF_COMPS}/esp_dispatcher/include
)

idf_component_register(
    SRCS "${srcs}"
    INCLUDE_DIRS "${includes}"
    REQUIRES audio_pipeline audio_sal driver esp-adf-libs esp_http_client
)
