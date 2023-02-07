
import multiprocessing as mp
import ctypes
import os
import signal
import sys
import argparse

# collects user inputs and sends to handler thread
def input_thread(buf, q):
    pass

# handles user inputs sent from input thread
def handler_thread(buf, q):
    pass

def main():

    ARRAY_SIZE = 3
    QUEUE_LEN = 20

    """ real time input buffer
    thread-safe buffer to share data between a producer and consumer
    data is not guaranteed to be received; data can be updated by 
    producer without being acknowledged by consumer

    meant to be used by controller joysticks or other inputs with 
    frequent updates and intermediate values that can be ignored
    """
    input_buf = mp.Array(ctypes.c_double, (0.0 for i in range(ARRAY_SIZE)))

    """ input queue
    thread-safe queue to share data between a producer and consumer
    data in queue remains valid until the queue fills; data updated by
    producer will be appended to the queue.

    meant to be used by controller buttons or other inputs where 
    all inputs must be acknowledged (but not necessarily in real time)
    """
    input_queue = mp.JoinableQueue(QUEUE_LEN)

    # start processes

    input = mp.Process(target = handler_thread, args=(input_buf, input_queue))
    handler = mp.Process(target = handler_thread, args=(input_buf, input_queue))
    
    input.start()
    handler.start()

    # not reached unless program is terminated
    
    input_queue.join()
    input.join()
    handler.join()


if __name__ == '__main__':
    mp.set_start_method('spawn')
    main()

