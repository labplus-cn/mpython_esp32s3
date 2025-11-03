#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// #include "ie_kaiji.h"
#include "speech_commands_action.h"

void wake_up_action(void)
{
 //   esp_audio_play((int16_t *)(playlist[0].data), playlist[0].length, portMAX_DELAY);
    printf("wake\n");
}

void speech_commands_action(int command_id)
{
   // esp_audio_play((int16_t *)(playlist[command_id + 1].data), playlist[command_id + 1].length, portMAX_DELAY);
    printf("sc action:%d\n", command_id);
}
