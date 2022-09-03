#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Convert Channel F .bin files into .chf files"""

# TODO: multi-cart support
# TODO: extra string data support
# TODO: extra file data support

import argparse
import pathlib
import functools
import sys
import shlex

from math import ceil
from io import BufferedWriter
from typing import TypeAlias

PROGRAM_NAME = "bin2chf"
PROGRAM_VERSION = "1.0.0"
FORMAT_VERSION = "1.0"

uint8: TypeAlias = int
uint16: TypeAlias = int
uint32: TypeAlias = int
array_of_uint8: TypeAlias = memoryview

class ChipType:
    def __init__(self, designation_id: uint16, name: str, has_data: bool) -> None:
        self.designation_id = designation_id
        self.name = name.lower()
        self.has_data = has_data
        setattr(ChipType, name.upper(), designation_id)

class Packet:
    def __init__(self, chip_type: uint16, load_address: uint16, image_size: uint16, data: array_of_uint8 = None, bank_number: uint16 = 0) -> None:
        self.chip_type = chip_type
        self.bank_number = bank_number
        self.load_address = load_address
        self.image_size = image_size
        self.data = data

class HardwareType:
    def __init__(self, designation_id: uint16, name: str, packets: list[Packet], manual_memory_map: bool = False) -> None:
        self.designation_id = designation_id
        self.name = name
        self.packets = packets
        self.manual_memory_map = manual_memory_map

class ChfData:
    def __init__(self, hardware_type: uint16, version: str, title: str, extra: str, packets: list[Packet]) -> None:
        self.hardware_type = hardware_type
        self.version = version
        self.title = title
        self.extra = extra
        self.packets = packets

chip_type_list = [
    ChipType(0, "ROM", has_data=True),
    ChipType(1, "RAM", has_data=False),
    ChipType(2, "LED", has_data=True),
    ChipType(3, "NVRAM", has_data=True),
]

hardware_type_list = [
    HardwareType(0, "Videocart",
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0xF800)
        ]
    ),
    HardwareType(1, "Videocart 10/18 (with 2102 SRAM)",
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0xF800)
        ]
    ),
    HardwareType(2, "ROM + RAM (with 3853 SMI)",
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0x2000),
            Packet(chip_type=ChipType.RAM, load_address=0x2800, image_size=0x800),
            Packet(chip_type=ChipType.ROM, load_address=0x3000, image_size=0xC800),
        ]
    ),
    HardwareType(3, "SABA Videoplay 20",
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0x2000),
            Packet(chip_type=ChipType.RAM, load_address=0x2800, image_size=0x800),
            Packet(chip_type=ChipType.ROM, load_address=0x3000, image_size=0x800),
            Packet(chip_type=ChipType.LED, load_address=0x3800, image_size=0x800),
            Packet(chip_type=ChipType.ROM, load_address=0x4000, image_size=0xB800),
        ]
    ),
    HardwareType(4, "Multi-Cart", []),
    HardwareType(5, "Flashcart",
        [
            Packet(chip_type=ChipType.ROM, load_address=0x800, image_size=0x2000),
            Packet(chip_type=ChipType.RAM, load_address=0x2800, image_size=0x800),
            Packet(chip_type=ChipType.ROM, load_address=0x3000, image_size=0xC800),
        ],
        manual_memory_map = True
    ),
]

def read_config(config: pathlib.Path | None) -> list[str]:
    arguments = []
    if config is not None:
        with open(config, 'r') as config_fp:
            for line in config_fp:
                if not line.lstrip().startswith('#'):
                    arguments += shlex.split(line)
    return arguments

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
        "-w",
        "--hardwaretype",
        type=int,
        choices=list(range(len(hardware_type_list))),
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
            f"-{chip_type.name}",
            f"--{chip_type.name}",
            nargs=2,
            metavar=("START", "SIZE"),
            type=functools.partial(int, base=0),
            default=[],
            action="append",
            help=f"designates a range of memory as {chip_type.name.upper()}",
        )

    args = parser.parse_args()
    return parser.parse_args(read_config(args.config) + sys.argv[1:])

def validate_and_fetch_infile(infile: pathlib.Path) -> bytes:
    if infile.suffix != ".bin":
        sys.exit(f"[ERROR] File \"{infile}\" is not a .bin file")
    if not infile.is_file():
        sys.exit(f"[ERROR] File \"{infile}\" does not exist")
    try:
        with open(infile, mode='rb') as infile_fp:
            return infile_fp.read()
    except OSError:
        sys.exit(f"[ERROR] File \"{infile}\" could not be opened/read")

def validate_and_fetch_outfile(infile: pathlib.Path, outfile: pathlib.Path, yes_flag: bool, no_flag: bool) -> BufferedWriter:
    if outfile is None: # No output filename given
        outfile = pathlib.Path(infile.stem).with_suffix('.chf')
    if outfile.exists():
        response = 'y'
        if not yes_flag and not no_flag:
            response = input(f"File {outfile} already exists. Overwrite? [y/N] ")
        if no_flag or response != 'y':
            sys.exit(f"[ERROR] File \"{outfile}\" already exists")
        else:
            print(f"[WARNING] Overwriting \"{outfile}\"")    
    try:
        return open(outfile, "wb")
    except OSError:
        sys.exit(f"[ERROR] File \"{outfile}\" could not be opened/written")

def generate_arg_text(packet: Packet) -> str:
    command = f"--{chip_type_list[packet.chip_type].name}"
    start = hex(packet.load_address)
    size = hex(packet.image_size)
    return f"{command} {start} {size}"

def get_memory_map(args: argparse.Namespace) -> list[Packet]:
    packets = hardware_type_list[args.hardwaretype].packets
    
    # Memory map provided by user?
    if True in (bool(getattr(args, chip_type.name)) for chip_type in chip_type_list):
        if hardware_type_list[args.hardwaretype].manual_memory_map:
            # Build packets
            packets = []
            for chip_type in chip_type_list:
                for start, size in getattr(args, chip_type.name):
                    packets.append(Packet(chip_type.designation_id, start, size))

            # Validate packet ranges
            for packet in packets:
                if not 0x800 <= packet.load_address <= 0xffff:
                    sys.exit(f"[ERROR] Load address \"0x{packet.load_address:x}\" in \"{generate_arg_text(packet)}\" is invalid. Must be between 0x0800 & 0xffff")
                if not 1 <= packet.image_size <= 0x10000 - packet.load_address:
                    sys.exit(f"[ERROR] Size \"0x{packet.image_size:x}\" in \"{generate_arg_text(packet)}\" is invalid. Must be between 0x1 & 0x{0x10000 - packet.load_address:x}")

            # Check for overlapping packets
            packets = sorted(packets, key=lambda packet: packet.load_address)
            for prev_packet, packet in zip(packets[::2], packets[1::2]):
                if packet.load_address < prev_packet.load_address + prev_packet.image_size:
                    sys.exit(f"[ERROR] Packet \"{generate_arg_text(packet)}\" overlaps packet \"{generate_arg_text(prev_packet)}\"")
        else:
            print("[WARNING] Hardware type doesn't support manual memory map")
    return packets

def map_bin_to_packets(infile_data: bytes, packets: list[Packet]) -> list[Packet]:
    infile_data = memoryview(infile_data) # Avoid unnecessary copying
    valid_packets = []
    for packet in packets:
        if chip_type_list[packet.chip_type].has_data:
            index = packet.load_address - 0x800
            if index <= len(infile_data) - 1:
                packet.data = infile_data[index:index + packet.image_size]
                packet.image_size = len(packet.data)
                valid_packets.append(packet)
        else:
            valid_packets.append(packet)
    return valid_packets

def create_chf_file(fp: BufferedWriter, chf_data: ChfData, outfile_name: str) -> None:
    try:
        # Magic number: 16 bytes
        fp.write("CHANNEL F       ".encode('utf-8'))

        # File header length padded to be 16-byte aligned: 4 bytes
        file_header_length = 16 + 4 + 2 + 2 + 8 + 1 + len(chf_data.title)
        file_header_length = 16 * ceil(file_header_length / 16)
        fp.write(file_header_length.to_bytes(4, 'little'))

        # Format version: 2 bytes (Minor, Major)
        version_major, version_minor = map(int, chf_data.version.split('.'))
        fp.write(version_minor.to_bytes(1, 'little'))
        fp.write(version_major.to_bytes(1, 'little'))

        # Hardware type: 2 bytes
        fp.write(chf_data.hardware_type.to_bytes(2, 'little'))

        # Reserved: 8 bytes
        fp.write((0).to_bytes(8, 'little'))

        # Title length: 1 byte
        fp.write((len(chf_data.title) - 1).to_bytes(1, 'little')) # NOTE: is a simpler mapping better?

        # Title: 1 - 256 bytes
        fp.write(chf_data.title.encode('utf-8'))

        # Padding: 0 - 15 bytes
        fp.write((0).to_bytes(file_header_length - fp.tell(), 'little'))

        # Packets
        for packet in chf_data.packets:
            packet_header_address = fp.tell()
            fp.write("CHIP".encode('utf-8'))                            # Magic number: 4 bytes
            packet_length = 4 + 4 + 2 + 2 + 2 + 2 + packet.image_size   # Packet length padded to be 16-byte aligned: 4 bytes
            packet_length = 16 * ceil(packet_length / 16)
            fp.write(packet_length.to_bytes(4, 'little'))
            fp.write(packet.chip_type.to_bytes(2, 'little'))            # Chip type: 2 bytes
            fp.write(packet.bank_number.to_bytes(2, 'little'))          # Bank number: 2 bytes
            fp.write(packet.load_address.to_bytes(2, 'little'))         # Load address: 2 bytes
            fp.write(packet.image_size.to_bytes(2, 'little'))           # Data length: 2 bytes
            if chip_type_list[packet.chip_type].has_data:
                fp.write(packet.data)                                   # Data: 0 - 63,488 bytes
                fp.write((0).to_bytes(packet_length - fp.tell() + packet_header_address, 'little')) # Padding: 0 - 15 bytes

        fp.close()
    except OSError:
        sys.exit(f"[ERROR] File \"{outfile_name}\" could not be written")

if __name__ == "__main__":

    args = parse_args()
    infile_data = validate_and_fetch_infile(args.infile)
    outfile_fp = validate_and_fetch_outfile(args.infile, args.outfile, args.yes, args.no)

    if args.title is None:
        args.title = args.infile.stem
    if len(args.title) == 0:
        args.title = 'out'

    packets = get_memory_map(args)
    packets = map_bin_to_packets(infile_data, packets)
    chf_data = ChfData(args.hardwaretype, FORMAT_VERSION, args.title, None, packets)

    print(f"\nGenerating \"{outfile_fp.name}\":")
    print(f"  Title: {args.title}")
    print(f"  Hardware Type: {hardware_type_list[args.hardwaretype].name} [{args.hardwaretype}]")
    print("  Packets:")
    for packet in packets:
        print(f"    Type: {chip_type_list[packet.chip_type].name.upper()} [{packet.chip_type}]", end=', ')
        print(f"Start: 0x{packet.load_address:x}", end=', ')
        print(f"Size: 0x{packet.image_size:x} bytes")

    create_chf_file(outfile_fp, chf_data, args.outfile)
    print("\nOK")