<div align="center">

# The Channel F Cartridge Image Format (.chf)
 
![badge](https://badgen.net/badge/version/v0.2/orange?style=flat-square)

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

The file header contains basic information on the Videocart (name/author/version), as well as file format information that's necessary for interpretting the data, while allowing for future expansion. It's followed by a list of packets, described in the next section.

<div align = "center">
  <img width="43%" src="https://user-images.githubusercontent.com/44975876/164077423-d5c0acfc-75c8-4dc4-b2a9-409ef7bb985e.png">
 
  *Placeholder*
</div>

| Name                    | Length (bytes) | Description                                                  |
| ----------------------- | -------------- | ------------------------------------------------------------ |
| Magic number            | 8              | `CHANNELF`. Used to detect a valid file.                     |
| Header length           | 2              |                                                              |
| File Format Version     | 2              | `$00 $01` = Ver 01.00. Implementations should refuse to run games with major version numbers unknown by them. |
| File attributes         | 1              | The flashcart runs this file on boot if bit 0 is set `xxxxxxx1`. Other implementations should ignore this flag |
| Reserved for future use | 3              |                                                              |
| Videocart version       | 2              | The game version major/minor (e.g. maze ver 3.2 = `$02 $03`) |
| Videocart name length   | 1              | Allows a length of 1 - 256                                   |
| Videocart name          | 1 - 256        |                                                              |
| Videocart author length | 1              | Allows a length of 1 - 256                                   |
| Videocart author        | 1 - 256        |                                                              |

# Packet Overview

Packets serve as hardware descriptors, providing information on what hardware the game expects to be present. ROM packets are special, as they provides the data that is (or would be) present in the on-board ROM.
The flexibility provided can be abused by developers, and as such it's strongly encouraged to adhere to the following standards:

**Expected memory maps**
- 8-bit SRAM = \$2800 - \$3000
- LED = \$3800 - \$4000

**Expected port maps**
- 1-bit SRAM = 0x18/0x19
- programmable interrupt vector address = 0x0C/0x0D
- programmable timer = 0x0E
- interrupt control = 0x0F

# Packet Header

The packet header contains basic information on how the expected hardware is accessed.

<div align = "center">
  <img width="43%" src="https://user-images.githubusercontent.com/44975876/164077423-d5c0acfc-75c8-4dc4-b2a9-409ef7bb985e.png">
 
  *Placeholder*
</div>

| Name                    | Length (bytes) | Description                                                  |
| ----------------------- | -------------- | ------------------------------------------------------------ |
| Magic number            | 4              | `CHIP`. Used to detect a valid file.                         |
| Total packet length     | 2              | Header + Data(ROM only)                                      |
| Chip type               | 2              | Described below                                              |

| Name                    | Length (bytes) | Description                                                  |
| ----------------------- | -------------- | ------------------------------------------------------------ |
| Starting address        | 2              | Where the memory region starts                               |
| Range / Data length     | 2              | The size of the memory region                                |
| Data                    | 1 - 63,488     | Only present for the `ROM` chip type. Technically supports up to 65,536 bytes but the first 2K will always be shadowed by the BIOS |

| Name                    | Length (bytes) | Description                                                  |
| ----------------------- | -------------- | ------------------------------------------------------------ |
| Port addresses          | 1 - 256        | Only present for `Port-mapped` chip types. The port address for                               |

**Designated Chip Types**

| Name          | Chip Type Value | Mapping | Comments                                                     |
| ------------- | --------------- | ------- | ------------------------------------------------------------ |
| ROM           | $0000           | Memory  | This memory range is Read-only                               |
| NV-RAM        | $0001           | Memory  | This memory range is non-volatile and read/write-able        |
| 8-bit SRAM    | $0002           | Memory  | This memory range is read/write-able                         |
| 1-bit SRAM    | $0003           | Port    | ports described [here](http://seanriddle.com/mazepat.asm)    |
| LED           | $0004           | Memory  | Writing to this memory range toggles the LED                 |
| Programmable interrupt vector address    | $0007           | Port    | From the 3853 SMI IC              |
| Programmable timer    | $0008           | Port    | From the 3853 SMI IC                                 |
| Interrupt control    | $0009           | Port    | From the 3853 SMI IC                                  |
| Multimenu     | $0006           | Memory  | Provides 4 special registers used by the multimenu           |
| Bank Scheme 1 | $0005           | Memory  | A banking scheme providing 62KiB ROM/62KiB RAM. An 8-bit control Latch is present at $FFFF |

Are banking packets the only thing that would change packet interpretation? If so, perhaps they should be placed in the file header

# Credits

Developed by e5frog (from AtariAge) and Jefferson A. (3DMAZE at AtariAge)
