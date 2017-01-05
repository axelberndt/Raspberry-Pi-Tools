# Raspberry Pi Tools

[![GPL v3](https://img.shields.io/badge/license-GNU%20General%20Public%20License%20v3.0-blue.svg)](https://github.com/axelberndt/Raspberry-Pi-Tools/blob/master/LICENSE)

Author: [Axel Berndt](https://github.com/axelberndt)<br>

This repository holds some useful code for the Raspberry Pi. It is tested and runs under Raspbian Jessie.

### Shutdown and Reboot Button
The file `ButtonPress.py` is a Python script that drives a shutdown and reboot button on GPIO pin 13 (GND on pin 14 or any other ground pin). Put it to a location on your Pi, say `/home/pi/myTools/` and add the following line to `/etc/rc.local` before `exit 0`.

`python /home/pi/myTools/ButtonPress.py&`

Than reboot and the script will run in background. Pressing the button for more than 2 seconds up to 5 seconds triggers a reboot. Pressing the button for more than 5 seconds triggers a shutdown. Pressing the button for less than 2 seconds does nothing.

### More to come
...