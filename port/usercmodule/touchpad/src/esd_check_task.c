#include "esd_check_task.h"

 /****************************************************************************************
 *
 * @file i2c_tack.c
 *
 * @brief I2C master and slave tasks
 *
 * Copyright (C) 2020 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */
#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#include "focaltech_core.h"



/**
 * global response string
 */

/**
 * Callbacks
 */
#define mainCOUNTER_FREQUENCY_MS                OS_MS_2_TICKS(200)

