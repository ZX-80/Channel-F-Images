#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Convert Channel F .bin files into .chf files"""

import configparser
import argparse
import pathlib
import functools

from collections import OrderedDict

HARDWARE_TYPE_LIMIT = 5

uint8 = int
uint16 = int
uint32 = int

class Packet:
    def __init__(self, chip_type: uint16, bank_number: uint16, load_address: uint16, image_size: uint16, data: list[uint8]) -> None:
        self.chip_type = chip_type
        self.bank_number = bank_number
        self.load_address = load_address
        self.memory_size = image_size
        self.data = data

class ChfData:
    def __init__(self, hardware_type: uint16, version: float, name: str, extra: str, packets: list[Packet]) -> None:
        self.hardware_type = hardware_type
        self.version = version
        self.name = name
        self.extra = extra
        self.packets = packets

class multidict(OrderedDict):
    """Allow duplicate section names in ini files."""
    _unique = 0
    def __setitem__(self, key, val):
        if isinstance(val, dict):
            self._unique += 1
            key += f"_{self._unique}"
        OrderedDict.__setitem__(self, key, val)

def read_template(template_filename: str):
    # Read ini file
    config = configparser.ConfigParser(defaults=None, dict_type=multidict, strict=False)
    with open(template_filename) as stream:
        config.read_string("[Header]\n" + stream.read())  # Basic support for sectionless data

    # Print sections and their keys for debugging
    for section in config.sections():
        print(section, config.items(section))

# conv filein.bin fileout.crt -hardwaretype 2 -title "GAMENAME"
# conv in.bin
#      -o out.chf
#      -hardwaretype 5
#      -name multi menu
#
#      -rom 0x0200 0x2000
#      -ram 0x2000 0x2800
#      -rom 0x2800 0x3000
#
#      -template example.ini

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert .bin files to .chf files.")

    parser.add_argument(
        "infile",
        type=pathlib.Path,
        help="the .bin file",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=pathlib.Path,
        help="the output file name",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=pathlib.Path,
        help="the template file name",
    )
    parser.add_argument(
        "-ht",
        "--hardwaretype",
        type=int,
        choices=list(range(HARDWARE_TYPE_LIMIT + 1)),
        default=2,
        help="described below",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="the game's title",
    )
    parser.add_argument(
        "-ram",
        "--ram",
        nargs=2,
        metavar=("START", "END"),
        type=functools.partial(int, base=0),
        action="append",
        help="designates a range of memory as RAM",
    )
    parser.add_argument(
        "-rom",
        "--rom",
        nargs=2,
        metavar=("START", "END"),
        type=functools.partial(int, base=0),
        action="append",
        help="designates a range of memory as ROM",
    )
    parser.add_argument(
        "-led",
        "--led",
        nargs=2,
        metavar=("START", "END"),
        type=functools.partial(int, base=0),
        action="append",
        help="designates a range of memory as LED",
    )
    parser.add_argument(
        "-nvram",
        "--nvram",
        "-fram",
        "--fram",
        nargs=2,
        metavar=("START", "END"),
        type=functools.partial(int, base=0),
        action="append",
        help="designates a range of memory as NVRAM",
    )

    args = parser.parse_args()
    print("\n", args)
