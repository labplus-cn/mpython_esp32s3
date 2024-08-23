#ifndef __PLAYER_
#define __PLAYER_


typedef void* player_handle;
#define FATFS_PATH_LENGTH_MAX 256

void *player_create(int ringbuf_size, unsigned int core_num);
void player_play(void *handle, const char *path);
void player_pause(void *handle);
void player_continue(void *handle);
void player_exit(void *handle);
int player_get_state(void *handle);
void player_increase_vol(void *handle);
void player_decrease_vol(void *handle);

#endif
