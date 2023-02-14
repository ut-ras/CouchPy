import multiprocessing as mp
import threading
import ctypes
import functools
from game_controllers import LogitechGamepadF310
from evdev import (InputDevice, list_devices)

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
            1:functools.partialmethod(_generic_joystick_event, self.buf_idx['L-U/D']),
            5:functools.partialmethod(_generic_joystick_event, self.buf_idx['R-U/D'])
        } if self.buf_idx is not None else {
            1:functools.partial(self._generic_joystick_queue_event(1)),
            5:functools.partial(self._generic_joystick_queue_event(5))
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
        try:
            self.game_controller = game_controller = LogitechGamepadF310(
                event_device=self.event_device, 
                codes=self.input_functions)

            # pause forever
            threading.Event().wait()
        except Exception as e:  # unexpected exception
            raise e

