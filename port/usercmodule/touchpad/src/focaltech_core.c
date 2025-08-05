/*
 * Privileged & confidential  All Rights/Copyright Reserved by FocalTech.
 *       ** Source code released bellows and hereby must be retained as
 * FocalTech's copyright and with the following disclaimer accepted by
 * Receiver.
 *
 * "THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
 * EVENT SHALL THE FOCALTECH'S AND ITS AFFILIATES'DIRECTORS AND OFFICERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
 */

/*****************************************************************************
 *
 *    The initial work you should do is to implement the i2c communication function based on your platform:
 *  platform_i2c_write() and platform_i2c_read().
 *
 *    In your system, you should register a interrupt at initialization stage(The interrupt trigger mode is
 * falling-edge mode), then interrupt handler will run while host detects the falling-edge of INT port.
 *
 *
 *****************************************************************************/

/*****************************************************************************
 * Included header files
 *****************************************************************************/
#include "focaltech_core.h"
#include <inttypes.h>
#include <stdio.h>
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
/*****************************************************************************
 * Private constant and macro definitions using #define
 *****************************************************************************/
static QueueHandle_t gpio_evt_queue = NULL;


/*****************************************************************************
 * Private variables/functions
 *****************************************************************************/
static struct fts_ts_data _fts_data = {
    .suspended = 0,
    .gesture_support = FTS_GESTURE_EN,
    .esd_support = 1,
};

/*****************************************************************************
 * Global variable or extern global variabls/functions
 *****************************************************************************/

struct fts_ts_data *fts_data = &_fts_data;
uint8_t g_touch_event_nums = 0;

void fts_msleep(unsigned long msec)
{
    vTaskDelay(msec / portTICK_PERIOD_MS);
}

static int platform_i2c_write(uint8_t *wbuf, uint16_t wlen)
{
    return i2c_master_write_to_device(I2C_MASTER_NUM, I2C_PEER_ADDR, wbuf, wlen, 100 * (1 + wlen) / portTICK_PERIOD_MS);

}

static int platform_i2c_read(uint8_t addr, uint8_t *rbuf, uint16_t rlen)
{
    return i2c_master_write_read_device(I2C_MASTER_NUM, I2C_PEER_ADDR, &addr, 1, rbuf, rlen, I2C_MASTER_TIMEOUT_MS / portTICK_PERIOD_MS);
  
}

/*****************************************************************************
 * reset chip
 *****************************************************************************/
static int fts_hw_reset(uint8_t msec)
{
    /*firsty. set reset_pin low, and then delay 10ms*/
    /*secondly. set reset_pin high, and then delay 200ms*/
    return 0;
}


/*****************************************************************************
 * Initialize i2c
 *****************************************************************************/
static int platform_i2c_init(void)
{
    /*Initialize I2C bus, you should implement it based on your platform*/
    int i2c_master_port = I2C_MASTER_NUM;

    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };

    esp_err_t ret = i2c_param_config(i2c_master_port, &conf);
    if (ret != ESP_OK)
    {
        return ESP_FAIL;
    }
    return i2c_driver_install(i2c_master_port, conf.mode, I2C_MASTER_RX_BUF_DISABLE, I2C_MASTER_TX_BUF_DISABLE, 0);
}

/*****************************************************************************
 * Initialize reset pin
 *****************************************************************************/
static int platform_reset_pin_cfg(void)
{
    /*Initialize reset_pin,  you should implement it based on your platform*/

    /*firstly,set the reset_pin to output mode*/
    /*secondly,set the reset_pin to low */

    return 0;
}

/*****************************************************************************
 * Initialize gpio interrupt, and set trigger mode to falling edge.
 *****************************************************************************/
static void IRAM_ATTR int_pin_isr_handler(void *arg)
{
    uint32_t gpio_num = (uint32_t) arg;
    xQueueSendFromISR(gpio_evt_queue, &gpio_num, NULL);
}
static int platform_interrupt_gpio_init(void)
{
    /*Initialize gpio interrupt , and the corresponding interrupt function is fts_gpio_interrupt_handler,
    you should implement it based on your platform*/
gpio_config_t io_conf = {};

    //interrupt of rising edge
    io_conf.intr_type = GPIO_INTR_NEGEDGE;
    io_conf.pin_bit_mask = 1ULL<<INT_PIN;
    //set as input mode

    //change gpio interrupt type for one pin
    /*firstly,set int_pin to input mode with pull-up*/
    io_conf.mode = GPIO_MODE_INPUT;
    //enable pull-up mode
    io_conf.pull_up_en = 1;
    gpio_config(&io_conf);
    /*secondly,and set int_pin's trigger mode to falling edge trigger */
    // gpio_set_intr_type(INT_PIN, GPIO_INTR_NEGEDGE);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(INT_PIN, int_pin_isr_handler, (void*) NULL);

    return 0;
}

/*****************************************************************************
 * TP power on
 *****************************************************************************/
static void fts_power_on(void)
{
    /*refer to ic datasheet*/
}

/*****************************************************************************
 * Initialize timer and set to interrupt mode which period is 1 second
 *****************************************************************************/
static int platform_interrupt_timer_init(void)
{

    /*Initialize timer and set to interrupt mode which period is 1 second,
    and the corresponding interrupt function is fts_timer_interrupt_handler,
    you should implement it based on your platform*/
    return 0;
}

/*****************************************************************************
 * Name: fts_write
 * Brief:
 *   Write function via I2C bus, you should implement it based on your platform.
 *
 *   The code below is only a sample code, a pseudo code. you must implement it
 *  following standard I2C protocol based on your platform
 *
 *
 * Input: @addr: the command or register address
 *        @data: the data buffer, data buffer can be NULL for commands without data fields.
 *        @datalen: length of data buffer
 * Output:
 * Return:
 *   return 0 if success, otherwise error code.
 *****************************************************************************/
int fts_write(uint8_t addr, uint8_t *data, uint16_t datalen)
{
    /*TODO based your platform*/
    int ret = 0;
    uint8_t txbuf[256] = {0};
    uint16_t txlen = 0;
    int i = 0;

    if (datalen >= 256)
    {
        FTS_ERROR("txlen(%d) fails", datalen);
        return -1;
    }

    memcpy(&txbuf[0], &addr, 1);
    txlen = 1;
    if (data && datalen)
    {
        memcpy(&txbuf[txlen], data, datalen);
        txlen += datalen;
    }

    /*call platform_i2c_write function to transfer I2C package to TP controller
     *platform_i2c_write() is different for different platform, based on your platform.
     */
    for (i = 0; i < 3; i++)
    {
        ret = platform_i2c_write(txbuf, txlen);
        if (ret != 0)
        {
            FTS_ERROR("platform_i2c_write(%d) fails,ret:%d,retry:%d", addr, ret, i);
            continue;
        }
        else
        {
            ret = 0;
            break;
        }
    }

    return ret;
}

/*****************************************************************************
 * Name: fts_read
 * Brief:
 *   Read function via I2C bus, you should implement it based on your platform.
 *
 *   The code below is only a sample code, a pseudo code. you must implement it
 *  following standard I2C protocol based on your platform
 *
 *
 * Input: @addr: the command or register data
 *        @datalen: length of data buffer
 * Output:
 *        @data: the data buffer read from TP controller
 * Return:
 *   return 0 if success, otherwise error code.
 *****************************************************************************/
int fts_read(uint8_t addr, uint8_t *data, uint16_t datalen)
{

    /*TODO based your platform*/
    int ret = 0;
    int i = 0;

    if (!data || !datalen)
    {
        FTS_ERROR("data is null, or datalen is 0");
        return -1;
    }

    for (i = 0; i < 3; i++)
    {

        ret = platform_i2c_read(addr, data, datalen);

        if (ret != 0)
        {
            FTS_ERROR("platform_i2c_read fails,ret:%d,retry:%d", ret, i);
            continue;
        }
        else
        {
            FTS_DEBUG("platform_i2c_read success,ret:%d,i:%d", ret, i);
            break;
        }
    }

    return ret;
}

/*****************************************************************************
 * Name: fts_write_reg
 * Brief:
 *   write function via I2C bus, you should implement it based on your platform.
 *
 *   The code below is only a sample code, a pseudo code. you must implement it
 *  following standard I2C protocol based on your platform
 *
 *
 * Input: @addr: the command or register address
 *        @val: the data write to TP controller
 * Return:
 *   return 0 if success, otherwise error code.
 *****************************************************************************/
int fts_write_reg(uint8_t addr, uint8_t val)
{
    return fts_write(addr, &val, 1);
}

/*****************************************************************************
 * Name: fts_read_reg
 * Brief:
 *   read function via I2C bus, you should implement it based on your platform.
 *
 *   The code below is only a sample code, a pseudo code. you must implement it
 *  following standard I2C protocol based on your platform
 *
 *
 * Input: @addr: the command or register address
 * Output:
 *        @val: the data read from TP controller
 * Return:
 *   return 0 if success, otherwise error code.
 *****************************************************************************/
int fts_read_reg(uint8_t addr, uint8_t *val)
{
    return fts_read(addr, val, 1);
}

/*****************************************************************************
 * Name: fts_check_id1
 * Brief:
 *   The function is used to check id.
 * Input:
 * Output:
 * Return:
 *   return 0 if check id successfully, otherwise error code.
 *****************************************************************************/
int fts_check_id1(void)
{
    int ret = 0;

    uint8_t chip_id[2] = {0};

    /*delay 200ms,wait fw*/
    fts_msleep(200);

    /*get chip id*/
    fts_read_reg(FTS_REG_CHIP_ID, &chip_id[0]);
    fts_read_reg(FTS_REG_CHIP_ID2, &chip_id[1]);
    if ((FTS_CHIP_IDH == chip_id[0]) && (FTS_CHIP_IDL == chip_id[1]))
    {
        FTS_INFO("get ic information, chip id = 0x%02x%02x", chip_id[0], chip_id[1]);
        return 0;
    }

    /*get boot id*/
    FTS_INFO("fw is invalid, need read boot id");
    ret = fts_write_reg(0x55, 0xAA);
    if (ret < 0)
    {
        FTS_ERROR("start cmd write fail");
        return ret;
    }

    fts_msleep(FTS_CMD_START_DELAY);
    
    ret = fts_read(FTS_CMD_READ_ID, chip_id, 2);
    if ((ret == 0) && ((FTS_CHIP_IDH == chip_id[0]) && (FTS_CHIP_IDL == chip_id[1])))
    {
        FTS_INFO("get ic information, boot id = 0x%02x%02x", chip_id[0], chip_id[1]);
        ret = 0;
    }
    else
    {
        FTS_ERROR("read boot id fail,read:0x%02x%02x", chip_id[0], chip_id[1]);
        return -1;
    }

    return ret;
}

/*****************************************************************************
 *  Name: fts_esdcheck_algorithm
 *  Brief:
 *    The function is use to esd check.It should be called in timer interrupt handler.
 *  Input:
 *  Output:
 *  Return:
 *****************************************************************************/
void fts_esdcheck_process(void)
{
    uint8_t reg_value = 0;
    static uint8_t flow_work_hold_cnt = 0;
    static uint8_t flow_work_cnt_last = 0;

    /* 1. check power state, if suspend, no need check esd */
    if (fts_data->suspended == 1)
    {
        FTS_DEBUG("In suspend, not check esd");
        /* because in suspend state, when upgrade FW, will
         * active ESD check(active = 1); when resume, don't check ESD again
         */
        return;
    }

    /* 2. In factory mode, can't check esd */
    fts_read_reg(FTS_REG_WORKMODE, &reg_value);
    if ((reg_value == FTS_REG_WORKMODE_FACTORY_VALUE) || (reg_value == FTS_REG_WORKMODE_SCAN_VALUE))
    {
        FTS_DEBUG("in factory mode(%x), no check esd", reg_value);
        return;
    }

    /* 3. get Flow work cnt: 0x91 If no change for 5 times, then ESD and reset */
    fts_read_reg(FTS_REG_FLOW_WORK_CNT, &reg_value);
    if (flow_work_cnt_last == reg_value)
        flow_work_hold_cnt++;
    else
        flow_work_hold_cnt = 0;

    flow_work_cnt_last = reg_value;

    /* 4. If need hardware reset, then handle it here */
    if (flow_work_hold_cnt >= 5)
    {
        FTS_DEBUG("ESD, Hardware Reset");
        flow_work_hold_cnt = 0;
        fts_hw_reset(200);
    }
}

/*****************************************************************************
 * Name: fts_gesture_process
 * Brief:
 *   The function is used to read and parse gesture information. It should be
 *  called in gpio interrupt handler while system is in suspend state.
 * Input:
 * Output:
 *       @buf: read gesture data
 * Return:
 *   return 0 if getting and parsing gesture successfully,
 *   return 1 if gesture isn't enabled in FW,
 *   otherwise error code.
 *****************************************************************************/
static int fts_gesture_process(uint8_t *buf)
{
    int ret = 0;
    uint8_t regaddr = 0;
    uint8_t value = 0xFF;
    uint8_t gesture_id = 0;

    /*Read a byte from register 0xD0 to confirm gesture function in FW is enabled*/
    ret = fts_read_reg(FTS_REG_GESTURE_EN, &value);
    if ((ret < 0) || (value != FTS_REG_GESTURE_ENABLE))
    {
        FTS_DEBUG("gesture isn't enable in fw, don't process gesture");
        return 1;
    }

    /*Read 26 bytes from register 0xD3 to get gesture information*/
    regaddr = FTS_REG_GESTURE_OUTPUT_ADDRESS;
    memset(buf, 0xFF, MAX_LEN_GESTURE_INFO);
    ret = fts_read(regaddr, buf, MAX_LEN_GESTURE_INFO);
    if (ret < 0)
    {
        FTS_DEBUG("read gesture information from reg0xD3 fails");
        return ret;
    }

    /*get gesture_id, and the gestrue_id table provided by our technicians */
    //    gesture_id = &buf[0];
    gesture_id = buf[0];
    FTS_INFO("gesture_id = %d", gesture_id);
    /* Now you have parsed the gesture information, you can recognise the gesture type based on gesture id.
     * You can do anything you want to do, for example,
     *     gesture id 0x24, so the gesture type id "Double Tap", now you can inform system to wake up
     *     from gesture mode.
     */

    /*TODO...(report gesture to system)*/

    return 0;
}

/*****************************************************************************
 * Name: fts_touch_process
 * Brief:
 *   The function is used to read and parse touch points information. It should be
 *  called in gpio interrupt handler while system is in display(normal) state.
 * Input:
 * Output:
 *      @ts_event: touch event data
 *      @buf:touch data
 * Return:
 *   return 0 if getting and parsing touch points successfully, otherwise error code.
 *****************************************************************************/
int fts_touch_process(keys_state_t *key_state)
{
    int ret = 0;
    uint8_t i = 0;
    uint8_t base = 0;
    uint8_t regaddr = 0x01;
    uint8_t point_num = 0;
    uint8_t point_id = 0;
    uint8_t buf[100];
    struct fts_ts_event events[MAX_POINTS_TOUCH_TRACE];
    static uint8_t type_before[MAX_POINTS_TOUCH_TRACE] = {0, 0};

    g_touch_event_nums = 0;
    /*read touch information from reg0x01*/
    //    memset(buf, 0xFF, MAX_LEN_TOUCH_INFO);
    ret = fts_read(regaddr, buf, MAX_LEN_TOUCH_INFO);
    if (ret < 0)
    {
        FTS_DEBUG("Read touch information from reg0x01 fails");
        return ret;
    }

    if ((buf[1] == 0xFF) && (buf[2] == 0xFF) && (buf[3] == 0xFF))
    {
        FTS_INFO("FW initialization, need recovery");
        if (fts_data->gesture_support && fts_data->suspended)
            fts_write_reg(FTS_REG_GESTURE_EN, FTS_REG_GESTURE_ENABLE);
    }

    /*parse touch information based on register map*/
    //    memset(events, 0xFF, sizeof(struct fts_ts_event) * FTS_MAX_POINTS_SUPPORT);
    point_num = buf[1] & 0x0F;
    if (point_num > FTS_MAX_POINTS_SUPPORT)
    {
        FTS_DEBUG("invalid point_num(%d)", point_num);
        return -1;
    }

    for (i = 0; i < MAX_POINTS_TOUCH_TRACE; i++)
    {
        base = 2 + i * 6;
        point_id = buf[base + 2] >> 4;
        if (point_id >= MAX_POINTS_TOUCH_TRACE)
        {
            break;
        }

        events[i].x = ((buf[base] & 0x0F) << 8) + buf[base + 1];
        events[i].y = ((buf[base + 2] & 0x0F) << 8) + buf[base + 3];
        events[i].id = point_id;
        events[i].type = (buf[base] >> 6) & 0x03;
        events[i].p = buf[base + 4];
        events[i].area = buf[base + 5];
        if (((events[i].type == 0) || (events[i].type == 2)) && (point_num == 0))
        {
            FTS_DEBUG("abnormal touch data from fw");
            return -2;
        }

        g_touch_event_nums++;
    }

    if (g_touch_event_nums == 0)
    {
        FTS_DEBUG("no touch point information(%02x)", buf[1]);
        return -3;
    }

    /*Now you have get the touch information, you can report anything(X/Y coordinates...) you want to system*/
    /*TODO...(report touch information to system)*/
    /*Below sample code is a pseudo code*/
    for (i = 0; i < g_touch_event_nums; i++)
    {
        if ((events[i].type == 0) || (events[i].type == 2))
        {
            /* The event of point(point id is events[i].id) is down event, the finger of this id stands for is
             * pressing on the screen.*/
            /*TODO...(down event)*/
            // printf(">%d down event x:%d, y:%d\n", i, events[i].x, events[i].y);
            if(type_before[i] == 0){
                key_state[i].type = 1;
                key_state[i].key_id = events[i].y - 4000;
                type_before[i] = 1;
            }else{
                key_state[i].type =3;
            }
        }
        else
        {
            /*TODO...(up event)*/
            // printf(">%d up event x:%d, y:%d\n", i, events[i].x, events[i].y);
            if(type_before[i] == 1){
                key_state[i].type = 2;
                key_state[i].key_id = events[i].y - 4000;
                type_before[i] = 0;
            }else{
                key_state[i].type =3;
            }
        }
    }

    return 0;
}

/*****************************************************************************
 * An interrupt handler, will be called while the voltage of INT Port changes from high to low(falling-edge trigger mode).
 * The program reads touch data or gesture data from TP controller, and then sends it into system.
 *****************************************************************************/
// int fts_gpio_interrupt_handler(struct fts_ts_event *ts_event, uint8_t *touch_buf)
// {
//     int ret = 0;

//     if (fts_data->gesture_support && fts_data->suspended)
//     {
//         /*if gesture is enabled, interrupt handler should process gesture at first*/
//         ret = fts_gesture_process(touch_buf);
//         if (ret == 0)
//         {
//             FTS_DEBUG("success to process gesture.");
//             return 1;
//         }
//     }

//     /*if gesture isn't enabled, the handler should process touch points*/
//     fts_touch_process(ts_event, touch_buf);

//     return 0;
// }

/*****************************************************************************
 *  Name: fts_suspend
 *  Brief: System suspends and update the suspended state
 *  Input:
 *  Output:
 *  Return:
 *     return 0 if enter suspend successfully, otherwise error code
 *****************************************************************************/
int fts_ts_suspend(void)
{
    int ret = 0;

    if (fts_data->suspended)
    {
        FTS_INFO("Already in suspend state");
        return 0;
    }

    if (fts_data->gesture_support)
    {
        /*Host writes 0x01 to register address 0xD0 to enable gesture function while system suspends.*/
        ret = fts_write_reg(FTS_REG_GESTURE_EN, FTS_REG_GESTURE_ENABLE);
        if (ret < 0)
        {
            FTS_ERROR("enable gesture fails.ret:%d", ret);
        }
        else
        {
            FTS_INFO("enable gesture success.");
        }
    }
    else
    {
        /*Host writes 0x03 to register address 0xA5 to enter into sleep mode.*/
        ret = fts_write_reg(FTS_REG_POWER_MODE, 0x03);
        if (ret < 0)
        {
            FTS_ERROR("system enter sleep mode fails.ret:%d", ret);
        }
        else
        {
            FTS_INFO("system enter sleep mode success.");
        }
    }

    fts_data->suspended = 1;
    return 0;
}

/*****************************************************************************
 *  Name: fts_resume
 *  Brief: System resume and update the suspended state
 *  Input:
 *  Output:
 *  Return:
 *    return 0 if enter resume successfully, otherwise error code
 *****************************************************************************/
int fts_ts_resume(void)
{
    if (!fts_data->suspended)
    {
        FTS_INFO("Already in resume state");
        return 0;
    }

    fts_data->suspended = 0;
    fts_hw_reset(200);

    return 0;
}
// static void gpio_task_example(void* arg)
// {
//     uint32_t io_num;
//     for (;;) {
//         if (xQueueReceive(gpio_evt_queue, &io_num, portMAX_DELAY)) {
//             fts_touch_process();
//             xQueueReset(gpio_evt_queue);
//         }
//         // vTaskDelay(100 / portTICK_PERIOD_MS);

//     }
// }
/*****************************************************************************
 * Name: fts_init
 * Brief:
 *   The function is used to i2c init��tp_rst pin init��interrupt_pin init��timer init.
 * Input:
 * Output:
 * Return:
 *   return 0 if success, otherwise error code.
 *****************************************************************************/
// int fts_ts_init(void)
// {
//     int ret = 0;

//     /*Initialize I2C*/
//     ret = platform_i2c_init();
//     if (ret < 0)
//     {
//         FTS_ERROR("I2C init fails.ret:%d", ret);
//         return ret;
//     }

//     /*reset pin cfg*/
//     ret = platform_reset_pin_cfg();
//     if (ret < 0)
//     {
//         FTS_ERROR("reset pin init fails.ret:%d", ret);
//         return ret;
//     }

//     /*tp power on*/
//     fts_power_on();
//     ret = fts_fwupg_auto_upgrade();
//     if(ret < 0) {
//         FTS_ERROR("Upgrade fails.ret:%d\n",ret);
//         return ret;
//     }

//     /*check chip id*/
//     ret = fts_check_id1();
//     if (ret < 0)
//     {
//         FTS_ERROR("get chip id fails.ret:%d", ret);
//         return ret;
//     }

//     /*Register gpio interrupt handler,which for touch process or gestrue process*/
    
//     gpio_evt_queue = xQueueCreate(10, sizeof(uint32_t));
//     // xTaskCreate(gpio_task_example, "gpio_task_example", 2048, NULL, 10, NULL);
//     printf(">D%d[%s]\n", __LINE__, __FUNCTION__);
//     ret = platform_interrupt_gpio_init();
//     if (ret < 0)
//     {
//         FTS_ERROR("Register gpio interrupt handler fails.ret:%d", ret);
//         return ret;
//     }

//     /*Initialize timer and set to interrupt mode with one second one period, which for esd check*/
//     // ret = platform_interrupt_timer_init();
//     // if(ret < 0) {
//     //     FTS_ERROR("Initialize timer fails.ret:%d",ret);
//     //     return ret;
//     // }
//     gpio_task_example(NULL);
//     return ret;
// }
