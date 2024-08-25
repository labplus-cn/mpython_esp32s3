
#include "audio/include/audio_file.h"
#include "py/stream.h"
#include "py/reader.h"
#include "extmod/vfs.h"


mp_obj_t audio_file_open(const char *filename, const char *mode)
{
    mp_obj_t arg[2];
    
    arg[0] = mp_obj_new_str(filename, strlen(filename));
    arg[1] = mp_obj_new_str(mode, strlen(mode));

    return mp_vfs_open(2, arg, (mp_map_t*)&mp_const_empty_map);
}

void audio_file_close(mp_obj_t File) {
    mp_stream_close(File);
}

int audio_file_read(mp_obj_t File, int *read_bytes, uint8_t *buf, uint32_t len) 
{
    int errcode;

    *read_bytes = mp_stream_rw(File, buf, len, &errcode, MP_STREAM_RW_READ | MP_STREAM_RW_ONCE);
    if (errcode != 0) {
        // TODO handle errors properly
        audio_file_close(File);
        return MP_READER_EOF;
    }
    if (*read_bytes < len) {
        audio_file_close(File);
        return MP_READER_EOF;
    }

    return 0;
}

int audio_file_write(mp_obj_t File, int *write_bytes, uint8_t *buf, uint32_t len)
{
    int errcode;

    *write_bytes = mp_stream_rw(File, buf, len, &errcode, MP_STREAM_RW_WRITE | MP_STREAM_RW_ONCE);
    if (errcode != 0) {
        // TODO handle errors properly
        audio_file_close(File);
        return MP_READER_EOF;
    }
    if (*write_bytes < len) {
        audio_file_close(File);
        return MP_READER_EOF;
    }

    return 0;    
}

void audio_chdir(const char *path)
{
    mp_obj_t p = mp_obj_new_str(path, strlen(path));
    mp_vfs_chdir(p);
}

int audio_file_seek(mp_obj_t File, long offset, int whence)
{
    int error;
    mp_off_t res = mp_stream_seek(File, offset, whence, &error);

    return error;
}

mp_off_t audio_file_tell(mp_obj_t File)
{
    int error;
    return mp_stream_seek(File, 0, SEEK_CUR, &error);    
}

