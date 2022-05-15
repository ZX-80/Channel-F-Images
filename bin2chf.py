#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Convert Channel F .bin files into .chf files"""

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

def generate_chf(chf_data: ChfData) -> None:
    # TODO: Use the provided class to generate a chf file
    print(f"Output {chf_data.name[16:]}.chf")

if __name__ == "__main__":
    # TODO: Load presets from files in presets folder
    print(" 0) Official (Videocarts 1-26)")
    print("      ROM 0x0800 - 0xFFFF                ;62K")
    print("      I/O Ports: SRAM")
    print(" 1) Schach (Videoplay 20)")
    print("      ROM 0x0800 - 0x2000                ;6K")
    print("     SRAM 0x2800 - 0x3000                ;2K")
    print("      LED 0x3800 - 0x4000                ;2K")
    print(" 2) Homebrew (Example)")
    print("      ROM 0x0800 - 0x2000                ;6K")
    print("     FRAM 0x2800 - 0x3000                ;2K")
    print("      ROM 0x3000 - 0xFFFF                ;50K")
    print("      I/O Ports: SRAM, Random, 3853 SMI")
    input("Which preset [0-2]: ")
    chf_data = None # TODO: Read preset file (ini?)
    
    if chf_data.name == None:
        chf_data.name = input("Enter Videocart name: ")

    generate_chf(chf_data)
