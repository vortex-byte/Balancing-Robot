[![id](https://img.shields.io/badge/BAHASA-INDONESIA-red.svg)](https://github.com/vortex-byte/Balancing-Robot/blob/main/README.md)

# Balancing Robot

A self-balancing robot using Arduino Mega and Raspberry Pi 3, with a GUI for communication and monitoring.
## Features

- GUI for monitoring and tuning
- Ultrasonic sensors for obstacle avoidance
- LCD screen for notifications
- Auto-pilot and remote modes (coming soon!)


## Getting Started

### What You’ll Need

- [Putty](https://www.putty.org/) - For SSH login to the Raspberry Pi
- Your favorite code editor
- Python >= 3.9
- Pip >= 24.x
- An SD card reader - For editing the Raspberry Pi firmware

### Updating the Raspberry Pi Wi-Fi Configuration

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

2. Use CMD/Terminal to check if your PC is on the same network as the Raspberry Pi
```
ping raspberrypi -t
```
3. If the GUI server isn’t installed yet, clone this repository:
```
git clone https://github.com/vortex-byte/Balancing-Robot.git
cd GUI/server
```

4. Install the required libraries
```
pip install requirements
```

5. Start the Python GUI server program
```
python server.py
```

6. Note the server’s public IP address (e.g., 192.168.x.x)


### Installing the GUI Client

The GUI client runs on your PC

1. Clone this repository
```
git clone https://github.com/vortex-byte/Balancing-Robot.git
cd GUI/client
```

2. Install the required libraries:
```
pip install requirements
```

3. Start the Python client program:
```
python client.py
```

4. Enter the server’s IP address from earlier

Want to customize the client GUI? Check out this tutorial:  [Tkinter Designer](https://www.youtube.com/watch?v=Qd-jJjduWeQ)
## Let’s Connect!

- [@vortex-byte](mailto:mzimam.ath@gmail.com)

