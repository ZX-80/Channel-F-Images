<div align="center">

# The Channel F Cartridge Image Format (.chf)
 
![badge](https://badgen.net/badge/version/v0.3/orange?style=flat-square)

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
| Hardware type           | 2              | The packets to expect. Described below                       |
| Reserved for future use | 2              |                                                              |
| Videocart version       | 2              | The game version major/minor (e.g. maze ver 3.2 = `$02 $03`) |
| Videocart name length   | 1              | Allows a length of 1 - 256                                   |
| Videocart name          | 1 - 256        |                                                              |
| Videocart author length | 1              | Allows a length of 1 - 256                                   |
| Videocart author        | 1 - 256        |                                                              |

**Designated Hardware type**

| Name                    | Hardware Type Value | Description                                                  |
| ----------------------- | -------------- | ------------------------------------------------------------ |
| Normal                  | \$0000         | Packets do not overlap                                       |


# Packet Overview

Packets serve as hardware descriptors, providing information on what hardware the game expects to be present. Some packets are special, as they provides the data that is (or would be) present in the on-board ROM / NVRAM.

# Packet Header

The packet header contains basic information on how the expected hardware is accessed.

<div align = "center">
  <img width="43%" src="https://user-images.githubusercontent.com/44975876/164077423-d5c0acfc-75c8-4dc4-b2a9-409ef7bb985e.png">
 
  *Placeholder*
</div>

**Packets**

| Name                    | Length (bytes) | Description                                                  |
| ----------------------- | -------------- | ------------------------------------------------------------ |
| Magic number            | 4              | `CHIP`. Used to detect a valid file.                         |
| Total packet length     | 2              | Header + Data(only some chip types)                          |
| Chip type               | 2              | Described below                                              |
| Starting address        | 2              | Where the memory region starts <br/> `$0000` for ports                              |
| Length                  | 2              | The size of the memory region  <br/> 1-256 for ports                                |
| Data                    | 1 - 63,488     | Only present for the some chip types. Technically supports up to 65,536 bytes but the first 2K of memory (\$0000 - \$07FF) should always be the BIOS, so the largest practical range is \$0800 - \$FFFF <br/> A list of port addresses|

**Designated Chip Types**

| Name          | Chip Type Value | Mapping | Comments                                                     | Typical Range/Port | Has data |
| ------------- | --------------- | ------- | ------------------------------------------------------------ | ------- | -- |
| ROM           | $0000           | Memory  | This memory range is Read-only                               | \$0800 - \$FFFF | Y |
| NV-RAM        | $0001           | Memory  | This memory range is non-volatile and read/write-able        | | Y |
| 8-bit SRAM    | $0002           | Memory  | This memory range is read/write-able  | \$2800 - \$3000 | |
| 1-bit SRAM    | $0003           | Port    | ports described [here](http://seanriddle.com/mazepat.asm)    | 0x18/0x19 | |
| LED           | $0004           | Memory  | Similar to ROM, but writing to this memory range toggles the LED  | \$3800 - \$4000 | Y |
| Programmable interrupt vector address    | $0005           | Port    | From the 3853 SMI IC              | 0x0C/0x0D | |
| Programmable timer    | $0006           | Port    | From the 3853 SMI IC                                 | 0x0E | |
| Interrupt control    | $0007           | Port    | From the 3853 SMI IC                                  | 0x0F | |

# Credits

Developed by e5frog (from AtariAge) and Jefferson A. (3DMAZE at AtariAge)
