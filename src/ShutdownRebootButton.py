#!/usr/bin/env python3.5

# This Python script drives a shutdown/reboot button on GPIO pin 13, GND on pin 14.
# Put it to a location on your Pi, say /home/pi/myTools/ and add the following line
# to /etc/rc.local before exit 0:
# python /home/pi/myTools/ShutdownRebootButton.py&

# author: Axel Berndt

from time import sleep, time
from subprocess import call
from RPi import GPIO

GPIOpin = 27    # Button is on GPIO channel 27 / pin 13 of 40way connector with GND on pin 14
pressTime = float('Inf')  # this is used to keep track of the time passing between button press and release, when waiting for button press/falling it has the positive inf value to prevent unintended shutdowns

def init():
    GPIO.setmode(GPIO.BCM)                                  # set the GPIO naming/numbering convention to BCM
    GPIO.setup(GPIOpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # setup the channel as input with a 50K Ohm pull up. A push button will ground the pin, creating a falling edge.
    GPIO.add_event_detect(GPIOpin, GPIO.BOTH, callback=buttonPress)#, bouncetime=100) # define interrupt, add the bouncetime if it works better with your button

# the callback function when button is pressed/released
def buttonPress(GPIOpin):
    global pressTime                            # get access to the global time variable
    if not GPIO.input(GPIOpin):                 # if button falling event
        if pressTime != float('Inf'):           # if button is already pressed due to missing rise event or bouncing
            return                              # keep the current pressTime value, done
        pressTime = time()                      # get the current time
    else:                                       # if button rising event
        timePassed = time() - pressTime         # compute how long the button was pressed
        if timePassed < 2:                      # if it is less than 2 seconds
            pressTime = float('Inf')            # waiting for next button falling, prevent unintended reboot/shutdowns by setting this variable to positive infinity
        elif timePassed < 5:                    # if pressed for 2 up to 5 seconds
            call(['sudo reboot &'], shell=True) # do reboot
        else:                                   # if pressed for 5 seconds and more
            call(['shutdown -h now "System shutdown by GPIO action" &'], shell=True)   # do shutdown

def main():
    try:                        # run the program
        init()                  # initialize everything
        while True:             # idle loop
            sleep(60)           # wakes up once every minute
    except KeyboardInterrupt:
        GPIO.cleanup()          # clean up GPIO on CTRL+C exit
    GPIO.cleanup()              # clean up GPIO on normal exit

if __name__ == '__main__':
    main()