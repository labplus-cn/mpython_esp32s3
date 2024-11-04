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
    IO_MSG_TYPE_BT_STATUS,  /**< BT status change with subtype @ref GAP_MSG_TYPE */
    IO_MSG_TYPE_KEYSCAN,    /**< Key scan message with subtype @ref T_IO_MSG_KEYSCAN */
    IO_MSG_TYPE_QDECODE,    /**< subtype to be defined */
    IO_MSG_TYPE_UART,       /**< Uart message with subtype @ref T_IO_MSG_UART */
    IO_MSG_TYPE_KEYPAD,     /**< subtype to be defined */
    IO_MSG_TYPE_ADC,        /**< subtype to be defined */
    IO_MSG_TYPE_MOUSE_BUTTON,   /**< subtype to be defined */
    IO_MSG_TYPE_GPIO,       /**< Gpio message with subtype @ref T_IO_MSG_GPIO*/
    IO_MSG_TYPE_TIMER,      /**< App timer message with subtype @ref T_IO_MSG_TIMER */
    IO_MSG_TYPE_WRISTBNAD,  /**< wristband message with subtype @ref T_IO_MSG_WRISTBAND */
    IO_MSG_TYPE_MESH_STATUS,    /**< subtype to be defined */
    IO_MSG_TYPE_KEYBOARD_BUTTON, /**< subtype to be defined */
    IO_MSG_TYPE_BAT_FORCE_DETECT,   /**< BAT adc detect battery value*/
    IO_MSG_TYPE_BAT_LPC,        /**< lpc send low power message*/
    IO_MSG_TYPE_BAT_DETECT,     /**< BAT adc detect battery value*/
    IO_MSG_TYPE_AUDIO,          /**< Audio message with subtype @ref T_IO_MSG_TYPE_AUDIO*/
    IO_MSG_TYPE_RESET_WDG_TIMER, /**< reset watch dog timer*/
    IO_MSG_TYPE_BBPRO_HCI,  /**< bbpro hci message*/
    IO_MSG_TYPE_RTC,             /**< subtype to be defined */
    IO_MSG_TYPE_I2C,             /**< subtype to be defined */
    IO_MSG_TYPE_WIFI_UART,       /**< wifi uart message */
    IO_MSG_TYPE_PD_TIMER,
    IO_MSG_TYPE_AMA_BT_MSG,
    IO_MSG_TYPE_DFU_VALID_FW,
    IO_MSG_TYPE_DFU,
    // IO_ENCODER_PCNT,    /**< 编码器-计数器 */
    // IO_ENCODER_CAP,   /**< 编码器-捕获 */
    IO_BLE,
    IO_ENCODER,
    IO_ID_SENSOR,
    IO_MOTOR,
    IO_ACCELEROMETER,
    IO_MOTION,
    IO_PLAY,
    IO_ACT,
    IO_LED,
    IO_CONFIG,
} T_IO_MSG_TYPE;

typedef enum
{
    IO_BLE_SUB_CONFIGURATION,
    IO_BLE_SUB_ID_NOTIFY,
    IO_BLE_SUB_CREATE_TASK,
    IO_BLE_SUB_DEL_TASK,
    IO_ID_SENSOR_SUB_TIMEROUT,
    IO_ID_SENSOR_SUB_READ,
    IO_KEY_SUB_POWER_ON,
    IO_KEY_SUB_POWER_OFF,
    IO_KEY_SUB_CLICK,
    IO_KEY_SUB_DOUBLE_CLICK,
    IO_KEY_SUB_RELEASE,
    IO_ACCELEROMETER_SUB_IRQ,
    IO_ACCELEROMETER_SUB_NO_MOTION,
    IO_ACCELEROMETER_SUB_ANY_MOTION,
    IO_ACCELEROMETER_SUB_SINGLE_TAP,
    IO_ACCELEROMETER_SUB_DOUBLE_TAP,
    IO_MOTION_SUB_START,
    IO_MOTION_SUB_ARRIVED_TARGET,
    IO_MOTION_SUB_ARRIVED_LAST_TARGET,
    IO_MOTION_SUB_RSP,
    IO_PLAY_SUB_STATUS_END,
    IO_PLAY_SUB_CMD,
    IO_ACT_SUB_ACT,  
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
