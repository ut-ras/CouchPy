"""control.py
Control Loop
Controls motors based on controller input and control loop output

The open-loop control scheme is a multi-order moving average filter:
Desired speed setpoints (inputs from controller) are averaged in a moving 
filter; outputs from the first layer moving filter are averaged, etc.
The average of the final moving filter is the actual output speed.

Motor speeds are sent to motor controllers periodically

Simulation:
    To simulate motor output, `import sim_motor as motor` in `control.py`
    Simulated motor output is a live-graph plotting current motor output values

Author: Tianda Huang
Date:   2023/02/01

Usage:
    run
        main.py --help
    for a description of possible command line arguments
"""

import multiprocessing as mp
import time
from collections import deque

# import motor
import sim_motor as motor

class ControlThread():

    def __init__(self, buffer:mp.Array, queue:mp.JoinableQueue, port='dev/ttyS0', *args, **kwargs):
        self.buf = buffer
        self.q = queue
        self.port = port
        self.motor_controller = motor.MotorController(port)

        self.control_l = ControlThread.ControlLoop((10, 10, 5))
        self.control_r = ControlThread.ControlLoop((10, 10, 5))
        self.buf_idx = kwargs.get('buf_idx', None)
        self.period = kwargs.get('period', 0.02)

    class ControlLoop():
        """
        Multi-order moving average filter
        """

        def __init__(self, layer_sizes:tuple[int]):
            self.layer_sizes = layer_sizes
            # layers[0] is first moving average, [1] is moving average of [0], etc.
            self.layers = [deque([0.0 for i in range(l)], l) 
                           for l in layer_sizes]
            self.totals = [0.0 for _ in layer_sizes]

        # setpoint should be a value between (-100.0 and 100.0) but any value will work
        def update(self, setpoint:float) -> float:
            prev_average = setpoint
            for i, l in enumerate(self.layers):
                self.totals[i] = self.totals[i] - l[0] + prev_average
                l.append(prev_average)
                prev_average = self.totals[i]/self.layer_sizes[i]
            return prev_average

    def run(self):

        # funny little function to sleep for (period - execution time)
        def get_sleep_time():
            t = time.time()
            while True:
                t += self.period
                yield max(t - time.time(), 0)

        sleep_time = get_sleep_time()
        while True:
            time.sleep(next(sleep_time))

            speed_l = self.control_l.update(
                    float(self.buf[self.buf_idx['L-U/D']]))
            speed_r = self.control_r.update(
                    float(self.buf[self.buf_idx['R-U/D']]))
            
            self.motor_controller.motors_set_left(speed_l)
            self.motor_controller.motors_set_right(speed_r)
            

