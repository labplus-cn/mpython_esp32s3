/*
 * modaudio.c
 *
 *  Created on: 2024.08.23
 *      Author: zhaohuijiang
 */
// #if MICROPY_PY_AUDIO
#include <stdlib.h> 
#include <string.h>
#include "esp_err.h"
#include <sys/stat.h>
#include <ctype.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>

#include "py/nlr.h"
#include "py/runtime.h"
#include "py/objstr.h"
#include "mphalport.h"
#include "esp_log.h"
#include "esp_system.h"

#include "py/stream.h"
#include "py/reader.h"
#include "extmod/vfs.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
// #include "freertos/queue.h"
// #include "freertos/timers.h"

#include <time.h>
#include "soc/io_mux_reg.h"
#include "audio.h"
#include "player.h"
// #include "vfs_lfs2.h"
#include "recorder.h"

// static const char *TAG = "audio";

// static mp_obj_t audio_mod_lsfs2_open(size_t n_args, const mp_obj_t *args)
// {
//     vfs_lfs2_file_open(mp_obj_str_get_str(args[0]));
//     // vfs_fat_file_open(args[0], args[1]);
//     return mp_const_none;
// }
// static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(audio_mod_lfs2_open_obj, 0, 2, audio_mod_lsfs2_open);

static mp_obj_t mod_audio_init(void)
{
    audio_init();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(mod_audio_init_obj, mod_audio_init);

static mp_obj_t mod_audio_deinit(void)
{
    audio_deinit();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_deinit_obj, mod_audio_deinit);

/* ---------------player ------------------------*/
static mp_obj_t audio_player_init(size_t n_args, const mp_obj_t *args)
{
    // player_create(4096, 1);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(audio_player_init_obj, 0, 1, audio_player_init);

static mp_obj_t audio_player_deinit(void)
{
    return mp_const_none; 
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_player_deinit_obj, audio_player_deinit);

static mp_obj_t audio_play(mp_obj_t uri)
{
    const char *_uri = mp_obj_str_get_str(uri);
    player_play(_uri);
    
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(audio_play_obj, audio_play);
// static MP_DEFINE_CONST_FUN_OBJ_0(audio_play_obj, audio_play);

static mp_obj_t audio_resume(void)
{
    // player_resume();
    return mp_const_none;  
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_resume_obj, audio_resume);

static mp_obj_t audio_stop(void)
{
    // player_stop();
    return mp_const_none;   
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_stop_obj, audio_stop);

static mp_obj_t audio_pause(void)
{
    // player_pause();
    return  mp_const_none;   
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_pause_obj, audio_pause);

static mp_obj_t audio_volume(mp_obj_t Volume)
{
    // mp_int_t vol =  mp_obj_get_int(Volume);

    return mp_const_none;   
}
static MP_DEFINE_CONST_FUN_OBJ_1(audio_volume_obj, audio_volume);

static mp_obj_t audio_get_status(void)
{
    // player_status_t status = player_get_status();
    // if(status == RUNNING || status == PAUSED){
    //     return MP_OBJ_NEW_SMALL_INT(1); 
    // }     

    return MP_OBJ_NEW_SMALL_INT(0);
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_get_status_obj, audio_get_status);

/* ------------------------recorder--------------------------*/
static mp_obj_t audio_recorder_init(size_t n_args, const mp_obj_t *args)
{
    // esp_board_init(16000, 2, 32);
    return mp_const_none; 
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(audio_recorder_init_obj, 0, 1, audio_recorder_init);

static mp_obj_t audio_loudness(void)
{
    // uint32_t loud = recorder_loudness();
    return MP_OBJ_NEW_SMALL_INT(0); 
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_loudness_obj, audio_loudness);

static mp_obj_t audio_record(size_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args)
{
    enum { ARG_file_name, ARG_record_time};
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_file_name,    MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_record_time,  MP_ARG_INT, {.u_int = 5} },
    };
    // parse args
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    recorder_record(mp_obj_str_get_str(args[ARG_file_name].u_obj), args[ARG_record_time].u_int); 

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_KW(audio_record_obj, 0, audio_record);

static mp_obj_t audio_recorder_deinit(void)
{
    // recorder_deinit();
    
    return mp_const_none; 
}
static MP_DEFINE_CONST_FUN_OBJ_0(audio_recorder_deinit_obj, audio_recorder_deinit);

static const mp_map_elem_t mpython_audio_locals_dict_table[] = {
    {MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_audio)},
    {MP_OBJ_NEW_QSTR(MP_QSTR___init__), (mp_obj_t)&mod_audio_init_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_deinit), (mp_obj_t)&audio_deinit_obj},
    // {MP_OBJ_NEW_QSTR(MP_QSTR_lfs2_open), (mp_obj_t)&audio_mod_lfs2_open_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_player_init), (mp_obj_t)&audio_player_init_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_player_deinit), (mp_obj_t)&audio_player_deinit_obj},
	{MP_OBJ_NEW_QSTR(MP_QSTR_play), (mp_obj_t)&audio_play_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_resume), (mp_obj_t)&audio_resume_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_stop), (mp_obj_t)&audio_stop_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_pause), (mp_obj_t)&audio_pause_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_set_volume), (mp_obj_t)&audio_volume_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_player_status), (mp_obj_t)&audio_get_status_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_recorder_init), (mp_obj_t)&audio_recorder_init_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_loudness), (mp_obj_t)&audio_loudness_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_record), (mp_obj_t)&audio_record_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_recorder_deinit), (mp_obj_t)&audio_recorder_deinit_obj},
};

static MP_DEFINE_CONST_DICT(mpython_audio_locals_dict, mpython_audio_locals_dict_table);

const mp_obj_module_t mp_module_audio = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *)&mpython_audio_locals_dict,
};

MP_REGISTER_MODULE(MP_QSTR_audio, mp_module_audio);
// #endif //#if MICROPY_PY_AUDIO