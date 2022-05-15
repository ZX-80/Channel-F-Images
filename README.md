<div align="center">

# The Channel F Cartridge Image Format (.chf)
 
![badge](https://badgen.net/badge/version/v0.5/orange?style=flat-square)

A file format to store games made for the Fairchild Channel F. Based on the [Cartridge Image](http://unusedino.de/ec64/technical/formats/crt.html) format from the CCS64 emulator.

  
<div align = "center">
  <img width="43%" src="https://user-images.githubusercontent.com/44975876/164077423-d5c0acfc-75c8-4dc4-b2a9-409ef7bb985e.png">
 
  *Placeholder*
</div>
  
[File Overview](#file-overview) •
[File Header](#file-header) •
[Packet Overview](#packet-overview) •
[Packet Header](#packet-header) •
[Credits](#credits)
  
</div>

# File Overview

The `.chf` file format was created to solve three major issues:
- Confusion caused by multiple undocumented `.bin` formats. Detecting different banking schemes can be difficult or sometimes even impossible
- Simplify feature detection for emulators/flashcarts (such as the expected presence of SRAM). Currently SRAM is provided if a Videocart attempts to write to memory. But this method can cause issues if a bug writes to the ROM area
- `.bin` files contain no information on the games title / author

To solve these issues, the `.chf` file format needs to provide the necessary information, while also being future proof in the event of new hardware/banking schemes. The [Cartridge Image](http://unusedino.de/ec64/technical/formats/crt.html) format from the CCS64 emulator was used as inspiration, as it had similar goals. Note this file format is little-endian, as that is what arduino/x86/RP2040 architectures all use.

# File Header

The file header contains basic information on the Videocart (name/hardware), as well as file format information that's necessary for interpretting the data, while allowing for future expansion. It's followed by a list of packets, described in the next section. The header is zero-padded to be 16-byte aligned.

<div align = "center">
  <img width="43%" src="https://user-images.githubusercontent.com/44975876/164077423-d5c0acfc-75c8-4dc4-b2a9-409ef7bb985e.png">
 
  *Placeholder*
</div>

| Name                    | Length (bytes) | Address | Description                                                  |
| ----------------------- | -------------- | ------- | ------------------------------------------------------------ |
| Cartridge signature     | 16             | \$0000  | `CHANNEL F`. Used to detect a valid file. Padded with spaces |
| File header length      | 4              | \$0010  |                                                              |
| Cartridge Version       | 2              | \$0014  | The version of the file format being used. Typically `$00 $01` = Ver 01.00. Implementations should refuse to run games with major version numbers unknown by them. |
| Cartridge Hardware type | 2              | \$0016  | The hardware that's used                                     |
| Reserved for future use | 8              | \$0018  |                                                              |
| Videocart name length   | 1              | \$0020  | Allows a length of 1 - 256                                   |
| Videocart name          | 1 - 256        | \$0021  |                                                              |

**Designated Hardware type**

| Name                    | Hardware Type Value | Memory-mapped | Port-mapped | Comments |
| ----------------------- | ------------------- | ------------- | ----------- | -------- |
| Videocarts              | \$0000              | ROM           |             | Used by all Videocarts except 10, 18, and 20 (SABA) |
| Videocarts 10 / 18      | \$0001              | ROM           | 2102 SRAM   |          |
| ROM+RAM (With 3853)     | \$0002              | ROM, RAM      | 3853 SMI    |          |
| SABA Videoplay 20       | \$0003              | ROM, RAM, LED | 3853 SMI    |          |
| Multi-Cart              | \$0004              | ROM, FRAM     | 3853 SMI    | Has selectable banking |
| Flashcart               | \$0005              | All           | All         |          |







# Packet Overview

Packets serve as hardware descriptors, providing information on what hardware the game expects to be present. Some packets are special, as they provides the data that is (or would be) present in the on-board ROM / NVRAM.

# Packet Header

The packet header contains basic information on how the expected hardware is accessed.

<div align = "center">
  <img width="43%" src="https://user-images.githubusercontent.com/44975876/164077423-d5c0acfc-75c8-4dc4-b2a9-409ef7bb985e.png">
 
  *Placeholder*
</div>

**Packets**

| Name                    | Length (bytes) | Memory-mapped Description                                    | Port-mapped Description |
| ----------------------- | -------------- | ------------------------------------------------------------ | ----------------------- |
| Signature               | 4              | `CHIP`. Used to detect a valid file.                         | Same as Memory-mapped   |
| Total packet length     | 4              | Header + Data(only some chip types)                          | Same as Memory-mapped   |
| Chip type               | 2              | Described below                                              | Same as Memory-mapped   |
| Bank number             | 2              | Used for banking. Always `$0000` for a normal hardware type  | Same as Memory-mapped   |
| Starting load address   | 2              | Where the memory region starts                               | Always `$0000`          |
| Image size in bytes     | 2              | The size of the memory region                                | The amount of ports used (1 - 256) |
| Data                    | 1 - 63,488     | Only present for the some chip types. Technically supports up to 65,536 bytes but the first 2K of memory (\$0000 - \$07FF) should always be the BIOS, so the largest practical range is \$0800 - \$FFFF | A list of port addresses |

**Designated Chip Types**

| Name          | Chip Type Value | Mapping | Comments                                                     | Typical Range/Port | Has data |
| ------------- | --------------- | ------- | ------------------------------------------------------------ | ------- | -- |
| ROM           | $0000           | Memory  | This memory range is Read-only                               | \$0800 - \$FFFF | Y |
| 8-bit RAM     | $0001           | Memory  | This memory range is read/write-able  | \$2800 - \$3000 | |
| LED           | $0002           | Memory  | Similar to ROM, but writing to this memory range toggles the LED  | \$3800 - \$4000 | Y |
| NVRAM         | $0003           | Memory  | This memory range is non-volatile and read/write-able        | | Y |
| 1-bit RAM     | $0004           | Port    | Ports described [here](http://seanriddle.com/mazepat.asm)    | 0x18/0x19 | |
| Programmable interrupt vector address    | $0005           | Port    | From the 3853 SMI IC              | 0x0C/0x0D | |
| Programmable timer    | $0006           | Port    | From the 3853 SMI IC                                 | 0x0E | |
| Interrupt control    | $0007           | Port    | From the 3853 SMI IC                                  | 0x0F | |

# Credits

Developed by e5frog (from AtariAge) and Jefferson A. (3DMAZE at AtariAge)
