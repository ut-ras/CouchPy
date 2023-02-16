#!/usr/bin/env python3
# Copyright (c) 2023 UT Longhorn Racing Solar
"""couch.py
Very Basic Couch Control
Caution(!) will be very jerky

Author: Tianda Huang
Date:   2023/02/01
"""

from time import sleep
from sabertooth2x60 import SabertoothPacketized
from game_controllers import LogitechGamepadF310
from evdev import (InputDevice, list_devices)

port = '/dev/ttyS0'

DONT_MAKE_ME_REPEAT_MYSELF = 2
MOTOR_ENABLE = True
DEAD_ZONE_PERCENT = 5
EXECUTION_RATE = 50

def main():

    left_percent = 0.0
    right_percent = 0.0
    controller_pair = SabertoothPacketized(port, baudrate=9600)

    def left_motor_event(value):
        percent = ((-value + 127) * 100) / 128
        if percent <= DEAD_ZONE_PERCENT and percent >= -DEAD_ZONE_PERCENT:
            percent = 0.0
        nonlocal left_percent
        left_percent = percent
                

    def right_motor_event(value):
        percent = ((-value + 127) * 100) / 128
        if percent <= DEAD_ZONE_PERCENT and percent >= -DEAD_ZONE_PERCENT:
            percent = 0.0
        nonlocal right_percent
        right_percent = percent
          

    event_device = [InputDevice(path).path for path in list_devices() if InputDevice(path).name == "Logitech Logitech Dual Action"][0]
    input_functions = {
        1 : left_motor_event,
        5 : right_motor_event
    }
    
    game_controller = LogitechGamepadF310(event_device=event_device, codes=input_functions)

    while True:
        right_percent
        left_percent
        print('r/l', right_percent, left_percent)
        controller_pair.motors_set_right(right_percent)
        controller_pair.motors_set_left(left_percent)
        sleep(1/EXECUTION_RATE)



def test_main():
    controller_pair = SabertoothPacketized(port, baudrate=9600)
    test_values = (-100, 0, 100, 0, -50, 0, 50, 0)
    sleep(1)
    for speed in test_values:
        print('right motor:', speed)
        controller_pair.motors_set_right(speed)
        sleep(1)
    for speed in test_values:
        print('left motor:', speed)
        controller_pair.motors_set_left(speed)
        sleep(1)
    print('both motors: stop')
    while True:
        controller_pair.motors_stop()
        sleep(1)

if __name__ == '__main__':
    main()
