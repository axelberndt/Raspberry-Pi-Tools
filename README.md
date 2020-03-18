# Raspberry Pi Tools

[![GPL v3](https://img.shields.io/badge/license-GNU%20General%20Public%20License%20v3.0-blue.svg)](https://github.com/axelberndt/Raspberry-Pi-Tools/blob/master/LICENSE)

Author: [Axel Berndt](https://github.com/axelberndt)<br>

This repository holds some useful code for the Raspberry Pi. It is tested and runs under Raspbian Jessie.

### Shutdown and Reboot Button
The file `ShutdownRebootButton.py` is a Python script that drives a shutdown and reboot button on GPIO pin 13 (GND on pin 14 or any other ground pin). Put it to a location on your Pi, say `/home/pi/myTools/`, and add the following line to `/etc/rc.local` before `exit 0`.

`python /home/pi/myTools/ShutdownRebootButton.py&`

Than reboot and the script will run in background. Pressing the button for more than 2 seconds up to 5 seconds triggers a reboot. Pressing the button for more than 5 seconds triggers a shutdown. Pressing the button for less than 2 seconds does nothing.

### Rotary Encoder
The file `RotaryEncoder.py` is a Python script that reads a rotary encoder connected to GPIO pin 16 and 18, GND on pin 14 or any other ground pin. Some encoders have inverse direction; in this case swap the values of the global variables `GPIOpinA` and `GPIOpinB` accordingly. This solution is quite robust and works without debouncing. Hence, no artificial delays are introduced. However, very quick rotation may lead to missing state changes and, hence, a few wrong results can occur. Furthermore, most users will not need the locking and can safely remove everything on that (wherever variable `lock` occurs). To run the script, put it to a location on your Pi, say `/home/pi/myTools/`, and write the following line in the terminal.

`python /home/pi/myTools/RotaryEncoder.py&`

This will execute the script in background and produce terminal output whenever the encoder rotates. To stop the script write

`ps -elf | grep python`

at the terminal and find the process id (PID) of the script. Then execute the following line and insert the right PID.

`kill -9 PID`

### Volume Control via Rotary Encoder
The Python script `VolumeRotaryControl.py` reads a rotary encoder connected to GPIO pin 16 and 18, GND on pin 14 or any other ground pin, and controls the ALSA Master volume. It is based on the script `RotaryEncoder.py`, so have a look at the above section and the respective code to find further details. Put the script file to a location on your Pi, say `/home/pi/myTools/`, and add the following line to `/etc/rc.local` before `exit 0`.

`python /home/pi/myTools/VolumeRotaryControl.py&`

This script requires the `python-alsaaudio` package to be installed! If it is not, execute the following terminal command.

`sudo apt-get install python-alsaaudio`

After the next reboot the script will run in background and allow you to control the Master volume via a rotary encoder. To access a different ALSA channel or have access to the separate output lines (e.g., left and right from a stereo channel) have a closer look into the code and find the corresponding comments and code lines in method `rotaryInterruptA()`. Further documentation of the `alsaaudio` package can be found [here](http://larsimmisch.github.io/pyalsaaudio/libalsaaudio.html#mixer-objects).

### Combined Shutdown/Reboot and Volume Control

The Python script `ShutdownRebootVolumeControl.py` is a combination of `ShutdownRebootButton.py` and `VolumeRotaryControl.py`. It is handy for those who use a rotary switch. To use it place it on your Pi, e.g. in `/home/pi/myTools/`, and add the line

`python /home/pi/myTools/ShutdownRebootVolumeControl.py&`

to `/etc/rc.local` before `exit 0`.
