"""input.py
Controller Input for Logitech F310
Controller inputs are collected asynchronously and inserted into 
a buffer and/or a queue to send to other process(es). Details about 
the buffer and queue can be found in `main.py`

Author: Tianda Huang
Date:   2023/02/01

TODO: add support and functionality for controller triggers buttons
"""

import multiprocessing as mp
import threading
import ctypes
import functools
from game_controllers import LogitechGamepadF310
from evdev import (InputDevice, list_devices)

class InputThread():
    """
    Logitech F310 Control Mapping

    for details check 'logitech controller codes.txt'
    """

    def __init__(self, buffer:mp.Array, queue:mp.JoinableQueue, *args, **kwargs):
        self.buf = buffer
        self.q = queue
        self.buf_idx = kwargs.get('buf_idx', None)
        self.dead_zone = kwargs.get('dead_zone', 5.0)   # dead zone in percent
        try:
            self.event_device = [
                    InputDevice(path).path for path in list_devices() if (
                        InputDevice(path).name == "Logitech Logitech Dual Action")
                    ][0]
        except Exception as e:  # controller not found
            print('Controller not found, plug in controller')
            raise e

        # input function definitions
        self.input_functions = {
            1:functools.partial(self._generic_joystick_event, self.buf_idx['L-U/D']),
            5:functools.partial(self._generic_joystick_event, self.buf_idx['R-U/D'])
        } if self.buf_idx is not None else {
            1:functools.partial(self._generic_joystick_queue_event, 1),
            5:functools.partial(self._generic_joystick_queue_event, 5)
        }

    def _map_joystick(self, value:int) -> ctypes.c_double:
        percent = ((-value + 127) * 100) / 128
        if -self.dead_zone <= percent and percent <= self.dead_zone:
            percent = 0.0
        return ctypes.c_double(percent)

    def _generic_joystick_event(self, buffer_index:int, value:int):
        self.buf[buffer_index] = self._map_joystick(value)

    def _generic_joystick_queue_event(self, id, value:int):
        self.q.put((id, self._map_joystick(value)))

    def _generic_button_event(self, id, value:int):
        self.q.put((id, value))

    def run(self):
        try:
            self.game_controller = LogitechGamepadF310(
                event_device=self.event_device, 
                codes=self.input_functions)

            # pause forever
            threading.Event().wait()
        except Exception as e:  # unexpected exception
            raise e

