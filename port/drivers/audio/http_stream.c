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

#include <sys/unistd.h>
#include <sys/stat.h>
#include <string.h>
#include <strings.h>
#include <errno.h>

#include "freertos/FreeRTOS.h"
#include "freertos/ringbuf.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

#include "esp_log.h"
// #include "line_reader.h"
// #include "gzip_miniz.h"
#if (ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(4, 3, 0))
#include "aes/esp_aes.h"
#elif (ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(4, 1, 0))
#if CONFIG_IDF_TARGET_ESP32
#include "esp32/aes.h"
#elif CONFIG_IDF_TARGET_ESP32S2
#include "esp32s2/aes.h"
#endif
#else
#include "hwcrypto/aes.h"
#endif
#include "esp_audio_simple_dec.h"
#include "http_stream.h"

static const char *TAG = "HTTP_STREAM";
#define HTTP_STREAM_BUFFER_SIZE (2048)
#define HTTP_MAX_CONNECT_TIMES  (5)

http_stream_t *http = NULL;

// `errno` is not thread safe in multiple HTTP-clients,
// so it is necessary to save the errno number of HTTP clients to avoid reading and writing exceptions of HTTP-clients caused by errno exceptions
int __attribute__((weak)) esp_http_client_get_errno(esp_http_client_handle_t client)
{
    (void) client;
    ESP_LOGE(TAG, "Not found right %s.\r\nPlease enter ADF-PATH with \"cd $ADF_PATH/idf_patches\" and apply the ADF patch with \"git apply $ADF_PATH/idf_patches/idf_%.4s_esp_http_client.patch\" first\r\n", __func__, IDF_VER);
    return errno;
}

static esp_audio_simple_dec_type_t get_audio_type(const char *content_type)
{
    if (strcasecmp(content_type, "mp3") == 0 ||
        strcasecmp(content_type, "audio/mp3") == 0 ||
        strcasecmp(content_type, "audio/mpeg") == 0 ||
        strcasecmp(content_type, "binary/octet-stream") == 0 ||
        strcasecmp(content_type, "application/octet-stream") == 0) {
        return ESP_AUDIO_SIMPLE_DEC_TYPE_MP3;
    }
    if (strcasecmp(content_type, "audio/aac") == 0 ||
        strcasecmp(content_type, "audio/x-aac") == 0 ||
        strcasecmp(content_type, "audio/mp4") == 0 ||
        strcasecmp(content_type, "audio/aacp") == 0 ||
        strcasecmp(content_type, "video/MP2T") == 0 ||
        strcasecmp(content_type, "audio/vnd.dlna.adts") == 0) {
        return ESP_AUDIO_SIMPLE_DEC_TYPE_AAC;
    }
    if (strcasecmp(content_type, "audio/wav") == 0 ||
        strcasecmp(content_type, "audio/x-wav") == 0) {
        return ESP_AUDIO_SIMPLE_DEC_TYPE_WAV;
    }
    // if (strcasecmp(content_type, "audio/opus") == 0) {
    //     return ESP_CODEC_TYPE_OPUS;
    // }
    // if (strcasecmp(content_type, "application/vnd.apple.mpegurl") == 0 ||
    //     strcasecmp(content_type, "vnd.apple.mpegURL") == 0) {
    //     return ESP_AUDIO_TYPE_M3U8;
    // }
    // if (strncasecmp(content_type, "audio/x-scpls", strlen("audio/x-scpls")) == 0) {
    //     return ESP_AUDIO_TYPE_PLS;
    // }
    return ESP_AUDIO_SIMPLE_DEC_TYPE_NONE;
}

// static int _gzip_read_data(uint8_t *data, int size, void *ctx)
// {
//     http_stream_t *http = (http_stream_t *) ctx;
//     return esp_http_client_read(http->client, (char *)data, size);
// }

static esp_err_t _http_event_handle(esp_http_client_event_t *evt)
{
    switch(evt->event_id) {
        case HTTP_EVENT_ERROR:
            ESP_LOGD(TAG, "HTTP_EVENT_ERROR");
            break;
        case HTTP_EVENT_ON_CONNECTED:
            ESP_LOGD(TAG, "HTTP_EVENT_ON_CONNECTED");
            break;
        case HTTP_EVENT_HEADER_SENT:
            ESP_LOGD(TAG, "HTTP_EVENT_HEADER_SENT");
            break;
        case HTTP_EVENT_ON_HEADER:
            if (strcasecmp(evt->header_key, "Content-Type") == 0) {
                ESP_LOGE(TAG, "%s = %s", evt->header_key, evt->header_value);
                //配置解码类型;
                http->stream_type = get_audio_type(evt->header_value);
            }
            // else if (strcasecmp(evt->header_key, "Content-Encoding") == 0) {
            //     http->gzip_encoding = true;
            //     if (strcasecmp(evt->header_value, "gzip") == 0) {
            //         gzip_miniz_cfg_t cfg = {
            //             .chunk_size = 1024,
            //             .ctx = http,
            //             .read_cb = _gzip_read_data,
            //         };
            //         http->gzip = gzip_miniz_init(&cfg);
            //     }
            //     if (http->gzip == NULL) {
            //         ESP_LOGE(TAG, "Content-Encoding %s not supported", evt->header_value);
            //         return ESP_FAIL;
            //     }
            // }
            // else if (strcasecmp(evt->header_key, "Content-Range") == 0) {
            //     if (http->request_range_size) {
            //         char* end_pos = strchr(evt->header_value, '-');
            //         http->is_last_range = true;
            //         if (end_pos) {
            //             end_pos++;
            //             int64_t range_end = atoll(end_pos);
            //             if (range_end == http->request_range_end) {
            //                 http->is_last_range = false;
            //             }
            //         }
            //     }
            // }
            break;
        case HTTP_EVENT_ON_DATA:
            ESP_LOGD(TAG, "HTTP_EVENT_ON_DATA, len=%d", evt->data_len);
            // http->data_len = evt->data_len;
            if (!esp_http_client_is_chunked_response(evt->client)) {
                // Write out data
                // printf("%.*s", evt->data_len, (char*)evt->data);
            }

            break;
        case HTTP_EVENT_ON_FINISH:
            ESP_LOGD(TAG, "HTTP_EVENT_ON_FINISH");
            break;
        case HTTP_EVENT_DISCONNECTED:
            ESP_LOGD(TAG, "HTTP_EVENT_DISCONNECTED");
            break;
        default: break;
    }
    return ESP_OK;
}

/*
static void _prepare_range(http_stream_t *http, int64_t pos)
{
    if (http->request_range_size > 0 || pos != 0) {
        char range_header[64] = {0};
        if (http->request_range_size == 0) {
            snprintf(range_header, sizeof(range_header), "bytes=%lld-", pos);
        } else {
            int64_t end_pos = pos + http->request_range_size - 1;
            if (pos < 0 && end_pos > 0) {
                end_pos = 0;
            }
            snprintf(range_header, sizeof(range_header), "bytes=%lld-%lld", pos, end_pos);
            http->request_range_end = end_pos;
        }
        esp_http_client_set_header(http->client, "Range", range_header);
    } else {
        esp_http_client_delete_header(http->client, "Range");
    }
}  */

esp_err_t http_open(const char *uri)
{
    if (uri == NULL) {
        ESP_LOGE(TAG, "Error open connection, uri = NULL");
        return ESP_FAIL;
    }
    ESP_LOGE(TAG, "URI=%s", uri);

    http = calloc(1, sizeof(http_stream_t));
    if(!http){  return ESP_ERR_NO_MEM; }

//     if (config->crt_bundle_attach) {
// #if  (ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(4, 3, 0))
//     #if CONFIG_MBEDTLS_CERTIFICATE_BUNDLE
//         http->crt_bundle_attach = config->crt_bundle_attach;
//     #else
//         ESP_LOGW(TAG, "Please enbale CONFIG_MBEDTLS_CERTIFICATE_BUNDLE configuration in menuconfig");
//     #endif
// #else
//         ESP_LOGW(TAG, "Just support MBEDTLS_CERTIFICATE_BUNDLE on esp-idf to v4.3 or later");
// #endif // ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(4, 3, 0)
//     }

    // http->request_range_size = config->request_range_size;
    // if (config->request_size) {
    //     cfg.buffer_len = config->request_size;
    // }

    http->_errno = 0;
    if (http->client == NULL) {
        esp_http_client_config_t http_cfg = {
            .url = uri,
            .event_handler = _http_event_handle,
            .timeout_ms = 30 * 1000,
            .buffer_size = HTTP_STREAM_BUFFER_SIZE,
            .method = HTTP_METHOD_GET,
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(4, 1, 0)
            .buffer_size_tx = 1024,
#endif
            .cert_pem = NULL,
#if  (ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(4, 3, 0)) && defined CONFIG_MBEDTLS_CERTIFICATE_BUNDLE
            .crt_bundle_attach = NULL,
#endif //  (ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(4, 3, 0)) && defined CONFIG_MBEDTLS_CERTIFICATE_BUNDLE
            .user_agent = NULL,
        };
        http->client = esp_http_client_init(&http_cfg);
        if(!http->client)
            return ESP_ERR_NO_MEM;
    } else {
        esp_http_client_set_url(http->client, uri);
    }

    // esp_http_client_close(http->client);
    // _prepare_range(http, info->byte_pos);
    if(esp_http_client_open(http->client, 0) == ESP_OK){
        http->is_open = true;
    }else{
        esp_http_client_cleanup(http->client);
        return ESP_ERR_INVALID_STATE;
    }

    http->content_len = esp_http_client_fetch_headers(http->client);
    ESP_LOGE(TAG, "content len: %ld", (long int)http->content_len);

    return ESP_OK;
}

void http_close(void)
{
    if(http){
        ESP_LOGD(TAG, "_http_close");
        if (http->is_open)
            http->is_open = false;

        // if (http->gzip) {
        //     gzip_miniz_deinit(http->gzip);
        //     http->gzip = NULL;
        // }
        if (http->client) {
            esp_http_client_close(http->client);
            esp_http_client_cleanup(http->client);
            http->client = NULL;
        }
        free(http);
    }
}

int http_read(char *buffer, int len)
{
    int rlen = 0;

    if(http){
        if (http->gzip_encoding == false) {
            rlen = esp_http_client_read(http->client, buffer, len);
        }else{
        // use gzip to uncompress data
            // rlen = gzip_miniz_read(http->gzip, (uint8_t*) buffer, len);
        }

        if (rlen <= 0) {
            http->_errno = esp_http_client_get_errno(http->client);
            // ESP_LOGW(TAG, "No more data,errno:%d, total_bytes:%llu, rlen = %d", http->_errno, info.byte_pos, rlen);
            // if (http->_errno != 0) {  // Error occuered, reset connection
            //     ESP_LOGW(TAG, "Got %d errno(%s)", http->_errno, strerror(http->_errno));
            //     return http->_errno;
            // }
        }
        // ESP_LOGD(TAG, "req lengh=%d, read=%d, pos=%d/%d", len, rlen, (int)info.byte_pos, (int)info.total_bytes);
    }
    return rlen;
}

void http_stream_set_server_cert(const char *cert)
{
    if(http){
        http->cert_pem = cert;
    }
}

http_stream_t *get_http_handle(void)
{
    return http;
}