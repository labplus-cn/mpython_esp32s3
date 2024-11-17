/*
 * ESPRESSIF MIT License
 *
 * Copyright (c) 2018 <ESPRESSIF SYSTEMS (SHANGHAI) PTE LTD>
 *
 * Permission is hereby granted for use on all ESPRESSIF SYSTEMS products, in which case,
 * it is free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the Software is furnished
 * to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or
 * substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */

#ifndef _HTTP_STREAM_H_
#define _HTTP_STREAM_H_

#include "esp_err.h"
#include "esp_system.h"
#include "esp_http_client.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief      HTTP Stream hook type
 */
typedef enum {
    HTTP_STREAM_PRE_REQUEST = 0x01, /*!< The event handler will be called before HTTP Client making the connection to the server */
    HTTP_STREAM_ON_REQUEST,         /*!< The event handler will be called when HTTP Client is requesting data,
                                     * If the fucntion return the value (-1: ESP_FAIL), HTTP Client will be stopped
                                     * If the fucntion return the value > 0, HTTP Stream will ignore the post_field
                                     * If the fucntion return the value = 0, HTTP Stream continue send data from post_field (if any)
                                     */
    HTTP_STREAM_ON_RESPONSE,        /*!< The event handler will be called when HTTP Client is receiving data
                                     * If the fucntion return the value (-1: ESP_FAIL), HTTP Client will be stopped
                                     * If the fucntion return the value > 0, HTTP Stream will ignore the read function
                                     * If the fucntion return the value = 0, HTTP Stream continue read data from HTTP Server
                                     */
    HTTP_STREAM_POST_REQUEST,       /*!< The event handler will be called after HTTP Client send header and body to the server, before fetching the headers */
    HTTP_STREAM_FINISH_REQUEST,     /*!< The event handler will be called after HTTP Client fetch the header and ready to read HTTP body */
    HTTP_STREAM_RESOLVE_ALL_TRACKS,
    HTTP_STREAM_FINISH_TRACK,
    HTTP_STREAM_FINISH_PLAYLIST,
} http_stream_event_id_t;


/**
 * @brief      HTTP Stream configurations
 *             Default value will be used if any entry is zero
 */
typedef struct {
    int                         out_rb_size;            /*!< Size of output ringbuffer */
    bool                        stack_in_ext;           /*!< Try to allocate stack in external memory */
    // http_stream_event_handle_t  event_handle;           /*!< The hook function for HTTP Stream */
    void                        *user_data;             /*!< User data context */
    int                         multi_out_num;          /*!< The number of multiple output */
    const char                  *cert_pem;              /*!< SSL server certification, PEM format as string, if the client requires to verify server */
    esp_err_t (*crt_bundle_attach)(void *conf);         /*!< Function pointer to esp_crt_bundle_attach. Enables the use of certification
                                                             bundle for server verification, must be enabled in menuconfig */
    int                         request_size;           /*!< Request data size each time from `http_client`
                                                             Defaults use DEFAULT_ELEMENT_BUFFER_LENGTH if set to 0
                                                             Need care this setting if audio frame size is small and want low latency playback */                                                         
    int                         request_range_size;     /*!< Range size setting for header `Range: bytes=start-end`
                                                             Request full range of resource if set to 0
                                                             Range size bigger than request size is recommended */
    const char                  *user_agent;            /*!< The User Agent string to send with HTTP requests */
} http_stream_cfg_t;

typedef struct http_stream {
    bool                            is_open;
    esp_http_client_handle_t        client;
    esp_audio_simple_dec_type_t     stream_type;
    int                             _errno;            /* errno code for http */
    int                             connect_times;     /* max reconnect times */
    const char                     *cert_pem;
#if (ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(4, 3, 0))
    esp_err_t                      (*crt_bundle_attach)(void *conf); /*  Function pointer to esp_crt_bundle_attach*/
#endif
    bool                            gzip_encoding;     /* Content is encoded */
    // gzip_miniz_handle_t             gzip;              /* GZIP instance */
    int                             request_range_size;
    int64_t                         request_range_end;
    bool                            is_last_range;
    const char                      *user_agent;
    uint64_t                        content_len;
}http_stream_t;

#define HTTP_STREAM_TASK_STACK          (6 * 1024)
#define HTTP_STREAM_TASK_CORE           (0)
#define HTTP_STREAM_TASK_PRIO           (4)
#define HTTP_STREAM_RINGBUFFER_SIZE     (20 * 1024)

esp_err_t http_open(char *uri);
void http_close(void);
int http_read(char *buffer, int len);
void http_stream_set_server_cert(const char *cert);
http_stream_t *get_http_handle(void);

#ifdef __cplusplus
}
#endif

#endif
