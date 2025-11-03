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
* 	Some descriptions about this sample code.
* 	fts_fwupg_auto_upgrade() is entry of this sample code.
*
* 	The initial work you should do is to implement the i2c communication function based on your platform:
*	 	platform_i2c_write() and platform_i2c_read().
*
*
* 	How to use the upgrade sample code?
*		Firstly, Place firmware file(app.i) into firmware directory.
*		Secondly, modify variable fw_file_ft3x68 to include firmware file you put into firmware directory.
* 	Warning: you can ignore the above steps if you want get firmware file as your way. And
*		   you should get firmware at the beginning of function fts_fwupg_auto_upgrade().
*	    Thirdly, call fts_fwupg_auto_upgrade().
*
*
*****************************************************************************/


/*****************************************************************************
* Included header files
*****************************************************************************/
#include "focaltech_core.h"


/*****************************************************************************
* Private constant and macro definitions using #define
*****************************************************************************/
/*command*/
#define FTS_CMD_RESET                               0x07
#define FTS_CMD_FLASH_MODE                          0x09
#define FTS_FLASH_MODE_UPGRADE_VALUE                0x0B
#define FTS_CMD_FLASH_STATUS                        0x6A
#define FTS_CMD_ERASE_APP                           0x61
#define FTS_RETRIES_REASE                           50
#define FTS_RETRIES_DELAY_REASE                     400
#define FTS_CMD_FLASH_STATUS_ERASE_OK               0xF0AA
#define FTS_CMD_FLASH_STATUS_ECC_OK                 0xF055
#define FTS_CMD_ECC_INIT                            0x64
#define FTS_CMD_ECC_CAL                             0x65
#define FTS_CMD_ECC_READ                            0x66
#define FTS_CMD_ECC_CAL_LEN                         6
#define FTS_RETRIES_ECC_CAL                         10
#define FTS_RETRIES_DELAY_ECC_CAL                   50
#define FTS_CMD_WRITE                               0xBF
#define FTS_RETRIES_WRITE                           100
#define FTS_CMD_READ_DELAY                          1
#define FTS_CMD_APP_DATA_LEN                        0x7A
#define FTS_CMD_FW_START_ADDRESS		    		0x0C00
/*register address*/
#define FTS_UPGRADE_AA                              0xAA
#define FTS_UPGRADE_55                              0x55


#define FTS_RETRIES_CHECK_ID                        20
#define FTS_DELAY_UPGRADE_AA                        10
#define FTS_DELAY_UPGRADE_RESET                     400
#define FTS_DELAY_READ_ID                           20
#define FTS_DELAY_UPGRADE                           80
#define FTS_RETRIES_UPGRADE                         2

#define FTS_MIN_LEN                                 0x120
#define FTS_MAX_LEN_APP                             (64 * 1024)
#define FTS_VER_IN_FILE_ADDR			    		0x010A


/*Defined Macroes*/
#define FTS_FLASH_PACKET_LENGTH                     (128)

#define FTS_MAX_LEN_ECC_CALC                        (0xFFFE) /* must be even */

/*****************************************************************************
* Private variables/functions
*****************************************************************************/
static bool tp_fw_valid = false;/*to note firmware in TP controller is valid or not*/


/* The array variable fw_file_ft3x68 stores the firmware file that you
 * want to upgrade.
 * Please modify it based on the firmware file you get.
 * Please ignore it if you get firmware file from file system, now you
 * need read firmware file using your method.
 */
const uint8_t fw_file_ft3x68[] = {
#include "CY_FT6146_V04_20250325_app.i"
};


/*Functions*/
/************************************************************************
* Name: fts_fwupg_check_flash_status
* Brief:
*   read status from tp
* Input: @flash_status: correct value from tp
*        @retries: read retry times
*        @retries_delay: retry delay
* Output:
* Return:
*   return true if flash status check pass, otherwise return false
***********************************************************************/
static bool fts_fwupg_check_flash_status(uint16_t flash_status, int retries, int retries_delay)
{
    int ret = 0;
    int i = 0;
    uint8_t cmd = 0;
    uint8_t val[2] = { 0 };
    uint16_t read_status = 0;

    for (i = 0; i < retries; i++) {
        cmd = FTS_CMD_FLASH_STATUS;
        ret = fts_read(cmd , val, 2);
        read_status = (((uint16_t)val[0]) << 8) + val[1];
        if (flash_status == read_status) {
            /* FTS_DEBUG("[UPGRADE]flash status ok"); */
            return true;
        }
        /* FTS_DEBUG("flash status fail,ok:%04x read:%04x, retries:%d", flash_status, read_status, i); */
        fts_msleep(retries_delay);
    }

    return ret;
}

/*****************************************************************************
* Name: fts_check_id
* Brief:
*   The function is used to check id.
* Input:
* Output:@id_h, id chiper high
*		 @id_l, id chiper low
* Return:
*   return 0 if check id successfully, otherwise error code.
*****************************************************************************/
static int fts_check_id(uint8_t id_h, uint8_t id_l)
{
    int i = 0;
    uint8_t cmd = FTS_CMD_READ_ID;
    uint8_t buf[2] = { 0 };

    cmd = 0xC0;
    fts_write_reg(FTS_REG_UPGRADE, FTS_UPGRADE_AA);
    fts_read(cmd, buf, 2);
    FTS_INFO("cmd:%x %x", buf[0], buf[1]);
    fts_write_reg(FTS_REG_UPGRADE, FTS_UPGRADE_55);
    fts_read(cmd, buf, 2);
    FTS_INFO("cmd:%x %x", buf[0], buf[1]);
    fts_msleep(FTS_DELAY_UPGRADE);
    /*confirm in boot*/
    for (i = 0; i < FTS_RETRIES_CHECK_ID; i++) {
        fts_write_reg(FTS_UPGRADE_55, FTS_UPGRADE_AA);
        fts_msleep(FTS_DELAY_UPGRADE_AA);
        cmd = FTS_CMD_READ_ID;
        fts_read(cmd, buf, 2);
        if ((buf[0] != id_h) || (buf[1] != id_l)) {
            FTS_ERROR("check id fail,read id:0x%02x%02x != 0x%02x%02x,retry:%d",
                      buf[0], buf[1], id_h, id_l, i);
            return -1;
        } else
            break;

//        fts_write_reg(FTS_REG_UPGRADE, FTS_UPGRADE_AA);
//        fts_write_reg(FTS_REG_UPGRADE, FTS_UPGRADE_55);
//        fts_msleep(FTS_DELAY_READ_ID);
    }

    if (i >= 10)
        return -1;

    FTS_INFO("read boot id:%x %x", buf[0], buf[1]);
    return 0;
}


/************************************************************************
* Name: fts_fwupg_enter_into_boot
* Brief:
*   enter into boot environment, ready for upgrade
* Input:
* Output:
* Return:
*   return 0 if success, otherwise return error code
***********************************************************************/
static int fts_fwupg_enter_into_boot(void)
{
    int ret = 0;
//    uint8_t boot_id[2] = { 0 };

    /*software reset to boot mode*/
    if (tp_fw_valid) {
        ret = fts_write_reg(FTS_REG_UPGRADE, FTS_UPGRADE_AA);
        if (ret < 0) {
            FTS_ERROR("write FC=0xAA fail");
            return ret;
        }
        fts_msleep(FTS_DELAY_UPGRADE_AA);

        ret = fts_write_reg(FTS_REG_UPGRADE, FTS_UPGRADE_55);
        if (ret < 0) {
            FTS_ERROR("write FC=0x55 fail");
            return ret;
        }

        fts_msleep(FTS_DELAY_UPGRADE);
    }

    /*confirm TP controller is int romboot state*/
    ret = fts_check_id(FTS_CHIP_IDH, FTS_CHIP_IDL);
    if (ret < 0) {
        FTS_ERROR("checking id fails");
        return -1;
    }

    return 0;
}

/************************************************************************
* Name: fts_fwupg_erase
* Brief:
*   erase flash area
* Input: @delay: delay after erase
* Output:
* Return:
*   return 0 if success, otherwise return error code
***********************************************************************/
static int fts_fwupg_erase(uint32_t delay)
{
    int ret = 0;
    uint8_t cmd = 0;
    bool flag = false;

    FTS_INFO("**********erase now**********");
    /*send to erase flash*/
    cmd = FTS_CMD_ERASE_APP;
    ret = fts_write(cmd, NULL, 0);
    if (ret < 0) {
        FTS_ERROR("erase cmd fail");
        return ret;
    }
    fts_msleep(delay);

    /* read status 0xF0AA: success */
    flag = fts_fwupg_check_flash_status(FTS_CMD_FLASH_STATUS_ERASE_OK, FTS_RETRIES_REASE, FTS_RETRIES_DELAY_REASE);
    if (!flag) {
        FTS_ERROR("ecc flash status check fail");
        return -1;
    }

    return 0;
}

/************************************************************************
* Name: fts_flash_write_buf
* Brief:
*   write buf data to flash address
* Input: @saddr: start address data write to flash
*        @buf: data buffer
*        @len: data length
*        @delay: delay after write
* Output:
* Return:
*   return 0 if success, otherwise return error code
***********************************************************************/
static int fts_flash_write_buf(uint32_t saddr, uint8_t *buf, uint16_t len, uint32_t delay)
{
    int ret = 0;
    uint32_t i = 0;
    uint32_t j = 0;
    uint32_t packet_number = 0;
    uint16_t packet_len = 0;
    uint32_t addr = 0;
    uint32_t offset = 0;
    uint16_t remainder = 0;
    uint8_t packet_buf[FTS_FLASH_PACKET_LENGTH+6] = {0};
    uint8_t cmd = 0;
    uint8_t val[2] = { 0 };
    uint16_t read_status = 0;
    uint16_t wr_ok = 0;

    if (!buf || !len) {
        FTS_ERROR("buf/len is invalid");
        return -1;
    }

    FTS_INFO("data buf start addr=0x%lx, len=0x%x", saddr, len);
    packet_number = len / FTS_FLASH_PACKET_LENGTH;
    remainder = len % FTS_FLASH_PACKET_LENGTH;
    if (remainder > 0)
        packet_number++;
    packet_len = FTS_FLASH_PACKET_LENGTH;
    FTS_INFO("write data, num:%ld remainder:%d", packet_number, remainder);

    for (i = 0; i < packet_number; i++) {
        offset = i * FTS_FLASH_PACKET_LENGTH;
        addr = saddr + offset;
        packet_buf[0] = FTS_CMD_WRITE;
        packet_buf[1] = (addr >> 16);
        packet_buf[2] = (addr >> 8);
        packet_buf[3] = (addr);

        /* last packet */
        if ((i == (packet_number - 1)) && remainder)
            packet_len = remainder;

        packet_buf[4] = (packet_len >> 8);
        packet_buf[5] = (packet_len);

        memcpy(&packet_buf[6],(buf+offset),packet_len);

        ret = fts_write(packet_buf[0], &packet_buf[1], (packet_len+5));
        if (ret < 0) {
            FTS_ERROR("app write fail");
            return ret;
        }
        fts_msleep(FTS_CMD_READ_DELAY);

        /* read status */
        wr_ok = 0x1000 + addr / packet_len;
        for (j = 0; j < FTS_RETRIES_WRITE; j++) {
            cmd = FTS_CMD_FLASH_STATUS;
            ret = fts_read(cmd, val, 2);
            read_status = (((uint16_t)val[0]) << 8) + val[1];
            if (wr_ok == read_status)
                break;
            else
                FTS_DEBUG("%x %x", wr_ok, read_status);
            fts_msleep(FTS_CMD_READ_DELAY);
        }
    }

    return 0;
}


/************************************************************************
* Name: fts_fwupg_ecc_cal_host
* Brief:
*   Calculate the ecc value of firmware program.
* Input: @data: pointer to firmware program
*        @data_len: length of firmware program
*	     @ecc_value: store ecc value
* Output:
* Return:
*   ecc value calculated in host using XOR8 algorithm
***********************************************************************/
static int fts_ecc_cal_host(const uint8_t *data, uint32_t data_len)
{
    uint8_t ecc = 0;
    uint32_t i = 0;

    for (i = 0; i < data_len; i++ ) {
        ecc ^= data[i];
    }

    return ecc;
}


/************************************************************************
* Name: fts_fwupg_ecc_cal
* Brief:
*   calculate and get ecc from tp
* Input: @saddr: start address need calculate ecc
*        @len: length need calculate ecc
* Output:
* Return:
*    return data ecc of tp if success, otherwise return error code
***********************************************************************/
static int fts_fwupg_ecc_tp(uint32_t saddr, uint16_t len)
{
    int ret = 0;
    uint8_t wbuf[7] = { 0 };
    uint8_t val[2] = { 0 };
    bool bflag = false;
    uint8_t cmd = 0;
    uint8_t regaddr = 0;
	uint32_t packet_num = 0;
//    uint32_t packet_len = 0;
    uint32_t remainder = 0;

    /* check sum init */
    cmd = FTS_CMD_ECC_INIT;
    ret = fts_write(cmd, NULL, 0);
    if (ret < 0) {
        FTS_ERROR("ecc init cmd write fail");
        return ret;
    }

	packet_num = len / FTS_MAX_LEN_ECC_CALC;
	remainder = len % FTS_MAX_LEN_ECC_CALC;
   if (remainder)
	   packet_num++;
//   packet_len = FTS_MAX_LEN_ECC_CALC;

	for(uint32_t i=0;i < packet_num; i++){
    /* send commond to start checksum */
    wbuf[0] = FTS_CMD_ECC_CAL;
    wbuf[1] = (saddr >> 16);
    wbuf[2] = (saddr >> 8);
    wbuf[3] = (saddr);
    wbuf[4] = (len >> 8);
    wbuf[5] = (len );

//    FTS_DEBUG("ecc calc startaddr:0x%04x, len:%d", saddr, len);
    ret = fts_write(wbuf[0], &wbuf[1] , (FTS_CMD_ECC_CAL_LEN-1));
    if (ret < 0) {
        FTS_ERROR("ecc calc cmd write fail");
        return ret;
    }

    fts_msleep(len / 256);

    /* read status if check sum is finished */
    bflag = fts_fwupg_check_flash_status(FTS_CMD_FLASH_STATUS_ECC_OK, FTS_RETRIES_ECC_CAL, FTS_RETRIES_DELAY_ECC_CAL);
    if (!bflag) {
        FTS_ERROR("ecc flash status read fail");
        return -1;
    }
	}

    /* read out check sum */
    regaddr = FTS_CMD_ECC_READ;
    ret = fts_read(regaddr, val, 1);
    if (ret < 0) {
        FTS_ERROR( "ecc read cmd write fail");
        return ret;
    }

    return (val[0]);
}



/*****************************************************************************
* Name: fts_ft3x68_upgrade
* Brief:
*   Main flow of FT3x68 firmware upgrade.
* Input: @fw_file: firmware file buffer
*        @fw_file_size: firmware file size
* Output:
* Return:
*   Error code if upgrade fails, 0 if success.
*****************************************************************************/
static int fts_ft3x68_upgrade(uint8_t *fw_file, uint32_t fw_file_size)
{
    int ret = 0;
    uint8_t rst_cmd = FTS_CMD_RESET;
//    uint8_t cmd[4] = { 0 };
    uint8_t *firmware;
    uint32_t firmware_size;
    uint32_t start_address = 0;
    int ecc_in_host = 0;
    int ecc_in_tp = 0;


    if (!fw_file || (fw_file_size < FTS_MIN_LEN) || (fw_file_size > (37 * 1024))) {
        FTS_ERROR("fw file is null, or fw file size(%ld) is invalid", fw_file_size);
        return -1;
    }

    /*get firmware data*/
    firmware = fw_file;
    firmware_size = fw_file_size;

    /*enter into boot environment*/
    ret = fts_fwupg_enter_into_boot();
    if (ret < 0) {
        FTS_ERROR("enter into boot fails");
        goto err_upgrade;
    }
#if 0
    /*send firmware size*/
    cmd[0] = FTS_CMD_APP_DATA_LEN;
    cmd[1] = (firmware_size >> 16);
    cmd[2] = (firmware_size >> 8);
    cmd[3] = (firmware_size);
    ret = fts_write(cmd[0], &cmd[1], 3);
    if (ret < 0) {
        FTS_ERROR("write 7A fails");
        return ret;
    }

#endif
    /*Erase firmware part in flash*/
    ret = fts_write_reg(FTS_CMD_FLASH_MODE, FTS_FLASH_MODE_UPGRADE_VALUE);
    if (ret < 0) {
        FTS_ERROR("upgrade mode(09) cmd write fail");
        goto err_upgrade;
    }

    ret = fts_fwupg_erase(60 * (firmware_size / 4096));
    if (ret < 0) {
        FTS_ERROR("erase cmd write fail");
        goto err_upgrade;
    }

    /*write firmware data into flash*/
    start_address = FTS_CMD_FW_START_ADDRESS;
    ret = fts_flash_write_buf(start_address, firmware, firmware_size, 1);
    if (ret < 0 ) {
        FTS_ERROR("write buffer to flash fail");
        goto err_upgrade;
    }

    ecc_in_host = fts_ecc_cal_host(firmware, firmware_size);
    ecc_in_tp = fts_fwupg_ecc_tp(start_address, firmware_size);
    FTS_INFO("ecc in tp:%x, host:%x", ecc_in_tp, ecc_in_host);
    if (ecc_in_tp != ecc_in_host) {
        FTS_ERROR("ecc check fail");
        goto err_upgrade;
    }

    FTS_INFO("upgrade success, reset to normal boot");
    ret = fts_write(rst_cmd, NULL, 0);
    if (ret < 0) {
        FTS_ERROR("reset to normal boot fail");
    }
    fts_msleep(FTS_DELAY_UPGRADE_RESET);

    return 0;

err_upgrade:
    ret = fts_write(rst_cmd, NULL, 0);
    if (ret < 0) {
        FTS_ERROR("reset to normal boot fail");
    }
    return -1;
}


/*****************************************************************************
* Name: fts_fwupg_check_fw_valid
* Brief:
*   To check firmware in TP controller is valid or not.
* Input:
* Output:
* Return:
*   true: fw is valid, false: fw is invalid
*****************************************************************************/
static bool fts_fwupg_check_fw_valid(void)
{
    int ret = 0;
    int i = 0;
    uint8_t id = 0xFF;

    do {
        /*loop to read ID because some time is needed for TP controller initialization*/
        ret = fts_read_reg(FTS_REG_CHIP_ID, &id);
        if (id == FTS_CHIP_IDH) {
            FTS_DEBUG("TP Ready,Device ID:0x%02x", id);
            return true;
        } else {
            FTS_DEBUG("TP Not Ready,Read:0x%02x,ret:%d", id, ret);
        }
        fts_msleep(INTERVAL_READ_REG);
    } while (i++ < 5);

    return false;
}

/*****************************************************************************
* Name: fts_fwupg_need_upgrade
* Brief:
*   To check firmware upgrade is needed or not. Host need upgrade firmware in
*   the following situations(one of them):
*     a. firwmare in TP controller is invalid.
*     b. firmware versions in TP controller and host are different.
* Input: @fw_file: firmware file buffer
*        @fw_file_size: firmware file size
* Output:
* Return:
*   true: firmware upgrade is needed, false: not needed
*****************************************************************************/
static bool fts_fwupg_need_upgrade(uint8_t *fw_file, uint32_t fw_file_size)
{
    int ret = 0;
    uint8_t fw_ver_in_host = 0;
    uint8_t fw_ver_in_tp = 0;

    if (!tp_fw_valid) {
        FTS_DEBUG("firmware in TP controller is invalid, need upgrade");
        return true;
    }

    ret = fts_read_reg(FTS_REG_FW_VER, &fw_ver_in_tp);
    if (ret < 0) {
        FTS_ERROR("read firmware version from reg0xA6 fals");
        return false;
    }

    if (fw_file_size > FTS_MIN_LEN)
        fw_ver_in_host = fw_file[FTS_VER_IN_FILE_ADDR];
    FTS_INFO("fw version in tp:%x, host:%x", fw_ver_in_tp, fw_ver_in_host);
    if (fw_ver_in_tp != fw_ver_in_host) {
        return true;
    }

    return false;
}


/*****************************************************************************
* Name: fts_fwupg_upgrade
* Brief:
*   The whole flow of firmware upgrade.
* Input: @fw_file: firmware file buffer
*        @fw_file_size: firmware file size
* Output:
* Return:
*   Error code if upgrade fails, 0 if success.
*****************************************************************************/
static int fts_fwupg_upgrade(uint8_t *fw_file, uint32_t fw_file_size)
{
    int ret = 0;
    bool upgrade_flag = false;
    uint8_t fw_ver = 0;
    uint8_t upgrade_count = 0;

    /*check firmware upgrade is needed or not*/
    upgrade_flag = fts_fwupg_need_upgrade(fw_file, fw_file_size);
    FTS_INFO("fw upgrade flag:%d", upgrade_flag);
    if (upgrade_flag) {
        do {
            upgrade_count++;
            ret = fts_ft3x68_upgrade(fw_file, fw_file_size);
            if (ret >= 0) {
                fts_read_reg(FTS_REG_FW_VER, &fw_ver);
                FTS_INFO("success upgrade to fw version %02x", fw_ver);
                break;
            }
        } while (upgrade_count < FTS_RETRIES_UPGRADE);
    }

    return ret;
}

/*****************************************************************************
* Name: fts_fwupg_auto_upgrade
* Brief:
*   firmware auto upgrade.
* Input:
* Output:
* Return:
*   Error code if auto upgrade fails, 0 if success.
*****************************************************************************/
int fts_fwupg_auto_upgrade(void)
{
    int ret = 0;
    uint8_t *fw_file = fw_file_ft3x68;
    uint32_t fw_file_size = sizeof(fw_file_ft3x68);

    FTS_INFO("********************auto upgrade********************");
    /* Get firmware file, and check firmware size
     * we use all.i as an example(variable fw_file_ft3x68 stores the firmware).
     * You should read it if you use all.bin
     */

    if (!fw_file || (fw_file_size < FTS_MIN_LEN)) {
        FTS_ERROR("fw_file is null, or firmare file size(%ld) is invalid", fw_file_size);
        return -1;
    }

    /*check firmware is valid or not*/
    tp_fw_valid = fts_fwupg_check_fw_valid();
    if (!tp_fw_valid) {
        FTS_DEBUG("firmware in flash is invalid");
    }

    /******run firmware upgrade flow******/
    ret = fts_fwupg_upgrade(fw_file, fw_file_size);
    if (ret < 0){
        FTS_ERROR("**********tp fw upgrade fails**********");
    }else{
        FTS_INFO("**********tp fw no upgrade/upgrade success**********");
	}

    return ret;
}

