#pragma once
#ifdef __cplusplus
extern "C" {
#endif

void text_to_speech(const char* text);
void model_init(void);

extern volatile int tts_flag;
int get_tts_flag(void);
int get_tts_init_flag(void);

#ifdef __cplusplus
}
#endif
