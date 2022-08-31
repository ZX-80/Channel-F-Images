<div align="center">

# BIN to CHF
 
![badge](https://badgen.net/badge/version/v1.0.0/orange?style=flat-square)
![badge](https://badgen.net/badge/platform/win-32%20|%20win-64/green?style=flat-square)
![badge](https://badgen.net/badge/python/3.10+/blue?style=flat-square)

A python script designed to convert Channel F ROMs stored as .bin files to .chf files

  
<p align = "center">
  <img width="450" src="https://user-images.githubusercontent.com/44975876/187595406-73d8b515-12de-43e9-a79c-ed306623d400.png">
</p>

  
[General Usage](#general-usage) •
[Options](#options) •
[Configuration](#configuration) •
[Installation](#installation) •
[Updating](#updating)
  
</div>

## General Usage

The most basic use requires an input file, and preferably a title

```
C:\Windows\System32> bin2chf game.bin -t "3D MONSTER MAZE"

Generating "game.chf":
  Title: 3D MONSTER MAZE
  Hardware Type: ROM + RAM (with 3853 SMI) [2]
  Packets:
    Type: ROM [0], Start: 0x800, Size: 0x2000 bytes
    Type: RAM [1], Start: 0x2800, Size: 0x800 bytes

OK

C:\Windows\System32>
```

To create a custom memory map, use hardware type 5 (Flashcart) with the rom/ram/led/nvram arguments

```
C:\Windows\System32> bin2chf game.bin -t "3D MONSTER MAZE" -w 5 -rom 0x800 439 -ram 0xf000 0xff

Generating "game.chf":
  Title: 3D MONSTER MAZE
  Hardware Type: Flashcart [5]
  Packets:
    Type: ROM [0], Start: 0x800, Size: 0x1b7 bytes
    Type: RAM [1], Start: 0xf000, Size: 0xff bytes

OK

C:\Windows\System32>
```

## Options

```
-h, --help                               Show this help message and exit.
-o FILENAME, --outfile FILENAME          The output file name. (defaults to input filename)
-c FILENAME, --config FILENAME           The config file name. Described below.
-w TYPE, --hardwaretype TYPE             A number for the type of hardware to use.
                                         0 = Videocart
                                         1 = Videocart 10/18 (with 2102 SRAM)
                                         2 = ROM + RAM (with 3853 SMI)        (default)
                                         3 = SABA Videoplay 20
                                         4 = Multi-Cart
                                         5 = Flashcart
-t TITLE, --title TITLE                  The game's title. (defaults to input filename)
-y, --yes                                Overwrite output files without asking.
-n, --no                                 Do not overwrite output files, and exit immediately 
                                         if a specified output file already exists.
-v, --version                            Show program's version number and exit.
-rom START SIZE, --rom START SIZE        Designates a range of memory as ROM.
-ram START SIZE, --ram START SIZE        Designates a range of memory as RAM.
-led START SIZE, --led START SIZE        Designates a range of memory as LED.
-nvram START SIZE, --nvram START SIZE    Designates a range of memory as NVRAM.
```

## Configuration

**NOT YET IMPLEMENTED**

For convenience, a config file can be created to store terminal arguments. The arguments will be run as if they were entered on the command line. It can then be used like so:

`bin2chf game.bin --config example.txt`

Where example.txt is:

```
# Lines starting with # are comments

# Set the title and filename
--title "Oils Well"
--output oilswell.chf

# Set the hardware type to "Flashcart"
--hardwaretype 5

# Define a simple memory map with 60K of ROM & 2K of RAM
--rom 0x0800 0x2000
--ram 0x2800 2048
--rom 0x3000 0xC800
```

## Installation
This script was developed and tested on Windows, but likely works on other operating systems. The python version installed was python 3.10.0. Installation for newer version of python 3 should look similar.

**1. Install Python 3**

  - Download and install the latest version of Python3 from [Python Downloads Page](https://www.python.org/downloads/), making sure to follow the below instructions during installation.
     - In the optional features menu, select **"pip"**, **"tcl/tk"**, **"py launcher"**, and **"for all users"**.
     - In the advanced  options menu: select **"Create shortcuts"**, **"Add Python to environment variables"**, and **"Precompile standard library"**
   
     <p align = "center">
       <img width="70%" alt="image" src="https://user-images.githubusercontent.com/44975876/157488978-aa671158-1161-4202-9f90-55f1f25e1698.png">
     </p>
     
   - Check that Python 3 is properly installed
     - First open a command prompt (cmd.exe), then run `python`. If it doesn't produce an error and looks similar to the example, then Python 3 is installed. Type `quit()` to exit Python 3
     - In the same command prompt, run `pip -V` (capital V), or `python -m pip -V`.  If it doesn't produce an error and looks similar to the example, then Pip is installed

     <p align = "center">
       <img width="70%" alt="image" src="https://user-images.githubusercontent.com/44975876/157490924-d4f9e061-73d1-48bf-b928-3e22a103edd6.png">
     </p>

**2. Install the script**

  - Create a folder where you'd like the script to live
  - Download the script files from github by clicking **Code** and then **Download Zip**
  - Unzip the files in `Videocart-Image-Format-main.zip` into the folder you created
  - The only file that matters is `bin2chf.py`. The others are just helpful text files that can be deleted if you want

  ## Updating

  To update, simply delete the old script, and reinstall as shown above