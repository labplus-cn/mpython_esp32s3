if(NOT ADF_PATH)
    get_filename_component(ADF_PATH ${CMAKE_CURRENT_LIST_DIR}/../../../../esp-adf ABSOLUTE)
endif()

if(NOT MPY_PORT_DIR)
    get_filename_component(MPY_PORT_DIR ${CMAKE_CURRENT_LIST_DIR}/../../.. ABSOLUTE)
endif()

set(ADF_COMPS ${ADF_PATH}/components)

set(USE_ESP_ADF ON)

set(srcs
    board_pins_config.c
    board_init.c
)

set(includes
    ${MPY_PORT_DIR}/boards/labplus_classroom_kit_nanjing/audio
)

idf_component_register(
    SRCS "${srcs}"
    INCLUDE_DIRS "${includes}"
    REQUIRES audio_hal audio_board audio_pipeline audio_sal driver esp-adf-libs esp_http_client
)
