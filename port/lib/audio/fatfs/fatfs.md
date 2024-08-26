# fatfs

## 关于fatfs
    - ff.c中包含所有的FAT文件及目录api，就用程序调用这些api实现对文件系统的读写。

    - ff.c中调用以下底层api实现具体的磁盘硬件操作，如spiflash sd card。

        ```c
        DSTATUS disk_initialize (BYTE pdrv);
        DSTATUS disk_status (BYTE pdrv);
        DRESULT disk_read (BYTE pdrv, BYTE* buff, LBA_t sector, UINT count);
        DRESULT disk_write (BYTE pdrv, const BYTE* buff, LBA_t sector, UINT count);
        DRESULT disk_ioctl (BYTE pdrv, BYTE cmd, void* buff);
        ```

        应用程序驱动必须实现以上接口。用户系统可能会有多个磁盘，通过pdrv区分，因此应用程序必须实pdrv和相应磁盘IO驱动实现对应。

## 本fatfs文件系统实现

    ff.h中通过以下define，接口diskio.c的磁盘IO api

    ```c
    #define disk_initialize     ffs_disk_initialize
    #define disk_status         ffs_disk_status
    #define disk_read           ffs_disk_read
    #define disk_write          ffs_disk_write
    #define disk_ioctl          ffs_disk_ioctl
    ```

    diskio.c中实现了这些接口。

    diskio中多磁盘驱动实现：

    1. 定义一结构（结构成员为diskio驱动aip指针）指针数组，数组各成员保存pdrv对应磁盘驱动api组成的结构的指针

        ```c
        static ffs_diskio_impl_t * s_impls[FF_VOLUMES] = { NULL };
        ```

        ```c
        typedef struct {
            DSTATUS (*init) (unsigned char pdrv);    /*!< disk initialization function */
            DSTATUS (*status) (unsigned char pdrv);  /*!< disk status check function */
            DRESULT (*read) (unsigned char pdrv, unsigned char* buff, uint32_t sector, unsigned count);  /*!< sector read function */
            DRESULT (*write) (unsigned char pdrv, const unsigned char* buff, uint32_t sector, unsigned count);   /*!< sector write function */
            DRESULT (*ioctl) (unsigned char pdrv, unsigned char cmd, void* buff); /*!< function to get info about disk and do some misc operations */
        } ffs_diskio_impl_t;
        ```

    2. diskio_rawflash.c/h为spiflash的读写驱动，把FAT的扇区转为spiflash地址读写，实现了以下api。

        ```c
        ffs_raw_initialize()
        ffs_raw_status()
        ffs_raw_read()
        ffs_raw_write()
        ffs_raw_ioctl()
        ```

        有几个需要关联的地方：

        1. 如果有多个spiflash，通过以下数组保存要操作的分区：

            ```c
            const esp_partition_t* ffs_raw_handles[FF_VOLUMES]; //FF_VOLUMES最多支持分区数。
            ```

        2. pdrv对应ffs_raw_handles[]数据索引。

        3. 需要把相关api通过注册，填充到s_impls[pdrv]对应结构指针指向的结构中。最终能被faffs的api调用。


## 应用程序使用fatfs

    1. 初始化

        vfs_fat_spiflash.c中

        ```c
        esp_err_t esp_vfs_fat_spiflash_mount(const char* base_path, const char* partition_label)
        {
            ...
            1、获取spiflash分区
            const esp_partition_t *data_partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
                    ESP_PARTITION_SUBTYPE_DATA_FAT, partition_label);
            ...

            // connect driver to FATFS
            2、通过判断s_impls[]对应成员是否为空，获取对应数组索引，做为pdrv值。
            BYTE pdrv = 0xFF;
            if (ffs_diskio_get_drive(&pdrv) != ESP_OK) {
                ...
            }

            3、此函数实现：
                a) 把欲操作spifash分区跟pdrv关联起来，分区保存在pdrv为索引的数组ffs_raw_handles[pdrv] = part_handle中。
                b)调用ffs_diskio_register(pdrv, &raw_impl)把底层api填充到以pdrv为索引的raw_impl[]结构的函数指针中去。
                这样，fatfs只需通过pdrv参数，就可实现对对应磁盘上的文件系统实实io操作。
            result = ffs_diskio_register_raw_partition(pdrv, data_partition); //把pdrv跟文件系统分区关联起来。
            if (result != ESP_OK) {
                ...
            }

            4、挂载磁盘，实际就是把一个磁盘对应FATFS结构跟保存到FATFS的static FATFS* FatFs[pdrv]中，实现pdrv跟
               对应磁盘的FATFS结构关联。完成此操作后，应用程序调用fread()等函数时，只需传入各磁盘FATFS结构就可以实
               现对本磁盘的操作。
            fs = ffs_memalloc(sizeof(FATFS)); //为一个fatfs结构分配内存
    
            char drv[3] = {(char)('0' + pdrv), ':', 0};
            FRESULT fresult = fs_mount(fs, drv, 1);
            if (fresult != FR_OK) {
                ESP_LOGW(TAG, "fs_mount failed (%d)", fresult);
                result = ESP_FAIL;
                goto fail;
            }
            return ESP_OK;

        fail:
            esp_vfs_fat_unregister_path(base_path);
            ffs_diskio_unregister(pdrv);
            return result;
        }
        ```

        ```c
        FRESULT fs_mount (
            FATFS* fs,			/* Pointer to the filesystem object to be registered (NULL:unmount)*/
            const TCHAR* path,	/* Logical drive number to be mounted/unmounted */
            BYTE opt			/* Mount option: 0=Do not mount (delayed mount), 1=Mount immediately */
        )
        {
            FATFS *cfs;
            int vol;
            FRESULT res;
            const TCHAR *rp = path;

            /* 获取逻辑扇区号，从字串 "0：" 得到数值0*/
            vol = get_ldnumber(&rp);
                ...
            // fatfs内部维护一个FATFS结构指针数组，static FATFS* FatFs[FF_VOLUMES]; pdrv跟数组索引关联。
            // 各磁盘有各自FATFS结构，保存各自FATFS相关信息，通过跟pdrv对应的vol做索引，把各磁盘的FATFS结构地址
            // 保存在FatFs[vol]中，反过来，这样对应关系建立后，后续的fread()等操作，只要传入各磁盘的FATFS结构地址，
            // 即可反查出pdrv。实现对指定磁盘的操作。
            FatFs[vol] = fs;					/* Register new fs object */

            if (opt == 0) return FR_OK;			/* Do not mount now, it will be mounted later */

            res = mount_volume(&path, &fs, 0);	/* Force mounted the volume */
        }
```
