#ifndef SC_MODULE_H
#define SC_MODULE_H

#ifdef __cplusplus
extern "C" {
#endif

// 供 sc.c 调用：传入命令 id，若该 id 注册了回调函数则调用
void sc_invoke_callback_for_id(int command_id);

#ifdef __cplusplus
}
#endif

#endif // SC_MODULE_H
