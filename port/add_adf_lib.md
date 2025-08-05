1. 添加user board
2. 不编译没用到的codec驱动

1. port下添加adf_components目录，把需要用到的adf component从adf项目复制过来。
2. 在需要adf功能的板子的mpconfigbard.cmake下导入adf component:
```bash
    set(ADF_COMPONENTS 
        ${MPY_PORT_DIR}/adf_components/adf_utils
        ${MPY_PORT_DIR}/adf_components/audio_board
        ${MPY_PORT_DIR}/adf_components/audio_hal
        ${MPY_PORT_DIR}/adf_components/audio_pipeline
        ${MPY_PORT_DIR}/adf_components/audio_recorder
        ${MPY_PORT_DIR}/adf_components/audio_sal
        ${MPY_PORT_DIR}/adf_components/audio_stream
        ${MPY_PORT_DIR}/adf_components/clouds
        ${MPY_PORT_DIR}/adf_components/display_service
        ${MPY_PORT_DIR}/adf_components/dueros_service
        ${MPY_PORT_DIR}/adf_components/esp_actions
        ${MPY_PORT_DIR}/adf_components/esp_dispatcher
        ${MPY_PORT_DIR}/adf_components/esp_peripherals
        ${MPY_PORT_DIR}/adf_components/esp-adf-libs
        ${MPY_PORT_DIR}/adf_components/esp-sr 
        ${MPY_PORT_DIR}/adf_components/tone_partition 
        ${MPY_PORT_DIR}/adf_components/wifi_service)

    list(APPEND EXTRA_COMPONENT_DIRS
        ${ADF_COMPONENTS}
        ${MPY_PORT_DIR}/boards/labplus_classroom_kit_nanjing/audio)
```
3. port/boards对应板下，放入板级相关文件夹audio
4. builtin中放入音频模块。
5. main组件添加对adf相关组件的依赖。