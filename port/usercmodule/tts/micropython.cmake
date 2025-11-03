add_library(usermod_tts INTERFACE)

target_sources(usermod_tts INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/src/tts.c
        ${CMAKE_CURRENT_LIST_DIR}/src/module.c
)

target_include_directories(usermod_tts INTERFACE
        ${CMAKE_CURRENT_LIST_DIR}/../tts/src
)

target_link_libraries(usermod INTERFACE usermod_tts)
