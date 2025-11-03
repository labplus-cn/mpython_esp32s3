新建板：mpython_pro(掌控板pro)
修改本文档，记录添加板相关修改。

1. port/boards下：复制labplus_fro_xuejing到mpython_pro，一些通用修改参阅labplus_fro_xuejing下board.md。

2. 修改bsp_audio_board.h/c文件：
    - 修改IIC IIS引脚定义
3. 在mpython_pro目录下搜labplus_for_xuejing,替换成mpython_pro。
4. 搜索CONFIG_LABPLUS_FOR_XUEJING_BOARD,替换为CONFIG_MPYTHON_PRO_BOARD,用于板相关编译配置
   - sdkconfig.board
   - port/drivers/audio/include/bsp_audio.h加入：
    #elif CONFIG_MPYTHON_PRO_BOARD
    #include "mpython_pro/bsp_audio_board.h"
5. 修改mpconfigboard.h
   mpconfigport.h做了些公用配置，其包含了mpconfigboard.h，用于做板级配置，修改此文件：
   - 加入音乐模块
   - 修改板名信息
6. 修改boards/mpython_pro/mpconfigboard.cmake
   - 设置目标芯片为s3
      set(IDF_TARGET esp32s3)
   - 修改SDKCONFIG_DEFAULTS变量，添加相关配置
   - 添加一些路径变量
   - 添加待编译的文件及路径变量
   - 设置manifest.py路径
7. 修改sdkconfig.board
   - 配置flash、分区表位置什么的。
   - 修改配置板名：
8. 修改sdkconfig.usb
   配置CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y，以实现内置usb-uart/jtag为repl固件自动下载功能
9.  修改sdkconfig.psram
   根据芯片型号正确配置片内或片外PSRAM。
   参考：
   硬件：https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/esp-hardware-design-guidelines-zh_CN-master-esp32s3.pdf
   配置：https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32s3/api-guides/flash_psram_config.html#:~:text=%E8%A6%81%E5%90%AF%E5%8A%A8%20PSRAM%EF%BC%8C
10. 配置分区表
11. 集成python模块
12. 加入labplus builtin module
    - machine_pin.c
      添加mpython基于esp32s3引脚
    - drivers/startup/i2c_master.h
      修改i2c引脚
13. 加入python库
    - mpython
      修改：
      i2c引脚
      mpython引脚
      各外设引脚
14. 
   