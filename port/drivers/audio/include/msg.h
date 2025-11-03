/**
 * @file msg.h
 * @author zhaohui jiang (diskman88@163.com)
 * @brief 
 * @version 0.1
 * @date 2022-07-15
 * 
 * @copyright Copyright (c) 2022
 * 
 */

#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#include <stdlib.h>

/**  @brief IO type definitions for IO message, may extend as requested */
typedef enum
{
    IO_MSG_TYPE_PLAY_STOP = 1,
    IO_MSG_TYPE_PLAY_PAUSE,  
    IO_MSG_TYPE_PLAY_HTTP_READ_END,
    IO_MSG_TYPE_RECORD_END,
} T_IO_MSG_TYPE;

typedef enum
{
    IO_PLAY_SUB_CMD,
} T_IO_MSG_SUB_TYPE;

/**  @brief IO message definition for communications between tasks*/
typedef struct
{
    uint16_t type;
    uint16_t subtype;
    union
    {
        uint8_t param_u8[4];
        uint16_t param_u16[2];
        uint32_t param_u32;
        void     *buf;
    } u;
}msg_t;

#ifdef __cplusplus
}
#endif
