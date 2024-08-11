/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * Development of the code in this file was sponsored by Microbric Pty Ltd
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2016 Damien P. George
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

#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <sys/time.h>
#include <time.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_task.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "startup/oled.h"
#include "esp_timer.h"		// add by zkh
#include "driver/timer.h"

#include "py/stackctrl.h"
#include "py/nlr.h"
#include "py/compile.h"
#include "py/runtime.h"
#include "py/persistentcode.h"
#include "py/repl.h"
#include "py/gc.h"
#include "py/mphal.h"
#include "shared/readline/readline.h"
#include "shared/runtime/pyexec.h"
#include "shared/timeutils/timeutils.h"
#include "mbedtls/platform_time.h"

#include "uart.h"
#include "usb.h"
#include "usb_serial_jtag.h"
#include "modmachine.h"
#include "modnetwork.h"

#if MICROPY_BLUETOOTH_NIMBLE
#include "extmod/modbluetooth.h"
#endif

#if MICROPY_PY_ESPNOW
#include "modespnow.h"
#endif

static uint16_t hw_init_flags = 0;
const char msg_iic_failed[] = "IIC硬件错误(IIC Hardfault),系统无法正常工作!IIC连线是否接反?请移除IIC总线上的所有设备后重试!\n";

// MicroPython runs as a task under FreeRTOS
#define MP_TASK_PRIORITY        (ESP_TASK_PRIO_MIN + 1)

// Set the margin for detecting stack overflow, depending on the CPU architecture.
#if CONFIG_IDF_TARGET_ESP32C3
#define MP_TASK_STACK_LIMIT_MARGIN (2048)
#else
#define MP_TASK_STACK_LIMIT_MARGIN (1024)
#endif

int vprintf_null(const char *format, va_list ap) {
    // do nothing: this is used as a log target during raw repl mode
    return 0;
}

volatile uint32_t ticker_ticks_ms = 0;
extern void mpython_music_tick(void);
static void timer_1ms_ticker(void *args)
{
    ticker_ticks_ms += 1;
    mpython_music_tick();
}

void mpython_display_exception(mp_obj_t exc_in)
{
    size_t n, *values;
    mp_obj_exception_get_traceback(exc_in, &n, &values);
    if (1) {
        vstr_t vstr;
        mp_print_t print;
        vstr_init_print(&vstr, 50, &print);
        #if MICROPY_ENABLE_SOURCE_LINE
        if (n >= 3) {
            mp_printf(&print, "line %u\n", values[1]);
        }
        #endif
        if (mp_obj_is_native_exception_instance(exc_in)) {
            mp_obj_exception_t *exc = (mp_obj_exception_t*)MP_OBJ_TO_PTR(exc_in);
            mp_printf(&print, "%q:\n  ", exc->base.type->name);
            if (exc->args != NULL && exc->args->len != 0) {
                mp_obj_print_helper(&print, exc->args->items[0], PRINT_STR);
            }
        }
        oled_init();
        oled_clear();
        oled_print(vstr_null_terminated_str(&vstr), 0, 0);
        oled_show();
        vstr_clear(&vstr);
        oled_deinit();
    }
}

void mpython_stop_timer(void) {
    // disable all timer and thread created by main.py
    for (timer_group_t g = TIMER_GROUP_0; g < TIMER_GROUP_MAX; g++) {
        for (timer_idx_t i = TIMER_0; i < TIMER_MAX; i++) {
            timer_pause(g, i);
        }
    }
}

void mpython_stop_thread(void) {
    #if MICROPY_PY_THREAD
    mp_thread_deinit();
    #endif  
}

time_t platform_mbedtls_time(time_t *timer) {
    // mbedtls_time requires time in seconds from EPOCH 1970

    struct timeval tv;
    gettimeofday(&tv, NULL);

    return tv.tv_sec + TIMEUTILS_SECONDS_1970_TO_2000;
}

void mp_task(void *pvParameter) {
    volatile uint32_t sp = (uint32_t)esp_cpu_get_sp();
    #if MICROPY_PY_THREAD
    mp_thread_init(pxTaskGetStackStart(NULL), MICROPY_TASK_STACK_SIZE / sizeof(uintptr_t));
    #endif
    #if CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG
    usb_serial_jtag_init();
    #elif CONFIG_USB_OTG_SUPPORTED
    usb_init();
    #endif
    #if MICROPY_HW_ENABLE_UART_REPL
    uart_stdout_init();
    #endif
    machine_init();

    // Configure time function, for mbedtls certificate time validation.
    mbedtls_platform_set_time(platform_mbedtls_time);

    esp_err_t err = esp_event_loop_create_default();
    if (err != ESP_OK) {
        ESP_LOGE("esp_init", "can't create event loop: 0x%x\n", err);
    }

    void *mp_task_heap = MP_PLAT_ALLOC_HEAP(MICROPY_GC_INITIAL_HEAP_SIZE);
    if (mp_task_heap == NULL) {
        printf("mp_task_heap allocation failed!\n");
        esp_restart();
    }

soft_reset:
    hw_init_flags = 0;
    // startup
    // iic总线错误,打印提示信息
    if (oled_init() == false) { 
        ESP_LOGE("system", "%s", msg_iic_failed);
        hw_init_flags |= 0x0001;
    } else {
        oled_drawImg(img_mpython);
        // oled_drawImg(img_InnovaBit);
        oled_show();
        oled_deinit();
    }

    // initialise the stack pointer for the main thread
    mp_stack_set_top((void *)sp);
    mp_stack_set_limit(MICROPY_TASK_STACK_SIZE - MP_TASK_STACK_LIMIT_MARGIN);
    gc_init(mp_task_heap, mp_task_heap + MICROPY_GC_INITIAL_HEAP_SIZE);
    mp_init();
    mp_obj_list_append(mp_sys_path, MP_OBJ_NEW_QSTR(MP_QSTR__slash_lib));
    readline_init0();

    MP_STATE_PORT(native_code_pointers) = MP_OBJ_NULL;

    // initialise peripherals
    machine_pins_init();
    #if MICROPY_PY_MACHINE_I2S
    machine_i2s_init0();
    #endif

	// for music function
	const esp_timer_create_args_t periodic_timer_args = {
		.callback = &timer_1ms_ticker,
		.name = "music tick timer"
	};
	esp_timer_handle_t periodic_timer;
    ticker_ticks_ms = 0;
	ESP_ERROR_CHECK(esp_timer_create(&periodic_timer_args, &periodic_timer));
	ESP_ERROR_CHECK(esp_timer_start_periodic(periodic_timer, 1000));
    
    // run boot-up scripts
    pyexec_frozen_module("_boot.py", false);
    int ret = pyexec_file_if_exists("boot.py");
    if (ret & PYEXEC_FORCED_EXIT) {
        goto soft_reset_exit;
    }
    if (pyexec_mode_kind == PYEXEC_MODE_FRIENDLY_REPL && ret != 0) {
        int ret = pyexec_file_if_exists("main.py");
        if (ret & PYEXEC_FORCED_EXIT) {
            goto soft_reset_exit;
        }
    }

    for (;;) {
        if (pyexec_mode_kind == PYEXEC_MODE_RAW_REPL) {
            vprintf_like_t vprintf_log = esp_log_set_vprintf(vprintf_null);
            if (pyexec_raw_repl() != 0) {
                break;
            }
            esp_log_set_vprintf(vprintf_log);
        } else {
            if (pyexec_friendly_repl() != 0) {
                break;
            }
        }
    }

soft_reset_exit:

    #if MICROPY_BLUETOOTH_NIMBLE
    mp_bluetooth_deinit();
    #endif

    #if MICROPY_PY_ESPNOW
    espnow_deinit(mp_const_none);
    MP_STATE_PORT(espnow_singleton) = NULL;
    #endif

    machine_timer_deinit_all();

    #if MICROPY_PY_THREAD
    mp_thread_deinit();
    #endif

    // Free any native code pointers that point to iRAM.
    if (MP_STATE_PORT(native_code_pointers) != MP_OBJ_NULL) {
        size_t len;
        mp_obj_t *items;
        mp_obj_list_get(MP_STATE_PORT(native_code_pointers), &len, &items);
        for (size_t i = 0; i < len; ++i) {
            heap_caps_free(MP_OBJ_TO_PTR(items[i]));
        }
    }

    gc_sweep_all();

    mp_hal_stdout_tx_str("MPY: soft reboot\r\n");

    // deinitialise peripherals
    machine_pwm_deinit_all();
    // TODO: machine_rmt_deinit_all();
    machine_pins_deinit();
    machine_deinit();
    #if MICROPY_PY_SOCKET_EVENTS
    socket_events_deinit();
    #endif

    mp_deinit();
    fflush(stdout);
    goto soft_reset;
}

void boardctrl_startup(void) {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }
}

void app_main(void) {
    // Hook for a board to run code at start up.
    // This defaults to initialising NVS.
    MICROPY_BOARD_STARTUP();

    // Create and transfer control to the MicroPython task.
    xTaskCreatePinnedToCore(mp_task, "mp_task", MICROPY_TASK_STACK_SIZE / sizeof(StackType_t), NULL, MP_TASK_PRIORITY, &mp_main_task_handle, MP_TASK_COREID);
}

void nlr_jump_fail(void *val) {
    printf("NLR jump failed, val=%p\n", val);
    esp_restart();
}

void *esp_native_code_commit(void *buf, size_t len, void *reloc) {
    len = (len + 3) & ~3;
    uint32_t *p = heap_caps_malloc(len, MALLOC_CAP_EXEC);
    if (p == NULL) {
        m_malloc_fail(len);
    }
    if (MP_STATE_PORT(native_code_pointers) == MP_OBJ_NULL) {
        MP_STATE_PORT(native_code_pointers) = mp_obj_new_list(0, NULL);
    }
    mp_obj_list_append(MP_STATE_PORT(native_code_pointers), MP_OBJ_TO_PTR(p));
    if (reloc) {
        mp_native_relocate(reloc, buf, (uintptr_t)p);
    }
    memcpy(p, buf, len);
    return p;
}

MP_REGISTER_ROOT_POINTER(mp_obj_t native_code_pointers);
