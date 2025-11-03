/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2023 Damien P. George
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include "py/runtime.h"

#if MICROPY_PY_ASR

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static mp_obj_t asr_init(void) {

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(asr_init_obj, asr_init);

static const mp_rom_map_elem_t asr_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_asr) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&asr_init_obj)},
};
static MP_DEFINE_CONST_DICT(asr_module_globals, asr_module_globals_table);

const mp_obj_module_t mp_module_asr = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&asr_module_globals,
};

MP_REGISTER_EXTENSIBLE_MODULE(MP_QSTR_asr, mp_module_asr);

#endif // MICROPY_PY_ASR
