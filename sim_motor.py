import dataplotting
from collections import deque

class MotorController():

    def __init__(self, port, *args, **kwargs):
        self.deque_l = deque([0.0 for _ in range(200)], 200)
        self.deque_r = deque([0.0 for _ in range(200)], 200)

        self.frame_rate = 60    # fps
        # rgb but plotting expects values between 0.0 to 1.0
        graph_color = tuple(map(lambda x: x/256, (191,87,0)))
        self.plot = dataplotting.DataPlotting(
                {'left motor':self.deque_l,
                 'right motor':self.deque_r}, 
                {'left motor':graph_color,
                 'right motor':graph_color})

    def motors_set_right(self, speed):
        self.deque_r.append(speed)
        self.plot.update()
    def motors_set_left(self, speed):
        self.deque_l.append(speed)
        # we should be setting both at the same time, 
        # so only update the plot when setting the right motor
    