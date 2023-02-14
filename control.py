import multiprocessing as mp
import threading as thr
import time
# from sabertooth2x60 import SabertoothPacketized
import numpy as np
import dataplotting
from collections import deque

class ControlThread():

    # TODO: PID

    def __init__(self, buffer:mp.Array, queue:mp.JoinableQueue, port='dev/ttyS0', *args, **kwargs):
        self.buf = buffer
        self.q = queue
        self.port = port
        # self.motor_controllers = SabertoothPacketized(port, baudrate=9600)
        self.buf_idx = kwargs.get('buf_idx', None)
        self.period = kwargs.get('period', 0.02)

    def _calculate_next_speed(self):
        pass

    def run(self):

        self.deque = deque([0.0 for _ in range(200)], 200)
        self.plot = dataplotting.DataPlotting({'motor':self.deque}, {'motor':(191/256,87/256,0/256)})

        # funny little function to sleep for (period - execution time)
        def get_sleep_time():
            t = time.time()
            while True:
                t += self.period
                yield max(t - time.time(), 0)

        sleep_time = get_sleep_time()
        while True:
            time.sleep(next(sleep_time))

            speed = 0.0 # TODO:
            self.deque.append(speed)
            self.plot.update()

            # self.motor_controllers.motors_set_right(speed_l)
            # self.motor_controllers.motors_set_left(speed_r)

