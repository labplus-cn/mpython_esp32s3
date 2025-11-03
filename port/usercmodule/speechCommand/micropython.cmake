add_library(usermod_sr INTERFACE)

target_sources(usermod_sr INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/src/sc.c
        ${CMAKE_CURRENT_LIST_DIR}/src/speech_commands_action.c
        ${CMAKE_CURRENT_LIST_DIR}/src/module.c
)

target_include_directories(usermod_sr INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/src
)

target_link_libraries(usermod INTERFACE usermod_sr)
