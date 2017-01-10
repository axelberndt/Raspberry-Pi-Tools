#!/usr/bin/env python3.5

# This is a combination of ShutdownRebootButton.py and VolumeRotaryControl.py. It is handy for those who use a rotary switch.

# Author: Axel Berndt


from RPi import GPIO
from time import sleep, time
from subprocess import call
import alsaaudio


GPIOpinButton = 27          # Button is on GPIO channel 27 / pin 13 of 40way connector with GND on pin 14
GPIOpinA = 23               # left pin of the rotary encoder is on GPIO 23 (Pi pin 16)
GPIOpinB = 24               # right pin of the rotary encoder is on GPIO 24 (Pi pin 18)
aDown = False               # this is set True to wait for GPIO A to go down
bUp = False                 # this is set True to wait for GPIO B to go up
bDown = False               # this is set True to wait for GPIO B to go down
pressTime = float('Inf')    # this is used to keep track of the time passing between button press and release, when waiting for button press/falling it has the positive inf value to prevent unintended shutdowns


# initialize GPIO input and define interrupts
def init():
    GPIO.setmode(GPIO.BCM)                                                  # set the GPIO naming/numbering convention to BCM
    GPIO.setup(GPIOpinA, GPIO.IN, pull_up_down=GPIO.PUD_UP)                 # input channel A
    GPIO.setup(GPIOpinB, GPIO.IN, pull_up_down=GPIO.PUD_UP)                 # input channel B
    GPIO.setup(GPIOpinButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)            # setup the channel as input with a 50K Ohm pull up. A push button will ground the pin, creating a falling edge.
    GPIO.add_event_detect(GPIOpinA, GPIO.BOTH, callback=rotaryInterruptA)   # define interrupt for action on channel A (no bouncetime needed)
    GPIO.add_event_detect(GPIOpinB, GPIO.BOTH, callback=rotaryInterruptB)   # define interrupt for action on channel B (no bouncetime needed)
    GPIO.add_event_detect(GPIOpinButton, GPIO.BOTH, callback=buttonInterrupt, bouncetime=100)  # define interrupt


# the callback functions when turning the encoder
# this one reacts on action on channel A
def rotaryInterruptA(GPIOpin):
    A = GPIO.input(GPIOpinA)                # read current value of channel A
    B = GPIO.input(GPIOpinB)                # read current value of channel B

    global aDown, bUp, bDown                # get access to some more global variables
    if aDown:                               # if we are waiting for channel A to go down (to finish -> rotation cycle)
        if not A:                           # check if it is down now
            aDown = False                   # -> rotation cycle finished
    elif bUp or bDown:                      # if a <- rotation cycle is unfinished so far
        pass                                # don't do anything new
    elif A:                                 # if a new rotation cycle starts, i.e. nothing to go up or down
        mixer = alsaaudio.Mixer()           # get ALSA mixer channel 'Master'
        volume = int(mixer.getvolume()[0])  # get the left channel's volume gain (right channel is the same)
        if B:                               # if B is already up, the rotation direction is ->
            aDown = True                    # to finish the cycle, wait for A to go down again
            volume += 1                     # increase volume gain
            if volume > 100:                # but do not get greater than 100 (ALSA max)
                volume = 100                # any value greater than 100 is clipped at 100
        else:                               # if B still has to come up, the rotation direction is <-
            bUp = True                      # in this rotation cycle B has to come up and down again, we start with waiting for B to come up
            volume -= 1                     # decrease volume gain
            if volume < 0:                  # but do not get less than 0 (ALSA min)
                volume = 0                  # any value less than 0 is clipped at 0
        mixer.setvolume(volume)             # apply the new volume gain to the mixer channel
    return                                  # done


# this callback function reacts on action on channel B
def rotaryInterruptB(GPIOpin):
    B = GPIO.input(GPIOpin) # read current value of channel B

    global bUp, bDown       # get access to some more global variables
    if B:                   # if B is up
        if bUp:             # and we have been waiting for B to come up (this is part of the <- rotation cycle)
            bDown = True    # wait for B to come down again
            bUp = False     # done with this
    elif bDown:             # B is down (if B: was False) and if we were waiting for B to come down
        bDown = False       # <- rotation cycle finished
    return                  # done


# the callback function when button is pressed/released
def buttonInterrupt(GPIOpin):
    global pressTime                            # get access to the global time variable
    if not GPIO.input(GPIOpin):                 # if button falling event
        pressTime = time()                      # get the current time
    else:                                       # if button rising event
        timePassed = time() - pressTime         # compute how long the button was pressed
        if timePassed < 2:                      # if it is less than 2 seconds
            pressTime = float('Inf')            # waiting for next button falling, prevent unintended reboot/shutdowns by setting this variable to positive infinity
        elif timePassed < 5:                    # if pressed for 2 up to 5 seconds
            call(['sudo reboot &'], shell=True) # do reboot
        else:                                   # if pressed for 5 seconds and more
            call(['shutdown -h now "System shutdown by GPIO action" &'], shell=True)   # do shutdown


# the main function
def main():
    try:                    # run the program
        init()              # initialize everything
        while True:         # idle loop
            sleep(300)      # wakes up once every 5 minutes = 300 seconds
    except KeyboardInterrupt:
        GPIO.cleanup()      # clean up GPIO on CTRL+C exit
    GPIO.cleanup()          # clean up GPIO on normal exit

# the entry point
if __name__ == '__main__':
    main()