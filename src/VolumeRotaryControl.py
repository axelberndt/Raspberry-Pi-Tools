#!/usr/bin/env python3.5

# This Python script reads a rotary encoder connected to GPIO pin 16 and 18, GND on pin 14 or any other ground pin,
# and controls the ALSA Master volume.
# Some encoders have inverse direction; in this case swap the values of GPIOpinA and GPIOpinB accordingly.
# This solution works without debouncing. However, very quick rotation may lead to missing state changes and, hence,
# some results could be wrong.
# Put it to a location on your Pi, say /home/pi/myTools/ and add the following line to /etc/rc.local before exit 0.
# python /home/pi/myTools/VolumeRotaryControl.py&
# After the next reboot the script will run in background.
# This script requires the python-alsaaudio package to be installed: sudo apt-get install python-alsaaudio.

# Author: Axel Berndt

# Rotary encoder pulse
#         +-------+       +-------+   0
#  A      |       |       |       |
#   ------+       +-------+       +-- 1
#     +-------+       +-------+       0
#  B  |       |       |       |
#   --+       +-------+       +------ 1

from RPi import GPIO
from time import sleep
import alsaaudio


GPIOpinA = 23   # left pin of the rotary encoder is on GPIO 23 (Pi pin 16)
GPIOpinB = 24   # right pin of the rotary encoder is on GPIO 24 (Pi pin 18)
lock = False    # this is set True to prevent interference of multiple interrupt processings
aDown = False   # this is set True to wait for GPIO A to go down
bUp = False     # this is set True to wait for GPIO B to go up
bDown = False   # this is set True to wait for GPIO B to go down


# initialize GPIO input and define interrupts
def init():
    GPIO.setmode(GPIO.BCM)                                                  # set the GPIO naming/numbering convention to BCM
    GPIO.setup(GPIOpinA, GPIO.IN, pull_up_down=GPIO.PUD_UP)                 # input channel A
    GPIO.setup(GPIOpinB, GPIO.IN, pull_up_down=GPIO.PUD_UP)                 # input channel B
    GPIO.add_event_detect(GPIOpinA, GPIO.BOTH, callback=rotaryInterruptA)   # define interrupt for action on channel A (no bouncetime needed)
    GPIO.add_event_detect(GPIOpinB, GPIO.BOTH, callback=rotaryInterruptB)   # define interrupt for action on channel B (no bouncetime needed)


# the callback functions when turning the encoder
# this one reacts on action on channel A
def rotaryInterruptA(GPIOpin):
    global lock, GPIOpinA, GPIOpinB         # get access to some global variables
    A = GPIO.input(GPIOpinA)                # read current value of channel A
    B = GPIO.input(GPIOpinB)                # read current value of channel B

    while lock:                             # while another interrupt is processing
        pass                                # wait

    lock = True                             # now, prevent other interrupts to interfere

    global value, aDown, bUp, bDown         # get access to some more global variables
    if aDown:                               # if we are waiting for channel A to go down (to finish -> rotation cycle)
        if not A:                           # check if it is down now
            aDown = False                   # -> rotation cycle finished
    elif bUp or bDown:                      # if a <- rotation cycle is unfinished so far
        pass                                # don't do anything new
    elif A:                                 # if a new rotation cycle starts, i.e. nothing to go up or down
        mixer = alsaaudio.Mixer()           # get ALSA mixer channel 'Master'
        # To control a different mixer channel, e.g. the 'Digital' channel from IQaudIO's Pi-DAC+ card, edit the above line in the following way
        # mixer = alsaaudio.Mixer('Digital')
        volume = int(mixer.getvolume()[0])  # get the left channel's volume gain (right channel is the same)

        if B:                               # if B is already up, the rotation direction is ->
            aDown = True                    # to finish the cycle, wait for A to go down again
            if volume < 100:                # do not get greater than 100 (ALSA max)
                volume += 1                 # increase volume gain
        else:                               # if B still has to come up, the rotation direction is <-
            bUp = True                      # in this rotation cycle B has to come up and down again, we start with waiting for B to come up
            if volume > 0:                  # do not get below 0 (ALSA min)
                volume -= 1                 # decrease volume gain

        mixer.setvolume(volume)             # apply the new volume gain to the mixer channel
        # To control the different subchannels of the mixer channel independently, replace the line above by these (example for stereo)
        # mixer.setvolume(volume, 0)          # apply the new volume gain to the left line of the mixer channel
        # mixer.setvolume(volume, 1)          # apply the new volume gain to the right line of the mixer channel

    lock = False                            # unlock, now other interrupts can do their job
    return                                  # done


# this callback function reacts on action on channel B
def rotaryInterruptB(GPIOpin):
    global lock, GPIOpinB           # get access to some global variables
    B = GPIO.input(GPIOpinB)        # read current value of channel B

    while lock:                     # while another interrupt is processing
        pass                        # wait

    lock = True                     # now, prevent other interrupts to interfere

    global bUp, bDown               # get access to some more global variables
    if B:                           # if B is up
        if bUp:                     # and we have been waiting for B to come up (this is part of the <- rotation cycle)
            bDown = True            # wait for B to come down again
            bUp = False             # done with this
    elif bDown:                     # B is down (if B: was False) and if we were waiting for B to come down
        bDown = False               # <- rotation cycle finished

    lock = False                    # unlock, now other interrupts can do their job
    return                          # done


# the main function
def main():
    try:                        # run the program
        init()                  # initialize everything
        while True:             # idle loop
            sleep(300)          # wakes up once every 5 minutes = 300 seconds
    except KeyboardInterrupt:
        GPIO.cleanup()          # clean up GPIO on CTRL+C exit
    GPIO.cleanup()              # clean up GPIO on normal exit

# the entry point
if __name__ == '__main__':
    main()