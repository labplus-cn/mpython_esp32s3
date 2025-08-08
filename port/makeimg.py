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

arg_sdkconfig = "sdkconfig"
arg_bootloader_bin = "bootloader/bootloader.bin"
arg_partitions_bin = "partition_table/partition-table.bin"
arg_application_bin = "micropython.bin"
arg_output_bin = bin_name
arg_output_uf2= uf2_name
arg_font_bin = "../Noto_Sans_CJK_SC_Light16.bin"
arg_voice_data_bin = "../managed_components/espressif__esp-sr/esp-tts/esp_tts_chinese/esp_tts_voice_data_xiaoxin.dat"
arg_sr_bin = "../build/srmodels/srmodels.bin"

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

offset_voice_data = 0
max_size_voice_data = 0
offset_sr = 0
max_size_sr = 0

# Inspect the partition table to find offsets and maximum sizes.
for part in partition_table:
    if part.name == "nvs":
        max_size_partitions = part.offset - offset_partitions
    elif part.name == "font":
        offset_font = part.offset
        max_size_font = part.size
    elif part.type == gen_esp32part.APP_TYPE and offset_application == 0:
        offset_application = part.offset
        max_size_application = part.size
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
