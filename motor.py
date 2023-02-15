"""motor.py
Motor Controller wrapper interface

Author: Tianda Huang
Date:   2023/02/01
"""

from sabertooth2x60 import SabertoothPacketized

class MotorController():

    def __init__(self, port, *args, **kwargs):
        self.motor_controller = SabertoothPacketized(port, baudrate=9600)
    def motors_set_right(self, speed):
        self.motor_controller.motors_set_right(speed)
    def motors_set_left(self, speed):
        self.motor_controller.motors_set_right(speed)
