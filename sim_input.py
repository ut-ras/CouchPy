# Copyright (c) 2023 UT Longhorn Racing Solar
"""sim_input.py
Simulated Controller Input
Controller inputs are fed into a buffer and/or a queue in a loop based 
on predefined inputs.

Author: Tianda Huang
Date:   2023/02/01
"""

import multiprocessing as mp
import ctypes
import functools
import time

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
        while True:
            for r, l in [
                ((1, 0), (5, 0)),
                ((1, 255), (5, 255)),
            ] :
                self.input_functions[r[0]](r[1])
                self.input_functions[l[0]](l[1])
                time.sleep(2)

