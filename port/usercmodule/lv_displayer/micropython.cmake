add_library(usermod_display INTERFACE)

target_sources(usermod_display INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/modlvdisplayer.c
)

target_include_directories(usermod_display INTERFACE
        ${IDF_PATH}/components/esp_lcd/include/
        ${CMAKE_CURRENT_LIST_DIR}/../esp-who/esp-who/components/modules/lcd
        ${CMAKE_CURRENT_LIST_DIR}/../lv_binding_micropython/lvgl
        ${CMAKE_CURRENT_LIST_DIR}/../lv_binding_micropython/lvgl/src
)

target_link_libraries(usermod INTERFACE usermod_display)
