#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "py/mperrno.h"
#include "py/mphal.h"
#include "py/runtime.h"
#include "extmod/modmachine.h"
#include "mfrc522.h"

#if MICROPY_PY_RFID

#define MFRC522_ADDR (47) 
#define MAX_LEN (16)
// static const char *TAG = "RFID";
static mp_obj_base_t *i2c_obj = NULL;

typedef struct{
    mp_obj_base_t base;
    uint8_t i2c_addr;
}rfid_obj_t;

const mp_obj_type_t rfid_522_type;
rfid_obj_t rfid_obj[2] = {
    {{&rfid_522_type}, 47}, 
    {{&rfid_522_type}, 43}, 
};

//原扇区A密码，16个扇区，每个扇区密码6Byte
static uint8_t sectorKeyA[16][6] = {
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF },
		{ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF }, };

static mp_obj_t mfrc522_init(mp_obj_t self_in, mp_obj_t i2c) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if(!i2c_obj)
        i2c_obj = (mp_obj_base_t *)MP_OBJ_TO_PTR(i2c);
    RFID_init(self->i2c_addr);
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(mfrc522_init_obj, mfrc522_init);

static mp_obj_t mfrc522_find_card(mp_obj_t self_in) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    unsigned char str[MAX_LEN];

	if (RFID_findCard(self->i2c_addr,PICC_REQIDL, str) == MI_OK)
	{
        return MP_OBJ_NEW_SMALL_INT(str[0] + (((uint16_t)str[1]) << 8));   
	}

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(mfrc522_find_card_obj, mfrc522_find_card);

static mp_obj_t mfrc522_anticoll(mp_obj_t self_in) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    unsigned char str[MAX_LEN];
    // uint8_t serNum[5];       // 4字节卡序列号，第5字节为校验字节

	if (RFID_anticoll(self->i2c_addr, str) == MI_OK)
	{
        mp_obj_t serNum[5] = {
            serNum[0] = mp_obj_new_int(str[0]),
            serNum[1] = mp_obj_new_int(str[1]),
            serNum[2] = mp_obj_new_int(str[2]),
            serNum[3] = mp_obj_new_int(str[3]),
            serNum[4] = mp_obj_new_int(str[4]),
        };
        return mp_obj_new_tuple(5, serNum);   
	}
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(mfrc522_anticoll_obj, mfrc522_anticoll);

static mp_obj_t mfrc522_select_tag(mp_obj_t self_in, mp_obj_t serialNum) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    // unsigned char str[MAX_LEN];
    uint8_t serNum[5];       // 4字节卡序列号，第5字节为校验字节
    mp_obj_t *elem;\
    uint16_t size;

    mp_obj_get_array_fixed_n(serialNum, 5, &elem);
    serNum[0] = mp_obj_get_int(elem[0]);
    serNum[1] = mp_obj_get_int(elem[1]);
    serNum[2] = mp_obj_get_int(elem[2]);
    serNum[3] = mp_obj_get_int(elem[3]);
    serNum[4] = mp_obj_get_int(elem[4]);

    size = RFID_selectTag(self->i2c_addr, serNum);
	if (size > 0)
        return MP_OBJ_NEW_SMALL_INT(size);   

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(mfrc522_select_tag_obj, mfrc522_select_tag);

static mp_obj_t mfrc522_auth(mp_obj_t self_in, mp_obj_t serialNum, mp_obj_t block) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    uint8_t serNum[5];       // 4字节卡序列号，第5字节为校验字节
    mp_obj_t *elem;
    int _block = mp_obj_get_int(block);

    mp_obj_get_array_fixed_n(serialNum, 5, &elem);
    serNum[0] = mp_obj_get_int(elem[0]);
    serNum[1] = mp_obj_get_int(elem[1]);
    serNum[2] = mp_obj_get_int(elem[2]);
    serNum[3] = mp_obj_get_int(elem[3]);
    serNum[4] = mp_obj_get_int(elem[4]);

    if (RFID_auth(self->i2c_addr, PICC_AUTHENT1A, _block, sectorKeyA[_block / 4], serNum) == MI_OK) //卡认证
        return MP_OBJ_NEW_SMALL_INT(1);   

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_3(mfrc522_auth_obj, mfrc522_auth);  

/* 以下所有操作须先完成寻卡及卡密验证工作先*/
static mp_obj_t mfrc522_read_block(mp_obj_t self_in, mp_obj_t block) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    int _block = mp_obj_get_int(block);
    vstr_t vstr;
    vstr_init_len(&vstr, 16);
    if (RFID_readBlock(self->i2c_addr, _block, (uint8_t*)vstr.buf) == MI_OK)
        return mp_obj_new_str_from_vstr(&vstr);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(mfrc522_read_block_obj, mfrc522_read_block);

static mp_obj_t mfrc522_write_block(mp_obj_t self_in, mp_obj_t block, mp_obj_t buf_in) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    int _block = mp_obj_get_int(block);
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(buf_in, &bufinfo, MP_BUFFER_READ);
    if (RFID_writeBlock(self->i2c_addr, _block, bufinfo.buf) == MI_OK)
        return MP_OBJ_NEW_SMALL_INT(1);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_3(mfrc522_write_block_obj, mfrc522_write_block);

static mp_obj_t mfrc522_increment(mp_obj_t self_in, mp_obj_t block, mp_obj_t value) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    int _block = mp_obj_get_int(block);
    int32_t pvalue = mp_obj_get_int(value);

    if (RFID_IncDecCardBlock(self->i2c_addr, PICC_INCREMENT, _block, pvalue) == MI_OK)
        return MP_OBJ_NEW_SMALL_INT(1);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_3(mfrc522_increment_obj, mfrc522_increment);

static mp_obj_t mfrc522_decrement(mp_obj_t self_in, mp_obj_t block, mp_obj_t value) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    int _block = mp_obj_get_int(block);
    int32_t pvalue = mp_obj_get_int(value);

    if (RFID_IncDecCardBlock(self->i2c_addr, PICC_DECREMENT, _block, pvalue) == MI_OK)
        return MP_OBJ_NEW_SMALL_INT(1);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_3(mfrc522_decrement_obj, mfrc522_decrement);

static mp_obj_t mfrc522_set_purse(mp_obj_t self_in, mp_obj_t block) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    uint8_t _block = (uint8_t)mp_obj_get_int(block);
    uint8_t data1[16] = { 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 
                          _block, ~_block, _block, ~_block };
    if (RFID_writeBlock(self->i2c_addr, _block, data1) == MI_OK)
        return MP_OBJ_NEW_SMALL_INT(1);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(mfrc522_set_purse_obj, mfrc522_set_purse);

static mp_obj_t mfrc522_balance(mp_obj_t self_in, mp_obj_t block) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    int _block = mp_obj_get_int(block);
    uint8_t buff[4];

    if (RFID_readBlock(self->i2c_addr, _block, buff) == MI_OK)
        return mp_obj_new_int(buff[0] + (((int32_t)buff[1]) << 8) + (((int32_t)buff[2]) << 16) + (((int32_t)buff[3]) << 24));

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(mfrc522_balance_obj, mfrc522_balance);

static mp_obj_t mfrc522_halt(mp_obj_t self_in) {
    rfid_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if (RFID_halt(self->i2c_addr ) == MI_OK)
        return MP_OBJ_NEW_SMALL_INT(1);

    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(mfrc522_halt_obj, mfrc522_halt);

static mp_obj_t rfid_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    enum { ARG_i2c, ARG_i2c_addr};
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_i2c, MP_ARG_OBJ | MP_ARG_REQUIRED, {.u_obj = MP_OBJ_NULL}},
        { MP_QSTR_i2c_addr, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 47}},
    };

    // parse args
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    rfid_obj_t *self = NULL;
    if(args[ARG_i2c_addr].u_int == 47) {
        self = &rfid_obj[0];
    }else if(args[ARG_i2c_addr].u_int == 43) {
        self = &rfid_obj[1];
    }

    if(!i2c_obj)
        i2c_obj = (mp_obj_base_t *)MP_OBJ_TO_PTR(args[ARG_i2c].u_obj);

    if(!self)
        mp_raise_ValueError("Invalid i2c address");

    RFID_init(self->i2c_addr);

    return MP_OBJ_FROM_PTR(self);
}

static const mp_map_elem_t mpython_rfid_locals_dict_table[] = {
    {MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_rfid_522)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_init), (mp_obj_t)&mfrc522_init_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_find_card), (mp_obj_t)&mfrc522_find_card_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_anticoll), (mp_obj_t)&mfrc522_anticoll_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_select_tag), (mp_obj_t)&mfrc522_select_tag_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_auth), (mp_obj_t)&mfrc522_auth_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_read_block), (mp_obj_t)&mfrc522_read_block_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_write_block), (mp_obj_t)&mfrc522_write_block_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_increment), (mp_obj_t)&mfrc522_increment_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_decrement), (mp_obj_t)&mfrc522_decrement_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_set_purse), (mp_obj_t)&mfrc522_set_purse_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_balance), (mp_obj_t)&mfrc522_balance_obj},
    {MP_OBJ_NEW_QSTR(MP_QSTR_halt), (mp_obj_t)&mfrc522_halt_obj},
};

static MP_DEFINE_CONST_DICT(mpython_rfid_locals_dict, mpython_rfid_locals_dict_table);

MP_DEFINE_CONST_OBJ_TYPE(
    rfid_522_type,
    MP_QSTR_rfid,
    MP_TYPE_FLAG_NONE,
    make_new, rfid_make_new,
    // print, rfid_print,
    locals_dict, &mpython_rfid_locals_dict
    );

static const mp_rom_map_elem_t rfid_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_rfid) },
    { MP_ROM_QSTR(MP_QSTR_rfid_522), MP_ROM_PTR(&rfid_522_type) },
};
static MP_DEFINE_CONST_DICT(rfid_module_globals, rfid_module_globals_table);

const mp_obj_module_t mp_module_rfid = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&rfid_module_globals,
};

MP_REGISTER_EXTENSIBLE_MODULE(MP_QSTR_rfid, mp_module_rfid);

void writeReg(uint8_t i2c_addr, uint8_t reg_addr, uint8_t val)
{
    // mp_machine_i2c_p_t *i2c_p = (mp_machine_i2c_p_t*)i2c_obj->type->protocol;
    mp_machine_i2c_p_t *i2c_p = (mp_machine_i2c_p_t *)MP_OBJ_TYPE_GET_SLOT(i2c_obj->type, protocol);
    uint8_t temp[2];
    temp[0] = (uint8_t)reg_addr;
    temp[1] = val;

    mp_machine_i2c_buf_t buf = {.len = 2, .buf = temp};
    bool stop = true;
    unsigned int flags = stop ? MP_MACHINE_I2C_FLAG_STOP : 0;
    int ret = i2c_p->transfer((mp_obj_base_t *)i2c_obj, i2c_addr, 1, &buf, flags);
    if (ret < 0) {
        mp_raise_OSError(-ret);
    }
}

uint8_t readReg(uint8_t i2c_addr, uint8_t reg_addr)
{
	uint8_t buff; 
    // mp_machine_i2c_p_t *i2c_p = (mp_machine_i2c_p_t*)i2c_obj->type->protocol;
    mp_machine_i2c_p_t *i2c_p = (mp_machine_i2c_p_t *)MP_OBJ_TYPE_GET_SLOT(i2c_obj->type, protocol);

    uint8_t _reg_addr = reg_addr;
    mp_machine_i2c_buf_t buf = {.len = 1, .buf = (uint8_t*)&_reg_addr};
    bool stop = false;
    unsigned int flags = stop ? MP_MACHINE_I2C_FLAG_STOP : 0;
    int ret = i2c_p->transfer((mp_obj_base_t *)i2c_obj, i2c_addr, 1, &buf, flags);
    if (ret < 0) {
        mp_raise_OSError(-ret);
    }

    buf.len = 1;
    buf.buf = &buff;
    stop = true;
    flags = MP_MACHINE_I2C_FLAG_READ | (stop ? MP_MACHINE_I2C_FLAG_STOP : 0);
    ret = i2c_p->transfer((mp_obj_base_t *)i2c_obj, i2c_addr, 1, &buf, flags);
    if (ret < 0) {
        mp_raise_OSError(-ret);
    }

  return(buff);
}

#endif // MICROPY_PY_RFID
