if(MPYTHON_PRO_BOARD OR LABPLUS_LEDONG_V2_BOARD OR LABPLUS_XUNFEI_JS_PRIMARY_BOARD OR LABPLUS_XUNFEI_JS_MIDDLE_BOARD)
# Add the lv_binding_micropython.
include(${CMAKE_CURRENT_LIST_DIR}/lv_binding_micropython/micropython.cmake)
# add esp-who module
include(${CMAKE_CURRENT_LIST_DIR}/esp-who/micropython.cmake)
endif()

# add lv displayer driver module
include(${CMAKE_CURRENT_LIST_DIR}/lv_displayer/micropython.cmake)

# add tts module
include(${CMAKE_CURRENT_LIST_DIR}/tts/micropython.cmake)

# add wake up and speech command module
include(${CMAKE_CURRENT_LIST_DIR}/speechCommand/micropython.cmake)

# add rfid module
include(${CMAKE_CURRENT_LIST_DIR}/rfid/micropython.cmake)

if(LABPLUS_LEDONG_V2_BOARD)
include(${CMAKE_CURRENT_LIST_DIR}/touchpad/micropython.cmake)
endif()
