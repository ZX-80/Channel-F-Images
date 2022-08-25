#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Convert Channel F .bin files into .chf files"""

# TODO: support a config file for command arguments

import argparse
import pathlib
import functools
import sys

from io import BufferedWriter
from typing_extensions import TypeAlias

PROGRAM_NAME = "bin2chf"
PROGRAM_VERSION = "1.0"

uint8: TypeAlias = int
uint16: TypeAlias = int
uint32: TypeAlias = int



class ChipType:
    def __init__(self, designation_id: uint16, string: str) -> None:
        self.designation_id = designation_id
        self.string = string
        setattr(ChipType, string, designation_id)

class Packet:
    def __init__(self, chip_type: uint16, load_address: uint16, image_size: uint16, data: list[uint8] = None, bank_number: uint16 = 0) -> None:
        self.chip_type = chip_type
        self.bank_number = bank_number
        self.load_address = load_address
        self.image_size = image_size
        self.data = data

class HardwareType:
    def __init__(self, designation_id: uint16, packets: list[Packet], manual_memory_map: bool = False) -> None:
        self.designation_id = designation_id # 2
        self.packets = packets # packets layout
        self.manual_memory_map = manual_memory_map # supports manual memory maps

class ChfData:
    def __init__(self, hardware_type: uint16, version: float, title: str, extra: str, packets: list[Packet]) -> None:
        self.hardware_type = hardware_type
        self.version = version
        self.title = title
        self.extra = extra
        self.packets = packets

chip_type_list = [
    ChipType(0, "ROM"),
    ChipType(1, "RAM"),
    ChipType(2, "LED"),
    ChipType(3, "NVRAM"),
]

hardware_type_list = [
    HardwareType(
        0,
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0xF800)
        ]
    ),
    HardwareType(
        1,
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0xF800)
        ]
    ),
    HardwareType(
        2,
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0x2000),
            Packet(chip_type=ChipType.RAM, load_address=0x2800, image_size=0x800),
            Packet(chip_type=ChipType.ROM, load_address=0x3000, image_size=0xC800),
        ]
    ),
    HardwareType(
        3,
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0x2000),
            Packet(chip_type=ChipType.RAM, load_address=0x2800, image_size=0x800),
            Packet(chip_type=ChipType.ROM, load_address=0x3000, image_size=0x800),
            Packet(chip_type=ChipType.LED, load_address=0x3800, image_size=0x800),
            Packet(chip_type=ChipType.ROM, load_address=0x4000, image_size=0xB800),
        ]
    ),
    HardwareType(4, []),
    HardwareType(
        5,
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0x2000),
            Packet(chip_type=ChipType.RAM, load_address=0x2800, image_size=0x800),
            Packet(chip_type=ChipType.ROM, load_address=0x3000, image_size=0xC800),
        ],
        True
    ),
]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description="Convert .bin files to .chf files.")

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
        "-c",
        "--config",
        type=pathlib.Path,
        help="the template file name",
    )
    parser.add_argument(
        "-ht",
        "--hardwaretype",
        type=int,
        choices=list(range(len(hardware_type_list) + 1)),
        default=2,
        help="described below",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        help="the game's title",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="overwrite output files without asking",
    )
    parser.add_argument(
        "-n",
        "--no",
        action="store_true",
        help="do not overwrite output files, and exit immediately if a specified output file already exists",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {PROGRAM_VERSION}"
    )

    for chip_type in chip_type_list:
        parser.add_argument(
            f"-{chip_type.string.lower()}",
            f"--{chip_type.string.lower()}",
            nargs=2,
            metavar=("START", "SIZE"),
            type=functools.partial(int, base=0),
            default=[],
            action="append",
            help=f"designates a range of memory as {chip_type.string}",
        )

    return parser.parse_args()

def validate_and_fetch_infile() -> bytes:
    if args.infile.suffix != ".bin":
        sys.exit(f"[ERROR] \"{args.infile}\" is not a .bin file")
    if not args.infile.is_file():
        sys.exit(f"[ERROR] \"{args.infile}\" does not exist")
    try:
        with open(args.infile, mode='rb') as infile_fp:
            return infile_fp.read()
    except OSError:
        sys.exit(f"[ERROR] File \"{args.infile}\" could not be opened/read")

def validate_and_fetch_outfile() -> BufferedWriter:
    if args.outfile is None: # No output filename given
        args.outfile = pathlib.Path(args.infile.stem).with_suffix('.chf')
    if args.outfile.exists(): # Outfile already exists
        response = 'y'
        if not args.yes and not args.no: # Prompt user
            response = input(f"File {args.outfile} already exists. Overwrite? [y/N] ")
        if args.no or response != 'y':
            sys.exit(f"[ERROR] \"{args.outfile}\" already exists")
        else:
            print(f"[WARNING] Overwriting \"{args.outfile}\"")    
    try:
        return open(args.outfile, "wb")
    except OSError:
        sys.exit(f"[ERROR] File \"{args.outfile}\" could not be opened/written")

def get_memory_map() -> list[Packet]:
    packets = hardware_type_list[args.hardwaretype].packets
    if sum(len(getattr(args, chip_type.string.lower())) for chip_type in chip_type_list) != 0: # Memory map provided by user?
        if hardware_type_list[args.hardwaretype].manual_memory_map:
            packets = []
            chip_type = 0
            for provided_ranges in (getattr(args, chip_type.string.lower()) for chip_type in chip_type_list):
                for start, size in provided_ranges:
                    packets.append(Packet(chip_type=chip_type, load_address=start, image_size=size))
                chip_type += 1

            if len(packets) > 0:
                # Validate packet ranges
                for packet in packets:
                    
                    arg_text = "--" + chip_type_list[packet.chip_type].string.lower() + " " + hex(packet.load_address) + " " + hex(packet.image_size)
                    if not 0x800 <= packet.load_address <= 0xffff:
                        sys.exit(f"[ERROR] Load address \"{hex(packet.load_address)}\" in \"{arg_text}\" is invalid. Must be between 0x0800 & 0xffff")
                    if not 1 <= packet.image_size <= 0xf800:
                        sys.exit(f"[ERROR] Size \"{hex(packet.image_size)}\" in \"{arg_text}\" is invalid. Must be between 0x0001 & {hex(0x10000 - packet.load_address)}")
                    if packet.load_address + packet.image_size > 0x10000:
                        sys.exit(f"[ERROR] \"{arg_text}\" ranges from {hex(packet.load_address)} to {hex(packet.load_address + packet.image_size - 1)} which exceeds 0xFFFF")

                # Check for overlapping packets      
                packets = sorted(packets, key=lambda packet: packet.load_address)
                prev_packet = packets[0]
                for packet in packets[1:]:
                    if packet.load_address < prev_packet.load_address + prev_packet.image_size:
                        prev_arg_text = "--" + chip_type_list[prev_packet.chip_type].string.lower() + " " + hex(prev_packet.load_address) + " " + hex(prev_packet.image_size)
                        arg_text = "--" + chip_type_list[packet.chip_type].string.lower() + " " + hex(packet.load_address) + " " + hex(packet.image_size)
                        sys.exit(f"[ERROR] packet {arg_text} overlaps packet {prev_arg_text}")
                    prev_packet = packet
        else:
            print("[WARNING] hardware type doesn't support manual memory map")
    return packets

if __name__ == "__main__":

    args = parse_args()
    print(f"\nDEBUG 1: {args}\n")

    # Handle infile
    infile_data = validate_and_fetch_infile()

    # Handle outfile
    outfile_fp = validate_and_fetch_outfile()

    # Handle title
    if args.title is None:
        args.title = args.infile.stem

    # Handle memory map
    packets = get_memory_map()

    # TODO: map data in .bin file to packets in packets list,
    # deleting/resizing packets as necessary
    
    print("\nPackets:")
    for packet in packets:
        print("   Type: ", packet.chip_type)
        print("   Start:", hex(packet.load_address))
        print("   Size: ", hex(packet.image_size), "\n")

    print(f"\nDEBUG 2: {args}\n")
    
    # TODO: produce .chf file from ChfData object    
        