# Combine bootloader, partition table and application into a final binary.
from __future__ import print_function

import argparse
import datetime
import subprocess
import os, sys

sys.path.append(os.getenv("IDF_PATH") + "/components/partition_table")

import gen_esp32part

OFFSET_BOOTLOADER_DEFAULT = 0x1000
OFFSET_PARTITIONS_DEFAULT = 0x8000

def get_version_info_from_git(repo_path):
    # Python 2.6 doesn't have check_output, so check for that
    try:
        subprocess.check_output
    except AttributeError:
        return None

    # Note: git describe doesn't work if no tag is available
    try:
        git_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--dirty", "--always", "--match", "v[1-9].*"],
            cwd=repo_path,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).strip()
        # Turn git-describe's output into semver compatible (dot-separated
        # identifiers inside the prerelease field).
        git_tag = git_tag.split("-", 1)
        if len(git_tag) == 1:
            return git_tag[0]
        else:
            return git_tag[0] + "-" + git_tag[1].replace("-", ".")
    except (subprocess.CalledProcessError, OSError):
        return None

def get_hash_from_git(repo_path):
    # Python 2.6 doesn't have check_output, so check for that.
    try:
        subprocess.check_output
    except AttributeError:
        return None

    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_path,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).strip()
    except (subprocess.CalledProcessError, OSError):
        return None

def load_sdkconfig_value(filename, value, default):
    value = "CONFIG_" + value + "="
    with open(filename, "r") as f:
        for line in f:
            if line.startswith(value):
                return line.split("=", 1)[1]
    return default


def load_sdkconfig_hex_value(filename, value, default):
    value = load_sdkconfig_value(filename, value, None)
    if value is None:
        return default
    return int(value, 16)


def load_sdkconfig_str_value(filename, value, default):
    value = load_sdkconfig_value(filename, value, None)
    if value is None:
        return default
    return value.strip().strip('"')


def load_partition_table(filename):
    with open(filename, "rb") as f:
        return gen_esp32part.PartitionTable.from_binary(f.read())

def littlefs_bin_park(file_path, board_name, size):
    os.system("mkdir -p file_system")
    os.system(f"cp -r {file_path}/common/*  file_system/")
    os.system(f"cp -rf {file_path}/{board_name}/*  file_system/")
    os.system(f"./../mklittlefs -c file_system  -s {size} littlefs.bin")
            
# Extract command-line arguments.
# arg_sdkconfig = sys.argv[1]
# arg_bootloader_bin = sys.argv[2]
# arg_partitions_bin = sys.argv[3]
# arg_application_bin = sys.argv[4]
# arg_output_bin = sys.argv[5]
# arg_output_uf2 = sys.argv[6]
arg_board_name = sys.argv[1]
git_tag = get_version_info_from_git("../")
git_hash = get_hash_from_git("../")
build_date = datetime.date.today().strftime("%Y-%m-%d")
bin_name = "{}-{}-{}_{}.bin".format(arg_board_name, git_tag, git_hash, build_date)
uf2_name = "{}-{}-{}_{}.uf2".format(arg_board_name, git_tag, git_hash, build_date)
print(bin_name)

littlefs_bin_park(f"../file_system", arg_board_name, 0x200000)

arg_sdkconfig = "sdkconfig"
arg_bootloader_bin = "bootloader/bootloader.bin"
arg_partitions_bin = "partition_table/partition-table.bin"
arg_application_bin = "micropython.bin"
arg_vfs_bin = "littlefs.bin"
arg_output_bin = bin_name
arg_output_uf2= uf2_name
arg_font_bin = "../Noto_Sans_CJK_SC_Light16.bin"
arg_voice_data_bin = "../managed_components/espressif__esp-sr/esp-tts/esp_tts_chinese/esp_tts_voice_data_xiaoxin.dat"
arg_sr_bin = "srmodels/srmodels.bin"

# Load required sdkconfig values.
idf_target = load_sdkconfig_str_value(arg_sdkconfig, "IDF_TARGET", "").upper()
offset_bootloader = load_sdkconfig_hex_value(
    arg_sdkconfig, "BOOTLOADER_OFFSET_IN_FLASH", OFFSET_BOOTLOADER_DEFAULT
)
offset_partitions = load_sdkconfig_hex_value(
    arg_sdkconfig, "PARTITION_TABLE_OFFSET", OFFSET_PARTITIONS_DEFAULT
)

# Load the partition table.
partition_table = load_partition_table(arg_partitions_bin)

max_size_bootloader = offset_partitions - offset_bootloader
max_size_partitions = 0
offset_application = 0
max_size_application = 0
offset_font = 0
max_size_font = 0
offset_vfs = 0
max_size_vfs = 0
offset_voice_data = 0
max_size_voice_data = 0
offset_sr = 0
max_size_sr = 0

# partition table
# Name,       Type, SubType,   Offset,    Size,      Flags
# -------------------------------------------------------
# bootloader, app,  boot,      0x0,       0x7000,
# partitions, data, partition, 0x8000,    0
# nvs,        data, nvs,       0x9000,    0x6000,
# phy_init,   data, phy,       0xf000,    0x1000,
# factory,    app,  factory,   0x10000,   0x6E0000,
# vfs,        data, spiffs,    0x6F0000,  0x200000,
# voice_data, data, fat,       0x8F0000,  0x3CD000,
# sr_module,  data, spiffs,    0xCBD000,  0x31F000,
# fr,         data,   ,        0xFDC000,  0x20000
# user_nvs,   data, nvs,       0xFFC000,  0x4000,

# Inspect the partition table to find offsets and maximum sizes.
for part in partition_table:
    if part.name == "nvs":
        max_size_partitions = part.offset - offset_partitions # partition table size
    # elif part.name == "font":
    #     offset_font = part.offset
    #     max_size_font = part.size
    elif part.type == gen_esp32part.APP_TYPE and offset_application == 0:
        offset_application = part.offset
        max_size_application = part.size
    elif part.name == "vfs":
        offset_vfs = part.offset
        max_size_vfs = part.size
    elif part.name == "voice_data":
        offset_voice_data = part.offset
        max_size_voice_data = part.size
    elif part.name == "sr_module":
        offset_sr = part.offset
        max_size_sr = part.size

# Define the input files, their location and maximum size.
files_in = [
    ("bootloader", offset_bootloader, max_size_bootloader, arg_bootloader_bin),
    ("partitions", offset_partitions, max_size_partitions, arg_partitions_bin),
    ("application", offset_application, max_size_application, arg_application_bin),
    ("vfs", offset_vfs, max_size_vfs, arg_vfs_bin),
    ("voice_data", offset_voice_data, max_size_voice_data, arg_voice_data_bin),
    ("sr_module", offset_sr, max_size_sr, arg_sr_bin),
]
file_out = arg_output_bin

# Write output file with combined firmware.
cur_offset = offset_bootloader
with open(file_out, "wb") as fout:
    for name, offset, max_size, file_in in files_in:
        assert offset >= cur_offset
        fout.write(b"\xff" * (offset - cur_offset))
        cur_offset = offset
        with open(file_in, "rb") as fin:
            data = fin.read()
            fout.write(data)
            cur_offset += len(data)
            print(
                "%-12s@0x%06x % 8d  (% 8d remaining)"
                % (name, offset, len(data), max_size - len(data))
            )
            if len(data) > max_size:
                print(
                    "ERROR: %s overflows allocated space of %d bytes by %d bytes"
                    % (name, max_size, len(data) - max_size)
                )
                sys.exit(1)
    print("%-22s% 8d" % ("total", cur_offset))

# Generate .uf2 file if the SoC has native USB.
if idf_target in ("ESP32S2", "ESP32S3"):
    sys.path.append(os.path.join(os.path.dirname(__file__), "../micropython/tools"))
    import uf2conv

    families = uf2conv.load_families()
    uf2conv.appstartaddr = 0
    uf2conv.familyid = families[idf_target]
    with open(arg_application_bin, "rb") as fin, open(arg_output_uf2, "wb") as fout:
        fout.write(uf2conv.convert_to_uf2(fin.read()))
