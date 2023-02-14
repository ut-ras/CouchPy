import multiprocessing as mp
import time
# import motor
import sim_motor as motor
from collections import deque

class ControlThread():

    def __init__(self, buffer:mp.Array, queue:mp.JoinableQueue, port='dev/ttyS0', *args, **kwargs):
        self.buf = buffer
        self.q = queue
        self.port = port
        self.motor_controller = motor.MotorController(port)

        self.control_l = ControlThread.ControlLoop((10, 10))
        self.control_r = ControlThread.ControlLoop((10, 10))
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
            

