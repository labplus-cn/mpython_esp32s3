升级mpython micropython
micropython v1.23.0
esp-idf v5.0.4

esp-idf采用cmake构建编译系统，micropython现支持make和使用idf.py编译系统。make内部也是调用idf.py实现，因些需要了解esp32的编译。
说明：esp32把用户的应用代码称之为项目。esp-idf不是项目的一部分。
esp32项目管理：
参考文档：https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32/api-guides/build-system.html中的构建系统章节

关于esp32的构建系统，了解：
1、项目及主程序概念
2、构建系统，idf.py
3、组件 main组件
4、示例项目
5、CMakeList.txt
sdkconfig

micropython项目架构
项目CMakeList.txt，位于port下。定义下以下内容
IDF_VERSION
MICROPY_BOARD
MICROPY_BOARD_DIR
SDKCONFIG #合并后的sdkconfig文件位置
include(${MICROPY_BOARD_DIR}/mpconfigboard.cmake) # mpconfigboard.cmake定义了1、各个板的MICROPY_FROZEN_MANIFEST位置（当然也可能没定义）2、SDKCONFIG_DEFAULTS，各个板的skdconfig.xxx集合，有这两项，就可以做下面两件事。
MICROPY_FROZEN_MANIFEST # mainfest.py位置，通常在各个板目录下，如果没有，则用boards下的。
SDKCONFIG_DEFAULT # 合并各个sdkcofig.xxx 生成sdkconfig.combobin,各个板其于sdkconfig.base，定制n个sdkconfig.xxx，用于实现不同的config，后面的配置会覆盖前面的配置？
micropython中通过sdkconfig.base + 多个sckconfig.xxx来实现不同的配置，最后合并成config.combobin
list(APPEND EXTRA_COMPONENT_DIRS main_${IDF_TARGET}) 
    重命名main组件，且通过这个区别项目用哪个esp芯片。
    各个不同芯片的main组件目录下，包含以下文件：
    CMakeList.txt：该芯片main组件的CMakeList.txt文件，会包含esp32_common.cmake（公用的cmake配置），及各芯片自已的一些配置
    idf_component.yml: Component Manager Manifest File,用于加入esp其它级件
    link.if



PSRAM支持

mainfest.py

项目组建：
拉取esp-idf及micrpython，做为项目子模块，分别checkout到v5.0.4，v1.23.0，执行git submodule updatee --init --recursive，拉取所有子模块。
新建port文件夹
从micropython/ports/esp32复制
boards modules、README.md，README.ulp.md 

CMakeLists.txt
esp32_common.cmake

Noto_Sans_CJK_SC_Light16.bin .gitignore过来，把.gitignore内容复制过来。


项目编译：
1、进入esp-idf，执行./install.sh，安装esp-idf的编译环境。
2、执行. ./export.sh，导出相关环境变量。