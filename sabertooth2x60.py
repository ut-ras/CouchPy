# Copyright (c) 2023 UT Longhorn Racing Solar
"""sabertooth2x60.py
Driver for interfacing with two Sabertooth2x60 motor controllers
Uses packetized serial mode for communication 

Author: Tianda Huang
Date:   2023/02/01
"""

import time
import serial

class SabertoothPacketized():

    ADDRESS_LEFT = 128
    ADDRESS_RIGHT = 129

    # valid commands used for reference. 
    # these may be aliased elsewhere for performance
    COMMAND_TABLE = {
        'MOTOR1_FWD':0,
        'MOTOR1_REV':1,
        'MIN_VOLTAGE':2,
        'MAX_VOLTAGE':3,
        'MOTOR2_FWD':4,
        'MOTOR2_REV':5,
        'BAUD_RATE':15
        # TODO: add all the other commands
    }
    # usage example for motor1: 
    # cmd = MOTOR1_FWD + MOTOR_REV_OFS if speed < 0 else 0
    MOTOR1_FWD = 0
    MOTOR2_FWD = 4
    MOTOR_REV_OFS = 1

    def __init__(self, port, baudrate=9600):
        self._serial = serial.Serial(
                port=port, 
                baudrate=baudrate, 
                timeout=1, 
                write_timeout=1)

    def motors_stop(self):
        self.motors_set_right(0)
        self.motors_set_left(0)

    # speed should be a float from -100 to 100, negative for backwards
    def motors_set_right(self, speed : float):
        motor_value = int(127 * abs(speed) / 100.0)
        cmd1 = self.MOTOR1_FWD + (self.MOTOR_REV_OFS if speed < 0 else 0)
        cmd2 = self.MOTOR2_FWD + (self.MOTOR_REV_OFS if speed < 0 else 0)
        self._send_packetized(self.ADDRESS_RIGHT, cmd1, motor_value)
        self._send_packetized(self.ADDRESS_RIGHT, cmd2, motor_value)

    # speed should be a float from -100 to 100, negative for backwards
    def motors_set_left(self, speed : float):
        motor_value = int(127 * abs(speed) / 100.0)
        cmd1 = self.MOTOR1_FWD + (self.MOTOR_REV_OFS if speed < 0 else 0)
        cmd2 = self.MOTOR2_FWD + (self.MOTOR_REV_OFS if speed < 0 else 0)
        self._send_packetized(self.ADDRESS_LEFT, cmd1, motor_value)
        self._send_packetized(self.ADDRESS_LEFT, cmd2, motor_value)
    
    def baudrate_set(self, baudrate):
        baudrates = {
            2400:1,
            9600:2,
            19200:3,
            38400:4,
            115200:5
        }
        if baudrate not in baudrates:
            raise ValueError
        # we have no idea the existing baudrate so we send with all.
        baudrate_id = baudrates[baudrate]
        for br in baudrates:
            self._serial.baudrate = br
            self._send_packetized(
                    self.ADDRESS_LEFT, 
                    self.COMMAND_TABLE['BAUD_RATE'], 
                    baudrate_id)
            time.sleep(0.05)
            self._send_packetized(
                    self.ADDRESS_RIGHT, 
                    self.COMMAND_TABLE['BAUD_RATE'], 
                    baudrate_id)
            time.sleep(0.05)
        self._serial.baudrate = baudrate

    def _send_packetized(self, address, command, value):
        # packet is 3-bytes:
        # byte 1 = address, byte 2 = command, byte 3 = value, byte 4 = 7 bit checksum
        # all addresses should be > 128, all commands/values should be under 128
        packet = bytearray((
                address, command, value, 
                (address + command + value) & 127))
        self._serial.write(data=packet)
