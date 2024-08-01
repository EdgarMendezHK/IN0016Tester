# Installation instructions

To install opencd fistly verify your system's date is correct, if it is not run these commands and wait for the system to reboot

```
sudo apt-get update
sudo apt-get upgrade
sudo timedatectl set-ntp True
sudo apt-get install -y ntp
sudo date -s yyyyMMdd hh:mm:ss
sudo reboot
```

# Install necesary dependencies

Run the next commands to update and upgrade your systems

```
sudo apt-get update
sudo apt-get upgrade
```

Then add install the next tools.

```
sudo apt-get install -y git autoconf libtool make pkg-config libusb-1.0-0 libusb-1.0-0-dev
```

Download the Openocd repository by using the next command. You can use the openocd.zip file if you don't want to download it.

```
git clone http://openocd.zylin.com/openocd
```

Once is downloaded run the next commands

```
cd openocd/
./bootstrap
./configure --enable-sysfsgpio --enable-bcm2835gpio
make
sudo make install
```

# Connecting the Raspberry pi 4 model B to the SAML21G

<div style="width:100%; text-align:center;">

|         Description         |        RASPBERRY PIN         | CORTEX DEBUG CONNECTOR PIN |
| :-------------------------: | :--------------------------: | :------------------------: |
|            3.3V             |            1, 17             |             1              |
|            SWDIO            |              24              |             2              |
|             GND             | 6, 9, 14, 20, 25, 30, 34, 39 |            3, 4            |
|           SWDCLK            |              23              |             4              |
| $$\overline{\text{RESET}}$$ |              12              |             10             |

</div>

_Note: the not listed cortex debug pins are not necesesary_

# Flashing the MCU

Localize the hex or elf file you want to flash to your microcontroller and copy the _openocd.cfg_ file, contained in this folder, to the another directory. Open the _openocd.cfg_ file and locate the last line. In there change the part that says _tp.hex_ for the name of your file. Do not forget to include its extension. Then, in the terminal, go to the file directory and run the next command.

```
sudo openocd -f interface/raspberrypi-native.cfg -f openocd.cfg
```
