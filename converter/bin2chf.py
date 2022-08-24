#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Convert Channel F .bin files into .chf files"""

# TODO: support a config file for command arguments

import argparse
import pathlib
import functools
import sys

HARDWARE_TYPE_LIMIT = 5
PROGRAM_NAME = "bin2chf"
PROGRAM_VERSION = "1.0"

uint8 = int
uint16 = int
uint32 = int

class Packet:
    ROM = 0
    RAM = 1
    LED = 2
    NVRAM = 3
    def __init__(self, chip_type: uint16, load_address: uint16, image_size: uint16, data: list[uint8] = None, bank_number: uint16 = 0) -> None:
        self.chip_type = chip_type
        self.bank_number = bank_number
        self.load_address = load_address
        self.image_size = image_size
        self.data = data

class ChfData:
    def __init__(self, hardware_type: uint16, version: float, title: str, extra: str, packets: list[Packet]) -> None:
        self.hardware_type = hardware_type
        self.version = version
        self.title = title
        self.extra = extra
        self.packets = packets

# conv filein.bin fileout.crt -hardwaretype 2 -title "GAMENAME"
# conv in.bin
#      -o out.chf
#      -hardwaretype 5
#      -title "Oils Well"
#
#      -rom 0x0800 0x2000
#      -ram 0x2800 0x800
#      -rom 0x3000 0xC800
#
#      -config example.ini
#
#      -y
#      -n
#      -v

if __name__ == "__main__":

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
        choices=list(range(HARDWARE_TYPE_LIMIT + 1)),
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
        "-ram",
        "--ram",
        nargs=2,
        metavar=("START", "END"),
        type=functools.partial(int, base=0),
        default=[],
        action="append",
        help="designates a range of memory as RAM",
    )
    parser.add_argument(
        "-rom",
        "--rom",
        nargs=2,
        metavar=("START", "END"),
        type=functools.partial(int, base=0),
        default=[],
        action="append",
        help="designates a range of memory as ROM",
    )
    parser.add_argument(
        "-led",
        "--led",
        nargs=2,
        metavar=("START", "END"),
        type=functools.partial(int, base=0),
        default=[],
        action="append",
        help="designates a range of memory as LED",
    )
    parser.add_argument(
        "-nvram",
        "--nvram",
        nargs=2,
        metavar=("START", "END"),
        type=functools.partial(int, base=0),
        default=[],
        action="append",
        help="designates a range of memory as NVRAM",
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

    args = parser.parse_args()
    print(f"\nDEBUG 1: {args}\n")

    # Handle infile
    if args.infile.suffix != ".bin":
        sys.exit(f"[ERROR] \"{args.infile}\" is not a .bin file")
    if not args.infile.is_file():
        sys.exit(f"[ERROR] \"{args.infile}\" does not exist")
    try:
        with open(args.infile, mode='rb') as infile_fp:
            infile_data = infile_fp.read()
    except OSError:
        sys.exit(f"[ERROR] File \"{args.infile}\" could not be opened/read")

    # Handle outfile
    if args.outfile is None: # No output filename given
        args.outfile = pathlib.Path(args.infile.stem).with_suffix('.chf')
    if args.outfile.exists(): # outfile already exists
        if not args.yes and not args.no: # prompt user
            response = input(f"File {args.outfile} already exists. Overwrite? [y/N] ")
            if response != 'y':
                sys.exit(f"[ERROR] \"{args.outfile}\" already exists")
            else:
                print(f"[WARNING] Overwriting \"{args.outfile}\"")
        elif args.no: # exit if file exists
            sys.exit(f"[ERROR] \"{args.outfile}\" already exists")
        elif args.yes: # continue if file exists
            print(f"[WARNING] Overwriting \"{args.outfile}\"")
    try:
        outfile_fp = open(args.outfile, "wb")
    except OSError:
        sys.exit(f"[ERROR] File \"{args.outfile}\" could not be opened/read")

    # Handle title
    if args.title is None:
        args.title = args.infile.stem

    # Handle memory map
    memory_map_provided = len(args.rom + args.ram + args.led + args.nvram) != 0
    if memory_map_provided and args.hardwaretype != 5:
        print("[WARNING] hardware type doesn't support manual memory map")

    if args.hardwaretype in [0, 1]:
        packets = [
            Packet(chip_type=Packet.ROM, load_address=0x800, image_size=0xF800)
        ]
    elif args.hardwaretype == 2 or (args.hardwaretype == 5 and not memory_map_provided):
        packets = [
            Packet(chip_type=Packet.ROM, load_address=0x800, image_size=0x2000),
            Packet(chip_type=Packet.RAM, load_address=0x2800, image_size=0x800),
            Packet(chip_type=Packet.ROM, load_address=0x3000, image_size=0xC800),
        ]
    elif args.hardwaretype == 3:
        packets = [
            Packet(chip_type=Packet.ROM, load_address=0x800, image_size=0x2000),
            Packet(chip_type=Packet.RAM, load_address=0x2800, image_size=0x800),
            Packet(chip_type=Packet.ROM, load_address=0x3000, image_size=0x800),
            Packet(chip_type=Packet.LED, load_address=0x3800, image_size=0x800),
            Packet(chip_type=Packet.ROM, load_address=0x4000, image_size=0xB800),
        ]
    elif args.hardwaretype == 5:
        packets = []
        chip_type = 0
        for provided_ranges in [args.rom, args.ram, args.led, args.nvram]:
            for start, size in provided_ranges:
                packets.append(Packet(chip_type=chip_type, load_address=start, image_size=size))
            chip_type += 1

        if len(packets) > 0:
            # Validate packet ranges
            for packet in packets:
                arg_text = "--" + {0:"rom", 1:"ram", 2:"led", 3:"nvram"}[packet.chip_type] + " " + hex(packet.load_address) + " " + hex(packet.image_size)
                if not 0x800 <= packet.load_address <= 0xffff:
                    sys.exit(f"[ERROR] Load address \"{hex(packet.load_address)}\" in \"{arg_text}\" is invalid. Must be between 0x0800 & 0xffff")
                if not 1 <= packet.image_size <= 0xf800:
                    sys.exit(f"[ERROR] Size \"{hex(packet.image_size)}\" in \"{arg_text}\" is invalid. Must be between 0x0001 & 0xf800")
                if packet.load_address + packet.image_size > 0x10000:
                    print(arg_text)
                    sys.exit(f"[ERROR] \"{arg_text}\" ranges from {hex(packet.load_address)} to {hex(packet.load_address + packet.image_size - 1)} which exceeds 0xFFFF")

            # Check for overlapping packets      
            packets = sorted(packets, key=lambda packet: packet.load_address)
            prev_packet = packets[0]
            for packet in packets[1:]:
                if packet.load_address < prev_packet.load_address + prev_packet.image_size:
                    prev_arg_text = "--" + {0:"rom", 1:"ram", 2:"led", 3:"nvram"}[prev_packet.chip_type] + " " + hex(prev_packet.load_address) + " " + hex(prev_packet.image_size)
                    arg_text = "--" + {0:"rom", 1:"ram", 2:"led", 3:"nvram"}[packet.chip_type] + " " + hex(packet.load_address) + " " + hex(packet.image_size)
                    sys.exit(f"[ERROR] packet {arg_text} overlaps packet {prev_arg_text}")
                prev_packet = packet

    # TODO: map data in .bin file to packets in packets list,
    # deleting/resizing packets as necessary
    
    print("\nPackets:")
    for packet in packets:
        print("   Type: ", packet.chip_type)
        print("   Start:", hex(packet.load_address))
        print("   Size: ", hex(packet.image_size), "\n")

    print(f"\nDEBUG 2: {args}\n")
    
    # TODO: produce .chf file from ChfData object    
        