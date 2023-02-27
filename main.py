#!/usr/bin/env python3
"""main.py
CouchBot (Python Implementation) Main File
Launches processes for handling controller inputs and running motors

Simulation:
    To simulate controller input, `import sim_input as input`
    To simulate motor output, `import sim_motor as motor` in `control.py`
    Simulated controller input is a loop feeding constant values;
    simulated motor output is a live-graph plotting current motor output values

Author: Tianda Huang
Date:   2023/02/01

Usage:
    run
        main.py --help
    for a description of possible command line arguments
"""

import multiprocessing as mp
import ctypes
import argparse

## Process Imports
# import input
import sim_input as input
import control

# collects user inputs and sends to handler thread
def input_thread(buf, q, *args, **kwargs):
    p = input.InputThread(buf, q, *args, **kwargs)
    p.run()

# handles user inputs sent from input thread
def handler_thread(buf, q, *args, **kwargs):
    p = control.ControlThread(buf, q, *args, **kwargs)
    p.run()

def main(args:argparse.Namespace):

    INPUT_BUFFER_IDX = {
        'L-U/D':0,
        'R-U/D':1,
        'L-R/L':2,
        'R-R/L':3}
    
    """ real time input buffer
    thread-safe buffer to share data between a producer and consumer
    data is not guaranteed to be received; data can be updated by 
    producer without being acknowledged by consumer

    meant to be used by controller joysticks or other inputs with 
    frequent updates and intermediate values that can be ignored

    Index 0: Left Stick - U/D - fully up is 100.0
          1: Right Stick - U/D - fully up is 100.0
          2: Left Stick - L/R - fully left is 100.0
          3: Right Stick - L/R - fully left is 100.0
    """
    input_buf = mp.Array(ctypes.c_double, [0.0 for i in range(len(INPUT_BUFFER_IDX))])

    """ input queue
    thread-safe queue to share data between a producer and consumer
    data in queue remains valid until the queue fills; data updated by
    producer will be appended to the queue.

    meant to be used by controller buttons or other inputs where 
    all inputs must be acknowledged (but not necessarily in real time)
    """
    input_queue = mp.JoinableQueue(args.QUEUE_LEN)

    # start processes

    input = mp.Process(target = input_thread, 
            args=(input_buf, input_queue), 
            kwargs={'buf_idx':INPUT_BUFFER_IDX})
    handler = mp.Process(target = handler_thread, 
            args=(input_buf, input_queue),
            kwargs={'buf_idx':INPUT_BUFFER_IDX, 'simulate':args.simulate})
    
    input.start()
    handler.start()

    # not reached unless program is terminated
    
    input_queue.join()
    input.join()
    handler.join()


if __name__ == '__main__':
    mp.set_start_method('spawn')

    parser = argparse.ArgumentParser(
        prog='CouchBot Main',
        description='Launches processes for handling controller inputs and running motors',
        epilog='🛋️')
    arguments_list = [
        (['-ql', '--queue_len'], {'default':20, 'dest':'QUEUE_LEN', 'type':int}),
        (['-s', '--simulate'], {'action':'store_true', 'dest':'simulate'})]
    for e in arguments_list: parser.add_argument(*e[0], **e[1])
    args = parser.parse_args()

    main(args)

