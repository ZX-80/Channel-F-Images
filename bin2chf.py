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
        self.image_size = image_size
        self.data = data
        
class ChfData:
    def __init__(self, hardware_type: uint16, version: float, name: str, author: str, packets: list[Packet]) -> None:
        self.hardware_type = hardware_type
        self.version = version
        self.name = name
        self.author = author
        self.packets = packets

def generate_chf(chf_data: ChfData) -> None:
    # TODO: Use the provided class to generate a chf file
    chf_data.name = input("Enter Videocart name: ")
    chf_data.author = input("Enter Videocart author: ")
    chf_data.version = float(input("Enter Videocart version: "))
    print("Output game.bin\ndone")

if __name__ == "__main__":
    positive_responses = ['Y', 'YES', '']
    if input("Use presets [Y/n]: ").upper() in positive_responses:
        # TODO: Load presets from files in presets folder
        print(" 0) Normal (Videocarts 1-26)")
        print("      ROM 0x0800 - 0xFFFF                ;up to 64K")
        print(" 1) 2102 SRAM (Videocarts 10 / 18)")
        print("      ROM 0x0800 - 0x1400                ;up to 3K")
        print("     SRAM 0x2800 - 0x3000                ;2K")
        print(" 2) Chess (Saba Chess)")
        print("      ROM 0x0800 - 0x2000                ;6K")
        print("     SRAM 0x2800 - 0x3000                ;2K")
        print("      LED 0x3800 - 0x4000                ;2K")
        print(" 3) SRAM (Homebrew only)")
        print("      ROM 0x0800 - 0x2800                ;up to 8K")
        print("     SRAM 0x2800 - 0x3000                ;2K")
        print("      ROM 0x3000 - 0xFFFF                ;up to 52K")
        print(" 4) FRAM (Homebrew only)")
        print("      ROM 0x0800 - 0x2800                ;up to 8K")
        print("     FRAM 0x2800 - 0x3000                ;2K")
        print("      ROM 0x3000 - 0xFFFF                ;up to 52K")
        input("Which preset [0-4]: ")
        generate_chf()
    else:
        input("Enter preset file address: ")
        # TODO: Read preset file (ini?)
        generate_chf()
