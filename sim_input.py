import multiprocessing as mp
import threading
import ctypes
import functools
import time

DEAD_ZONE_PERCENT = 5

class InputThread():
    """
    Logitech F310 Control Mapping

    for details check 'logitech controller codes.txt'
    """

    def __init__(self, buffer:mp.Array, queue:mp.JoinableQueue, *args, **kwargs):
        self.buf = buffer
        self.q = queue
        self.buf_idx = kwargs.get('buf_idx', None)

        # input function definitions
        self.input_functions = {
            1:functools.partial(self._generic_joystick_event, self.buf_idx['L-U/D']),
            5:functools.partial(self._generic_joystick_event, self.buf_idx['R-U/D'])
        } if self.buf_idx is not None else {
            1:functools.partial(self._generic_joystick_queue_event, 1),
            5:functools.partial(self._generic_joystick_queue_event, 5)
        }

    @staticmethod
    def _map_joystick(value:int) -> ctypes.c_double:
        percent = ((-value + 127) * 100) / 128
        if -DEAD_ZONE_PERCENT <= percent and percent <= DEAD_ZONE_PERCENT:
            percent = 0.0
        return ctypes.c_double(percent)

    def _generic_joystick_event(self, buffer_index:int, value:int):
        self.buf[buffer_index] = InputThread._map_joystick(value)

    def _generic_joystick_queue_event(self, id, value:int):
        self.q.put((id, InputThread._map_joystick(value)))

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

