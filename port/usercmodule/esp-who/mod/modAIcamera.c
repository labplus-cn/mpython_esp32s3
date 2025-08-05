// #include "human_face_detection.hpp"

#include "py/runtime.h"
#include "who_camera.h"
#include "esp_camera.h"
#include "esp_log.h"
#include "who_lcd.h"
#include "who_c_wrapper.h"
#include "who_human_face_recognition.hpp"
#include "who_code_scanner.h"
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

static bool ai_module_initialized = false;
static QueueHandle_t xQueueAIFrame = NULL;
static QueueHandle_t xQueueLCDFrame = NULL;
static QueueHandle_t xQueueResult = NULL;
static QueueHandle_t xQueueEvent = NULL;
static mp_obj_t ai_callback = MP_OBJ_NULL;
ai_msg_t msg;

static void task_resault_handler(void *arg)
{
    while (true)
    {
        xQueueReceive(xQueueResult, &msg, portMAX_DELAY); //识别成功
        if(ai_callback){
            mp_sched_schedule(ai_callback, mp_obj_new_int(0));
        }
    }
}
static mp_obj_t AI_detect_init(mp_obj_t type, mp_obj_t callback)
{
    ai_callback = callback;
    int _type = mp_obj_get_int(type);

    if(!ai_module_initialized){
        xQueueAIFrame = xQueueCreate(2, sizeof(camera_fb_t *));
        xQueueLCDFrame = xQueueCreate(2, sizeof(camera_fb_t *));
        xQueueEvent = xQueueCreate(2, sizeof(int8_t));
        xQueueResult = xQueueCreate(2, sizeof(ai_msg_t));
    
        if(_type == AI_TYPE_NONE){
            register_camera(PIXFORMAT_RGB565, FRAMESIZE_QVGA, 2, xQueueLCDFrame);
        }else{
            register_camera(PIXFORMAT_RGB565, FRAMESIZE_QVGA, 2, xQueueAIFrame);
        }
        
        switch(_type){
            case AI_TYPE_COLOR_DETECTION:
                register_color_detection_wrapper(xQueueAIFrame, xQueueEvent, xQueueResult, xQueueLCDFrame, false);
            break;
            case AI_TYPE_FACE_DETECTION:
                register_human_face_detection_wrapper(xQueueAIFrame, NULL, xQueueResult, xQueueLCDFrame, false);
            break;
            case AI_TYPE_FACE_RECOGNITION:
                register_human_face_recognition_wrapper(xQueueAIFrame, xQueueEvent, xQueueResult, xQueueLCDFrame, false);
            break;
            case AI_TYPE_CAT_FACE_DETECTION:
                register_cat_face_detection_wrapper(xQueueAIFrame, NULL, xQueueResult, xQueueLCDFrame, false);
            break;
            case AI_TYPE_MOTION_DEECTION:
                register_motion_detection_wrapper(xQueueAIFrame, NULL, xQueueResult, xQueueLCDFrame);
            break;
            case AI_TYPE_CODE_SCANNER:
                register_code_scanner(xQueueAIFrame, NULL, xQueueResult, xQueueLCDFrame, false);
            default:

            break;

        }

        register_lcd(xQueueLCDFrame, NULL, true);

        xTaskCreatePinnedToCore(task_resault_handler, "resault_task", 4 * 1024, NULL, 5, NULL, 1);

        ai_module_initialized = true;
    }


    return mp_const_none; 
}
static MP_DEFINE_CONST_FUN_OBJ_2(AI_detect_init_obj, AI_detect_init);

static mp_obj_t AI_command(mp_obj_t command)
{
    int cmd = mp_obj_get_int(command);
    xQueueSend(xQueueEvent, &cmd, portMAX_DELAY);
    return mp_const_none; 
}
static MP_DEFINE_CONST_FUN_OBJ_1(AI_command_obj, AI_command);

static mp_obj_t mp_get_result(void)
{
    mp_obj_t t[10];
    int i;
    mp_obj_t dict[msg.element_num];

    if(msg.type == AI_TYPE_FACE_DETECTION || msg.type == AI_TYPE_CAT_FACE_DETECTION){
        for(i = 0; i < msg.element_num; i++)
            dict[i] = mp_obj_new_dict(2);

        for(i = 0; i < msg.element_num; i++){
            t[0] = mp_obj_new_int(msg.box[i][0]);
            t[1] = mp_obj_new_int(msg.box[i][1]);
            t[2] = mp_obj_new_int(msg.box[i][2]);
            t[3] = mp_obj_new_int(msg.box[i][3]);
            mp_obj_dict_store(dict[i], MP_OBJ_NEW_QSTR(MP_QSTR_box),  mp_obj_new_tuple(4, t));
            
            for(int j = 0; j < 10; j++){
                t[j] = mp_obj_new_int(msg.keypoint[i][j]);
            }
            mp_obj_dict_store(dict[i], MP_OBJ_NEW_QSTR(MP_QSTR_keypoint),  mp_obj_new_tuple(10, t));
        }
        return mp_obj_new_tuple(msg.element_num, dict); 
    }else if(msg.type == AI_TYPE_FACE_RECOGNITION){
        mp_obj_t t[10];

        mp_obj_t dict = mp_obj_new_dict(4);
        mp_obj_dict_store(dict, MP_OBJ_NEW_QSTR(MP_QSTR_id), MP_OBJ_NEW_SMALL_INT(msg.id));
        mp_obj_dict_store(dict, MP_OBJ_NEW_QSTR(MP_QSTR_Similarity), mp_obj_new_float(msg.similarity));
        t[0] = mp_obj_new_int(msg.box[0][0]);
        t[1] = mp_obj_new_int(msg.box[0][1]);
        t[2] = mp_obj_new_int(msg.box[0][2]);
        t[3] = mp_obj_new_int(msg.box[0][3]);
        mp_obj_dict_store(dict, MP_OBJ_NEW_QSTR(MP_QSTR_box),  mp_obj_new_tuple(4, t));
        for(int j = 0; j < 10; j++){
            t[j] = mp_obj_new_int(msg.keypoint[0][j]);
        }
        mp_obj_dict_store(dict, MP_OBJ_NEW_QSTR(MP_QSTR_keypoint),  mp_obj_new_tuple(10, t));

        return dict;
    }else if(msg.type == AI_TYPE_COLOR_DETECTION){

        return mp_const_none;
    }else if(msg.type == AI_TYPE_CODE_SCANNER){
        return mp_obj_new_str(msg.data, strlen(msg.data));
    }else{
        return mp_const_none;
    }

}
static MP_DEFINE_CONST_FUN_OBJ_0(mp_get_result_obj, mp_get_result);

static const mp_rom_map_elem_t AIcamera_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_AIcamera) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&AI_detect_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_send_command), MP_ROM_PTR(&AI_command_obj) },
    { MP_ROM_QSTR(MP_QSTR_get_result), MP_ROM_PTR(&mp_get_result_obj) },
    { MP_ROM_QSTR(MP_QSTR_COLOR_DETECTION), MP_ROM_INT(AI_TYPE_COLOR_DETECTION) },
    { MP_ROM_QSTR(MP_QSTR_FACE_DETECTION), MP_ROM_INT(AI_TYPE_FACE_DETECTION) },
    { MP_ROM_QSTR(MP_QSTR_FACE_RECOGNITION), MP_ROM_INT(AI_TYPE_FACE_RECOGNITION) },
    { MP_ROM_QSTR(MP_QSTR_CAT_FACE_DETECTION), MP_ROM_INT(AI_TYPE_CAT_FACE_DETECTION) },
    { MP_ROM_QSTR(MP_QSTR_MOTION_DEECTION), MP_ROM_INT(AI_TYPE_MOTION_DEECTION) },
    { MP_ROM_QSTR(MP_QSTR_CODE_SCANNER), MP_ROM_INT(AI_TYPE_CODE_SCANNER) },
    { MP_ROM_QSTR(MP_QSTR_ENROLL), MP_ROM_INT(ENROLL) },
    { MP_ROM_QSTR(MP_QSTR_RECOGNIZE), MP_ROM_INT(RECOGNIZE) },
    { MP_ROM_QSTR(MP_QSTR_DELETE), MP_ROM_INT(DELETE) },
};
static MP_DEFINE_CONST_DICT(AIcamera_module_globals, AIcamera_module_globals_table);

// Define module object.
const mp_obj_module_t AIcamera_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&AIcamera_module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_AIcamera, AIcamera_cmodule);


