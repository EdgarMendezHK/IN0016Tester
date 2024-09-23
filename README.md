# Installation instructions

## Update date

To install the necesary dependencies fistly verify your system's date is correct, if it is not run these commands and wait for the system to reboot

```
sudo apt-get update
sudo apt-get upgrade
sudo timedatectl set-ntp True
sudo apt-get install -y ntp
```

Now update the date by using the command below. Remeber to substitute the [yyyyMMdd hh:mm:ss] for the current date

```
sudo date -s [yyyyMMdd hh:mm:ss]
sudo apt full-upgrade
sudo reboot
```

## Install necesary dependencies for OpenOCD

Run the next commands to update and upgrade your systems

```
sudo apt-get update
sudo apt-get upgrade

```

Then add install the next tools.

```
sudo apt-get install -y git autoconf libtool make pkg-config libusb-1.0-0 libusb-1.0-0-dev
```

## Installing OpenOCD

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

## Installing .Net8

The dotnet-install scripts are used for automation and non-admin installs of the SDK and Runtime. You can download the script from https://dot.net/v1/dotnet-install.sh. You can download the script with wget:

```
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
```

Before running this script, make sure you grant permission for this script to run as an executable:

```
chmod +x ./dotnet-install.sh
```

Set the following two environment variables in your shell profile. open the bashrc file and add the next lines.

```
nano ~/.bashrc
```

- DOTNET_ROOT

  This cariable is set to the folder .NET was installed to, such as _$HOME/.dotnet_:

  ```
  export DOTNET_ROOT=$HOME/.dotnet
  ```

- PATH
  This variable should include both the _DOTNET_ROOT_ folder and the _DOTNET_ROOT/tools_ folder:
  ```
  export PATH=$PATH:$DOTNET_ROOT:$DOTNET_ROOT/tools
  ```

Save and close the file and apply the next command to apply the changes.

```
source ~/.bashrc
```

# Using OpenOCD

## Connecting the Raspberry pi 4 model B to the POP314 board's programming port

The following connections are necesary to flash the microcontroller.

<div style="width:100%; text-align:center;">

|         Description         |        RASPBERRY PIN         | CORTEX DEBUG CONNECTOR PIN |
| :-------------------------: | :--------------------------: | :------------------------: |
|            3.3V             |            1, 17             |             1              |
|            SWDIO            |              24              |             2              |
|             GND             | 6, 9, 14, 20, 25, 30, 34, 39 |            3, 4            |
|           SWDCLK            |              23              |             4              |
| $$\overline{\text{RESET}}$$ |              12              |             10             |

</div>

_Note: The not listed cortex debug pins are not necesesary_

## Flashing the MCU

Localize the hex or elf file you want to flash to your microcontroller and copy the _openocd.cfg_ file, contained in this folder, to the another directory. Open the _openocd.cfg_ file and locate the last line. In there change the part that says _tp.hex_ for the name of your file. Do not forget to include its extension. Then, in the terminal, go to the file directory and run the next command.

```
sudo openocd -f interface/raspberrypi-native.cfg -f openocd.cfg
```

# Install python libraries

To install the required python libraries you need to locate at the project's path and run create and activate a virtual environment. Once is done you'll need to install the required libreries. To do so use the next command

```
python3 -m venv [environment name]
source [environment name]/bin/activate
pip install pyserial minimalmodbus
```

# Enabling serial and SPI communication

## Enable serial port and SPI

To enable serial communication run the next command in a terminal.

```
sudo raspi-config
```

Then select _interface options -> Serial port_. Then it will ask you if you'd like a login shell to be accessible over serial, choose **No**. En then choose **Yes** to enable the serial port hardware.

Once is done go back to _interface options -> Serial port_ and now enable SPI.

## Configure UART

- Edit the config.txt file to configure the UART settings. Open the file with:

```
sudo nano /boot/firmware/config.txt
```

- Add the following lines at the end to enable the UART

```
#disabling bloothoot
dtoverlay=disable-bt

#Enabling uart ports
enable_uart=1
dtoverlay=uart0
dtoverlay=uart2

```

- Disable the Bluetooth service

```
sudo systemctl disable hciuart
```

- Increase the amount of UART ports. Use the next command to open xmdline.txt file

```
sudo nano /boot/firmware/cmdline.txt
```

- Add the next line at the end. Add a whitespace after the last word and then add _8250.nr_uarts=3_. For example

```
console=tty1 root=PARTUUID=d3dfd584-02 rootfstype=ext4 fsck.repair=yes rootwait quiet splash plymouth.ignore-serial-consoles cfg80211.ieee80211_regdom=GB 8250.nr_uarts=3
```

- Save and exit the editor by pressing **CTRL+X**, then **Y**, and **Enter**.

-Set the GPIO alternative functions to gpio 0 and 1, so that, they can be used for serial communications

```
raspi-gpio set 0,1 a4
```

- Rebuild the device tree and reboot the raspberry pi to apply the changes.

```
sudo apt install --reinstall raspberrypi-kernel
sudo reboot
```

# Connecting the Raspberry pi 4 model B to the Nextion NX3224T024_011

The following connections are necesary to communicate with the Nextion display.

<div style="width:100%; text-align:center;">

| Raspberry pi pin | Nextion display cable color |
| ---------------- | --------------------------- |
| 4 (5V power)     | Red                         |
| 6 (Ground)       | Black                       |
| 8 (TXD)          | Yellow                      |
| 10 (RXD)         | Blue                        |

</div>

# Connecting the Raspberry pi 4 model B to POP314 board's serial communication port

The following connections are necesary to communicate with the board's serial communication port.

<div style="width:100%; text-align:center;">

| Raspberry pi pin | Communication port cable |
| ---------------- | ------------------------ |
| 2 (5V power)     | Red                      |
| 25 (Ground)      | Black                    |
| 27 (TXD)         | Green                    |
| 28 (RXD)         | White                    |

</div>
