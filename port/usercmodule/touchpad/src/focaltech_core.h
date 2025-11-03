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

#ifndef __FOCALTECH_CORE_H__
#define __FOCALTECH_CORE_H__
/*****************************************************************************
* Included header files
*****************************************************************************/
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
/*****************************************************************************
* Private constant and macro definitions using #define
*****************************************************************************/
#define HOST_MCU_DRIVER_VERSION                  	"FocalTech MCU V1.0 20220610"

#ifdef DEBUG
#define FTS_INFO(fmt, ...)							printf("[FTS/I]%s:"fmt"\r\n", __func__, ##__VA_ARGS__)
#define FTS_ERROR(fmt, ...)							printf("[FTS/E]%s:"fmt"\r\n", __func__, ##__VA_ARGS__)
#define FTS_DEBUG(fmt, ...)	    					printf("[FTS/D]%s:"fmt"\r\n", __func__, ##__VA_ARGS__)
#else
#define FTS_INFO(fmt, ...)							
#define FTS_ERROR(fmt, ...)							
#define FTS_DEBUG(fmt, ...)	   
#endif 					


#define INTERVAL_READ_REG                   		200  /* unit:ms */


#define FTS_CMD_READ_ID                     		0x90

/* chip id */
#define FTS_CHIP_IDH								0x64
#define FTS_CHIP_IDL								0x56

/* register address */
#define FTS_REG_CHIP_ID                     		0xA3
#define FTS_REG_CHIP_ID2                    		0x9F
#define FTS_REG_FW_VER                      		0xA6
#define FTS_REG_UPGRADE                         	0xFC

/*
 * Gesture function enable
 * default: disable
 */
#define FTS_GESTURE_EN                          	0

#define TRIGGER_PIN  HW_GPIO_PIN_12
#define TRIGGER_PORT HW_GPIO_PORT_0
#define TOUCH_RESET_PORT   HW_GPIO_PORT_1
#define TOUCH_RESET_PIN    HW_GPIO_PIN_1

#define FTS_CMD_START_DELAY 12

/* register address */
#define FTS_REG_WORKMODE 0x00
#define FTS_REG_WORKMODE_FACTORY_VALUE 0x40
#define FTS_REG_WORKMODE_SCAN_VALUE 0xC0
#define FTS_REG_FLOW_WORK_CNT 0x91
#define FTS_REG_POWER_MODE 0xA5
#define FTS_REG_GESTURE_EN 0xD0
#define FTS_REG_GESTURE_ENABLE 0x01
#define FTS_REG_GESTURE_OUTPUT_ADDRESS 0xD3

/*Max point numbers of gesture trace*/
#define MAX_POINTS_GESTURE_TRACE 6
/*Length of gesture information*/
#define MAX_LEN_GESTURE_INFO (MAX_POINTS_GESTURE_TRACE * 4 + 2)

/*Max point numbers of touch trace*/
#define MAX_POINTS_TOUCH_TRACE 2
/*Length of touch information*/
#define MAX_LEN_TOUCH_INFO (MAX_POINTS_TOUCH_TRACE * 6 + 2)

/*Max touch points that touch controller supports*/
#define FTS_MAX_POINTS_SUPPORT 10



#define	INT_PIN						                45
#define	RST_PIN						                -1

#define I2C_MASTER_SCL_IO           43                         /*!< GPIO number used for I2C master clock */
#define I2C_MASTER_SDA_IO           44                         /*!< GPIO number used for I2C master data  */
#define I2C_MASTER_NUM              0                          /*!< I2C master i2c port number, the number of i2c peripheral interfaces available will depend on the chip */
#define I2C_MASTER_FREQ_HZ          200000                     /*!< I2C master clock frequency */
#define I2C_MASTER_TX_BUF_DISABLE   0                          /*!< I2C master doesn't need buffer */
#define I2C_MASTER_RX_BUF_DISABLE   0                          /*!< I2C master doesn't need buffer */
#define I2C_MASTER_TIMEOUT_MS       1000

#define I2C_PEER_ADDR      0x38
/*****************************************************************************
* Private enumerations, structures and unions using typedef
*****************************************************************************/
/*
 * Structures of point information
 *
 * @x: X coordinate of this point
 * @y: Y coordinate of this point
 * @p: pressure value of this point
 * @type: event type of this point, 0 means down event,
 *		  1 means up event, 2 means contact event
 * @id: ID of this point
 * @area: touch area of this point
 */
struct fts_ts_event {
    int x;		/*x coordinate */
    int y;		/*y coordinate */
    int p;		/* pressure */
    int type;	/* touch event flag: 0 -- down; 1-- up; 2 -- contact */
    int id; 	/*touch ID */
    int area;   /*touch area*/

};


struct fts_ts_data {
    int suspended;		   /* suspended state, 1: suspended mode, 0:not suspended mode */
    int esd_support;	   /* esd enable or disable, default: disable */
    int gesture_support;   /* gesture enable or disable, default: disable */
};

typedef struct _keys_state_t{
    uint8_t type;
    uint16_t key_id;
}keys_state_t;

extern uint8_t g_touch_event_nums;

/*****************************************************************************
* Global variable or extern global variabls/functions
*****************************************************************************/
extern struct fts_ts_data *fts_data;

void fts_msleep(unsigned long msec);

/* communication interface */
int fts_read(uint8_t addr, uint8_t *data, uint16_t datalen);
int fts_read_reg(uint8_t addr, uint8_t *value);
int fts_write(uint8_t addr, uint8_t *data, uint16_t datalen);
int fts_write_reg(uint8_t addr, uint8_t value);

int fts_ts_init(void);
int fts_ts_suspend(void);
int fts_ts_resume(void);

int fts_touch_process(keys_state_t *key_state);
int fts_check_id1(void);

void fts_esdcheck_process(void);
int fts_gpio_interrupt_handler(struct fts_ts_event *ts_event,uint8_t *touch_buf);
#endif /* __FOCALTECH_CORE_H__ */
