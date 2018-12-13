#!/usr/bin/env python

# import the necessary packages
from collections import deque
from imutils.video import WebcamVideoStream

import argparse

try:
    import cPickle as pickle
except:
    import pickle

import cv2
import imutils
import numpy as np
import socket
import sys
import struct
import time
import select


# define frame fragment maximum send size
maxFragmentSize = 4000

# begins thread to read camera frames
vs = WebcamVideoStream(src=0).start()
#vsBack = WebcamVideoStream(src=1).start()

#vs = vsFront

#vs.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
#vs.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# defines server address to work on all TCP stacks
HOST = "0.0.0.0"
PORT = 8888

# create a UDP socket endpoint
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# attaches socket to server address
sock.bind((HOST, PORT))

# defines socket as non blocking
sock.setblocking(0)

# creates a list of addresses for those who want camera frames
addressList = []

frameNumber = 0


# keep looping
while True:
    
    # get frame from camera frame queue
    frame = vs.read()

    # try to catch all exceptions from socket reads
    try:

        # attempt to read message from socket
        data, address = sock.recvfrom(65507)
        print(data)
        print(address)

    except Exception:

        # set received fields to none when exception received
        # (an exception is generated each time one attempts to read from a socket and nothing is there)
        data = None
        address = None

    # if a message was received...
    if data:

        # process current message.

        # if the current message is a camera frame request message...
        if data.startswith("camera"):
            receiver = address
            
        #elif data.startswith("frontCamera"):
            #vs = vsFront
            
        #elif data.startswith("backCamera"):
            #vs = vsBack
            
            

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),40]
    result, imgencode = cv2.imencode('.jpg', frame, encode_param)
    
    d = pickle.dumps(imgencode)
    dLen = len(d)

    # start and stop indices of fragments
    start = 0
    stop  = maxFragmentSize

    # first message in message list
    msg = struct.pack("!2I{0}s".format(maxFragmentSize),
                      10, # message Id
                      8 + maxFragmentSize, # message length
                      d[start:stop])

        
    try:
        # send the current message.
        sent = sock.sendto(msg, receiver)
    except Exception:
        pass

    # initislize fragment counter to 1
    fragmentNumber = 1

    # increment start and stop to next frame interval
    start += maxFragmentSize
    stop = min(stop + maxFragmentSize, dLen)


    # Loop once for each message fragment
    while start < dLen:


        # Add another frame frament message to the message list
        msg = struct.pack("!4I{0}s".format(stop-start),
                          11, # message Id
                          16 + (stop - start), # message length
                          fragmentNumber,
                          1 if stop >= dLen else 0,
                          d[start:stop])

        try:
            # send the current message.
            sent = sock.sendto(msg, receiver)
        except Exception:
            pass

        # increment the the frame counter
        fragmentNumber += 1

        # increment start and stop to next frame interval
        start += maxFragmentSize
        stop = min(stop + maxFragmentSize, dLen)



# from fps_testing
vs.stop()


