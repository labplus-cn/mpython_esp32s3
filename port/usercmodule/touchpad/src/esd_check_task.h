/**
 ****************************************************************************************
 *
 * @file i2c_task.h
 *
 * @brief I2C task
 *
 * Copyright (C) 2020 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#ifndef _ESD_CHECK_TASK_H_
#define _ESD_CHECK_TASK_H_


/* The rate at which data is template task counter is incremented. */
#define COUNTER_FREQUENCY_MS                OS_MS_2_TICKS(200)


/**
 * @brief esd_check_task  :
 */
void ESD_Check_Task( void *pvParameters );

#endif /* _ESD_CHECK_TASK_H_ */
