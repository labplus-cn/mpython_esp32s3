add_library(usermod_touchpad INTERFACE)

target_sources(usermod_touchpad INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/src/focaltech_core.c
        ${CMAKE_CURRENT_LIST_DIR}/src/focaltech_upgrade_ft3x68.c
        ${CMAKE_CURRENT_LIST_DIR}/modtouchpad.c
)

target_include_directories(usermod_touchpad INTERFACE
        ${IDF_PATH}/components/driver/gpio/include
        ${CMAKE_CURRENT_LIST_DIR}/src

)

target_link_libraries(usermod INTERFACE usermod_touchpad)
