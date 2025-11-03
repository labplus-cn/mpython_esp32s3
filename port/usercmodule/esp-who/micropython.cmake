add_library(usermod_lcd INTERFACE)

if(LABPLUS_LEDONG_V2_BOARD OR LABPLUS_XUNFEI_JS_PRIMARY_BOARD)
        set(WHO_LCD_SRC)
elseif(MPYTHON_PRO_BOARD OR LABPLUS_XUNFEI_JS_MIDDLE_BOARD)
        set(WHO_LCD_SRC 
                ${CMAKE_CURRENT_LIST_DIR}/esp-who/components/modules/lcd/who_lcd.c
                ${CMAKE_CURRENT_LIST_DIR}/esp-who/components/modules/lcd/esp_lcd_panel_jd9853.c)
endif()

target_sources(usermod_lcd INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/mod/modlcd.c
        ${WHO_LCD_SRC}
)

set(ESP_COMPONENTS_LCD_INCLUDEDIRS
        ${IDF_PATH}/components/esp_lcd/include/
        ${IDF_PATH}/components/esp_lcd/interface/
)

set(MODULES_INCLUDEDIRS 
        ${CMAKE_CURRENT_LIST_DIR}/esp-who/components/modules/ai
        ${CMAKE_CURRENT_LIST_DIR}/esp-who/components/modules/camera
        ${CMAKE_CURRENT_LIST_DIR}/esp-who/components/modules/lcd
        ${CMAKE_CURRENT_LIST_DIR}/esp-who/components/modules/web
)

set(ESP32_CAMERA_INCLUDEDIRS 
        ${CMAKE_CURRENT_LIST_DIR}/esp-who/components/esp32-camera/driver/include
        ${CMAKE_CURRENT_LIST_DIR}/esp-who/components/esp32-camera/conversions/include
)

target_include_directories(usermod_lcd INTERFACE
        ${MODULES_INCLUDEDIRS}
        ${ESP32_CAMERA_INCLUDEDIRS}
        ${ESP_COMPONENTS_LCD_INCLUDEDIRS}
)

target_link_libraries(usermod INTERFACE usermod_lcd)

if(LABPLUS_LEDONG_V2_BOARD OR LABPLUS_XUNFEI_JS_PRIMARY_BOARD)
        add_library(usermod_sensor INTERFACE)

        target_sources(usermod_sensor INTERFACE
                ${CMAKE_CURRENT_LIST_DIR}/mod/modsensor.c
        )

        target_include_directories(usermod_sensor INTERFACE
                ${MODULES_INCLUDEDIRS}
                ${ESP32_CAMERA_INCLUDEDIRS}
        )

        target_link_libraries(usermod INTERFACE usermod_sensor)

        add_library(usermod_AIcamera INTERFACE)

        target_sources(usermod_AIcamera INTERFACE
                ${CMAKE_CURRENT_LIST_DIR}/mod/modAIcamera.c
        )

        target_include_directories(usermod_AIcamera INTERFACE
                ${MODULES_INCLUDEDIRS}
                ${ESP32_CAMERA_INCLUDEDIRS}
        )

        target_link_libraries(usermod INTERFACE usermod_AIcamera)
endif()

add_compile_options(-fdiagnostics-color=always)

