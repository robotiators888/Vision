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


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# define frame fragment maximum send size
maxFragmentSize = 4000


# begins thread to read camera frames
vs1 = WebcamVideoStream(src=0)
vs1.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
vs1.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
vs1.start()

vs2 = WebcamVideoStream(src=1)
vs2.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
vs2.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
vs2.start()

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
addressList1 = []
addressList2 = []

frameNumber = 0

# sockets from which we expect to read
inputs = [ sock ]
# sockets to which we expect to write
outputs = [ ]
# outgoing message queues
message_queues = {}

camera1 = False
camera2 = False

# keep looping
while True:

    # get frame from camera frame queue
    frame1 = vs1.read()
    frame2 = vs2.read()
    
    readyToRead, _, _ = select.select(inputs, outputs, inputs, 0.067)
    
    # if there is a message in ready
    if readyToRead:
            # try to catch all exceptions from socket reads
            try:

                # attempt to read message from socket
                data, address = sock.recvfrom(65507)

            except Exception:

                # set received fields to none when exception received
                # (an exception is generated each time one attempts to read from a socket and nothing is there)
                data = None
                address = None
                
            
            # if a message was received...
            if data:

                # process current message.

                # if the current message is a camera frame request message...
                if data.startswith("camera1"):
                    
                    camera1 = True
                    
                    # add new client to the address list.

                    print('received {0} bytes from {1}'.format(len(data), address))
                    print(data)

                    # if new client add to address list
                    if address not in addressList1:
                        addressList1.append(address)
                
                elif data.startswith("camera2"):
                    
                    camera2 = True
                    
                    # add new client to the address list.

                    print('received {0} bytes from {1}'.format(len(data), address))
                    print(data)

                    # if new client add to address list
                    if address not in addressList2:
                        addressList2.append(address)


    if (camera1 == True):
        
        # flatten image into single array
        #d = frame.flatten ()
        d1 = pickle.dumps(frame1)
        #print(d)
        #print(type(d))
        #exit()
        dLen1 = len(d1)
        #s = d.tostring ()
        #print('frame',frame)
        #print('flat',d)
        #exit(1)

        # start and stop indices of fragments
        start1 = 0
        stop1  = maxFragmentSize

        # first message in message list
        msg1 = struct.pack("!2I13f{0}s".format(maxFragmentSize),
                    10, # message Id
                    (15 * 4) + maxFragmentSize, # message length
                    0.0, # robot speed
                    0.0, 0.0, 0.0, # robot position
                    0.0, 0.0, 0.0, # robot orientation
                    0.0, 0.0, 0.0, # camera position
                    0.0, 0.0, 0.0, # camera orientation
                    d1[start1:stop1])
            

        #print('msgLength = ({0})'.format(len(msg)))
        # For each address in the address list...
        for address in addressList1:

            # send the current message.
            sent = sock.sendto(msg1, address)

        # initislize fragment counter to 1
        fragmentNumber1 = 1

        # increment start and stop to next frame interval
        start1 += maxFragmentSize
        stop1 = min(stop1 + maxFragmentSize, dLen1)

        #if address in addressList:
        #    print(stop-start)

        # Loop once for each message fragment
        while start1 < dLen1:

           #print(1 if stop >= dLen else 0, fragmentNumber, start,stop,stop - start, stop - start - 1)

            # Add another frame frament message to the message list
            msg1 = struct.pack("!4I{0}s".format(stop1-start1),
                          11, # message Id
                          16 + (stop1 - start1), # message length
                          fragmentNumber1,
                          1 if stop1 >= dLen1 else 0,
                          d1[start1:stop1])

            # For each address in the address list...
            for address in addressList1:

                # send the current message.
                sent = sock.sendto(msg1, address)

            # increment the the frame counter
            fragmentNumber1 += 1

            # increment start and stop to next frame interval
            start1 += maxFragmentSize
            stop1 = min(stop1 + maxFragmentSize, dLen1)
            
    if (camera2 == True):
        # flatten image into single array
        #d = frame.flatten ()
        d2 = pickle.dumps(frame2)
        #print(d)
        #print(type(d))
        #exit()
        dLen2 = len(d2)
        #s = d.tostring ()
        #print('frame',frame)
        #print('flat',d)
        #exit(1)

        # start and stop indices of fragments
        start2 = 0
        stop2  = maxFragmentSize

        # first message in message list
        msg2 = struct.pack("!2I13f{0}s".format(maxFragmentSize),
                    10, # message Id
                    (15 * 4) + maxFragmentSize, # message length
                    0.0, # robot speed
                    0.0, 0.0, 0.0, # robot position
                    0.0, 0.0, 0.0, # robot orientation
                    0.0, 0.0, 0.0, # camera position
                    0.0, 0.0, 0.0, # camera orientation
                    d2[start2:stop2])
            

        #print('msgLength = ({0})'.format(len(msg)))
        # For each address in the address list...
        for address in addressList2:

            # send the current message.
            sent = sock.sendto(msg2, address)

        # initislize fragment counter to 1
        fragmentNumber2 = 1

        # increment start and stop to next frame interval
        start2 += maxFragmentSize
        stop2 = min(stop2 + maxFragmentSize, dLen2)

        #if address in addressList:
        #    print(stop-start)

        # Loop once for each message fragment
        while start2 < dLen2:

           #print(1 if stop >= dLen else 0, fragmentNumber, start,stop,stop - start, stop - start - 1)

            # Add another frame frament message to the message list
            msg2 = struct.pack("!4I{0}s".format(stop2-start2),
                          11, # message Id
                          16 + (stop2 - start2), # message length
                          fragmentNumber2,
                          1 if stop2 >= dLen2 else 0,
                          d2[start2:stop2])

            # For each address in the address list...
            for address in addressList2:

                # send the current message.
                sent = sock.sendto(msg2, address)

            # increment the the frame counter
            fragmentNumber2 += 1

            # increment start and stop to next frame interval
            start2 += maxFragmentSize
            stop2 = min(stop2 + maxFragmentSize, dLen2)



# from fps_testing
vs.stop()



