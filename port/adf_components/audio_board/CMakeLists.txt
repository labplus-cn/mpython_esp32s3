set(COMPONENT_ADD_INCLUDEDIRS ./include)

# Edit following two lines to set component requirements (see docs)
set(COMPONENT_REQUIRES driver)
set(COMPONENT_PRIV_REQUIRES  audio_sal audio_hal)

if (CONFIG_ESP_LYRAT_V4_3_BOARD)
message(STATUS "Current board name is " CONFIG_ESP_LYRAT_V4_3_BOARD)
list(APPEND COMPONENT_ADD_INCLUDEDIRS ./lyrat_v4_3)
set(COMPONENT_SRCS
./lyrat_v4_3/board.c
./lyrat_v4_3/board_pins_config.c
)
endif()

if (CONFIG_ESP32_S3_BOX_BOARD)
message(STATUS "Current board name is " CONFIG_ESP32_S3_BOX_BOARD)
list(APPEND COMPONENT_ADD_INCLUDEDIRS ./esp32_s3_box)
set(COMPONENT_SRCS
./esp32_s3_box/board.c
./esp32_s3_box/board_pins_config.c
)
endif()

if (CONFIG_LABPLUS_CLASSROOM_KIT_NANJING_BOARD)
message(STATUS "Current board name is " CONFIG_LABPLUS_CLASSROOM_KIT_NANJING_BOARD)
list(APPEND COMPONENT_ADD_INCLUDEDIRS ./labplus_classroom_kit_nanjing_v1_0)
set(COMPONENT_SRCS
./labplus_classroom_kit_nanjing_v1_0/board.c
./labplus_classroom_kit_nanjing_v1_0/board_pins_config.c
)
endif()

if (CONFIG_LABPLUS_LEDONG_PRO_BOARD)
message(STATUS "Current board name is " CONFIG_LABPLUS_LEDONG_PRO_BOARD)
list(APPEND COMPONENT_ADD_INCLUDEDIRS ./labplus_Ledong_pro)
set(COMPONENT_SRCS
./labplus_Ledong_pro/board.c
./labplus_Ledong_pro/board_pins_config.c
)
endif()

if (CONFIG_LABPLUS_LEDONG_PSRAM_BOARD)
message(STATUS "Current board name is " CONFIG_LABPLUS_LEDONG_PSRAM_BOARD)
list(APPEND COMPONENT_ADD_INCLUDEDIRS ./labplus_Ledong_psram)
set(COMPONENT_SRCS
./labplus_Ledong_psram/board.c
./labplus_Ledong_psram/board_pins_config.c
)
endif()

register_component()
