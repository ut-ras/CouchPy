# Copyright (c) 2023 UT Longhorn Racing Solar
"""dataplotting.py
Simple Matplotlib live plotting
Updates as fast as you can call update() and as fast as the CPU can run update() 

Author: Tianda Huang
Date:   2023/02/01

Usage:
    plot = DataPlotting(...)
    while True:
        plot.update()
        sleep(...)
"""

import sys
import matplotlib.pyplot as plt
from collections import deque

class DataPlotting:
    """
    Plots streamed data from a single device using Matplotlib
    Uses blitting for responsive graph updates
    """

    def __init__(self, graphics_queues : dict[deque], colors : dict[tuple] = None, *args, **kwargs) -> None:
        self.queues = graphics_queues
        self.colors = colors

        SUBPLOT_ROWS = len(graphics_queues)
        SUBPLOT_COLS = 1

        self.fig = plt.figure()
        self.resize_event = self.fig.canvas.mpl_connect('resize_event', self.redraw)

        self.axes = {key:self.fig.add_subplot(SUBPLOT_ROWS, SUBPLOT_COLS, i+1) 
                     for i, key in enumerate(graphics_queues)}
        self.clear = {key:[sys.float_info.max for _ in graphics_queues[key]]
                      for key in self.axes}
        
        # self._reset_axes()
        plt.show(block=False)
        plt.pause(0.5)
        self.redraw()
        # self._update_background()
        # self.update()

    def update(self):
        for key in self.lines:
            self.lines[key].set_ydata(self.queues[key])
            self.fig.canvas.restore_region(self.backgrounds[key])
            self.axes[key].draw_artist(self.lines[key])
            self.fig.canvas.blit(self.axes[key].bbox)
        
        self.fig.canvas.flush_events()

    def redraw(self, event=None):
        for key in self.axes: self.axes[key].cla()
        self._reset_axes()
        self._update_background()
        self.update()

    def stop(self):
        print('displaying last output. close figure to continue')
        plt.show()

    def _reset_axes(self):
        self.lines = {key:(self.axes[key].plot(self.clear[key],
                           color=self.colors[key])[0]) 
                      for key in self.axes}

        # plot title, label, and color config
        for key in self.axes:
            self.axes[key].set_ylabel(key)
            self.axes[key].set_ylim((-100, 100))
            self.axes[key].xaxis.set_visible(False)
        
        self.fig.canvas.draw()

    def _update_background(self):
        self.backgrounds = {key:self.fig.canvas.copy_from_bbox(self.axes[key].bbox) 
                            for key in self.axes}

