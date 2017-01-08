#!/usr/bin/env python3.5

# This Python script reads a rotary encoder connected to GPIO pin 16 and 18, GND on pin 14 or any other ground pin.
# Some encoders have inverse direction; in this case swap the values of GPIOpinA and GPIOpinB accordingly.
# This solution works without debouncing. However, very quick rotation may lead to missing state changes and, hence,
# some results could be wrong.
# Put it to a location on your Pi, say /home/pi/myTools/ and write the following line at the terminal.
# python /home/pi/myTools/RotaryEncoder.py&
# This will execute the script in background and produce terminal output whenever the encoder rotates.
# To stop the script write
# ps -elf | grep python
# at the terminal and find the process id (PID) of the script. Then write this line and insert the right PID:
# kill -9 PID

# Author: Axel Berndt

#
# Rotary encoder pulse
#         +-------+       +-------+   0
#  A      |       |       |       |
#   ------+       +-------+       +-- 1
#     +-------+       +-------+       0
#  B  |       |       |       |
#   --+       +-------+       +------ 1

import RPi.GPIO
from time import sleep


GPIOpinA = 23   # left pin of the rotary encoder is on GPIO 23 (Pi pin 16)
GPIOpinB = 24   # right pin of the rotary encoder is on GPIO 24 (Pi pin 18)
value = 0       # this value will be in-/decreased by rotating the encoder
lock = False    # this is set True to prevent interference of multiple interrupt processings
aDown = False   # this is set True to wait for GPIO A to go down
bUp = False     # this is set True to wait for GPIO B to go up
bDown = False   # this is set True to wait for GPIO B to go down


# initialize GPIO input and define interrupts
def init():
    RPi.GPIO.setmode(RPi.GPIO.BCM)                                                  # set the GPIO naming/numbering convention to BCM
    RPi.GPIO.setup(GPIOpinA, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)             # input channel A
    RPi.GPIO.setup(GPIOpinB, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)             # input channel B
    RPi.GPIO.add_event_detect(GPIOpinA, RPi.GPIO.BOTH, callback=rotaryInterruptA)   # define interrupt for action on channel A (no bouncetime needed)
    RPi.GPIO.add_event_detect(GPIOpinB, RPi.GPIO.BOTH, callback=rotaryInterruptB)   # define interrupt for action on channel B (no bouncetime needed)


# the callback functions when turning the encoder
# this one reacts on action on channel A
def rotaryInterruptA(GPIOpin):
    global lock, GPIOpinA, GPIOpinB     # get access to some global variables
    A = RPi.GPIO.input(GPIOpinA)        # read current value of channel A
    B = RPi.GPIO.input(GPIOpinB)        # read current value of channel B

    while lock:                         # while another interrupt is processing
        pass                            # wait

    lock = True                         # now, prevent other interrupts to interfere

    global value, aDown, bUp, bDown     # get access to some more global variables
    if aDown:                           # if we are waiting for channel A to go down (to finish -> rotation cycle)
        if not A:                       # check if it is down now
            aDown = False               # -> rotation cycle finished
    elif bUp or bDown:                  # if a <- rotation cycle is unfinished so far
        pass                            # don't do anything new
    elif A:                             # if a new rotation cycle starts, i.e. nothing to go up or down
        if B:                           # if B is already up, the rotation direction is ->
            aDown = True                # to finish the cycle, wait for A to go down again
            value += 1                  # increase our test output value
            print("-> " + str(value))   # make terminal output
        else:                           # if B still has to come up, the rotation direction is <-
            bUp = True                  # in this rotation cycle B has to come up and down again, we start with waiting for B to come up
            value -= 1                  # decrease our test output value
            print("<- " + str(value))   # make terminal output

    lock = False                        # unlock, now other interrupts can do their job
    return                              # done


# this callback function reacts on action on channel B
def rotaryInterruptB(GPIOpin):
    global lock, GPIOpinB           # get access to some global variables
    B = RPi.GPIO.input(GPIOpinB)    # read current value of channel B

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
        RPi.GPIO.cleanup()      # clean up GPIO on CTRL+C exit
    RPi.GPIO.cleanup()          # clean up GPIO on normal exit

# the entry point
if __name__ == '__main__':
    main()