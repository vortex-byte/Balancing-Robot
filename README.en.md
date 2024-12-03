[![id](https://img.shields.io/badge/BAHASA-INDONESIA-red.svg)](https://github.com/vortex-byte/Balancing-Robot/blob/main/README.md)

# Balancing Robot

A self-balancing robot using Arduino Mega and Raspberry Pi 3, with a GUI for communication and monitoring.
## Features

- GUI for monitoring and tuning
- Ultrasonic sensors for obstacle avoidance
- LCD screen for notifications
- Auto and remote control modes


## Getting Started

### What You’ll Need

- [Putty](https://www.putty.org/) - For SSH login to the Raspberry Pi
- [Git](https://git-scm.com/downloads)
- Your favorite code editor
- Python >= 3.9
- Pip >= 24.x
- An SD card reader - For editing the Raspberry Pi firmware

### Raspberry Pi OS Configuration

<details>
	<summary><b>Install Raspberry Pi OS</b></summary>
    1. Insert SD Card to SD Card reader, then insert to your PC
    2. Download, install and open [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
    3. Match the Raspberry Pi Type, OS, and SD Card storage
    
    ![Type](https://cdn.mos.cms.futurecdn.net/cQHK7tWkKGRENVuMkR5Gkg-1200-80.png.webp)
    
    4. Open Edit Settings
    
    ![Type](https://cdn.mos.cms.futurecdn.net/u3EMmPAXT4AsU9gUeLHoC-1200-80.png.webp)
    
    5. In General tab, fill hostname, username, password, SSID, Wi-Fi Password. To make the SSH login process easier, use this configuration:
    ``` 
    Hostname: raspberrypi
    Username: pi
    Password: pi
    SSID: Raspi
    Wi-Fi Password: 12345678
    TImezone: Asia/Jakarta
    Keyboard: US
     ```
    
    ![Type](https://cdn.mos.cms.futurecdn.net/Et4hHahUd3dN3nufsLKqFN-1200-80.png.webp)
    
    6. In Services tab, check ``` Enable SSH ``` and select ``` Use password auth ``` then click Save and Yes till the installation process is complete
    
    ![Type](https://cdn.mos.cms.futurecdn.net/FQPA4pWp9qswNM8feDE4ye-1200-80.png.webp)
</details>

<details
    <summary><b>Updating the Raspberry Pi Wi-Fi Configuration</b></summary>
</details>

The Raspberry Pi needs Wi-Fi to communicate with the GUI client. Here’s how to update the Wi-Fi settings:

- Remove the SD card from the Raspberry Pi
- Connect the SD card to your PC using an SD card reader
- Open the boot partition and locate the ```wpa_supplicant.conf``` file
- Find the following text and update the SSID and password with your Wi-Fi credentials
```
network={
    ssid="WIFI SSID"
    psk="WIFI PASS"
}
```
- Save the file, eject the SD card, and insert it back into the Raspberry Pi

## Installation

### Installing the GUI Server

The GUI server runs on the Raspberry Pi.

1. Power on the robot, ensuring the Raspberry Pi is up and connected to Wi-Fi

2. Use CMD/Terminal to check if your PC is on the same network as the Raspberry Pi. Ping the Raspberry Pi hostname:
```
ping raspberrypi -t
```

Wait until get feedback from Raspberry Pi

3. Open Putty then in the Hostname fill with the hostname you already created. Hostname ```raspberrypi```, Port ```22```, Connection Type ```SSH```. then Open

4. If the GUI server isn’t installed yet, clone this repository:
```
git clone --single-branch --branch server https://github.com/vortex-byte/Balancing-Robot.git
```
```
cd Balancing-Robot
```

5. Install the required libraries
```
pip install -r requirements.txt
```

6. Start the Python GUI server program
```
python server.py
```

7. Note the server’s public IP address (e.g., 192.168.x.x)


### Installing the GUI Client

The GUI client runs on your PC

1. Clone this repository
```
git clone --single-branch --branch client https://github.com/vortex-byte/Balancing-Robot.git
```
```
cd Balancing-Robot
```

2. Install the required libraries:
```
pip install -r requirements.txt
```

3. Start the Python client program:
```
python client.py
```

4. Enter the server’s IP address from earlier

Want to customize the client GUI? Check out this tutorial:  [Tkinter Designer](https://www.youtube.com/watch?v=Qd-jJjduWeQ)

## Hardware Schematic

![Schematic](https://raw.githubusercontent.com/vortex-byte/Balancing-Robot/refs/heads/main/skematik.jpg)

## Let’s Connect!

- [@vortex-byte](mailto:mzimam.ath@gmail.com)

