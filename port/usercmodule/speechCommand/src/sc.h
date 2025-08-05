#pragma once
#ifdef __cplusplus
extern "C" {
#endif
void sc_init(const char *wakeup_word, uint16_t timeout_ms, bool enable_flag);
// 全局变量：最新触发的命令 id（初始设为 0，表示无有效命令）
extern volatile int latest_command_id;
extern volatile int sc_stop_flag;

// 获取最新命令 id
int get_latest_command_id(void);

int get_wakeup_flag(void);

// 重置最新命令 id（例如置为 -1）
void reset_latest_command_id(void);
void start_vad_record(void);

#ifdef __cplusplus
}
#endif
