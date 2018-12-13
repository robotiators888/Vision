#!/usr/bin/env python

# import the necessary packages
import argparse

try:
    import cPickle as pickle
except:
    import pickle

import cv2
import select
import socket
import struct
import sys
import time


# define frame fragment maximum send size
maxFragmentSize = 61440

# defines server address to work on all TCP stacks
HOST    = "0.0.0.0"
PORT    = 9999
ADDRESS = (HOST, PORT)

# defines camera frame provider address
cameraHost    = "10.8.88.12"
cameraPort    = 8888
cameraAddress = (cameraHost, cameraPort)

# create a UDP socket endpoint
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# attaches socket to server address
sock.bind(ADDRESS)


inputs = [sock]
outputs = []

state = 'idle'

# keep looping
while True:

    readable, _, _ = select.select(inputs, outputs, inputs, 0.25)
	
    # try to catch all exceptions from socket reads
    try:
	    if readable:
		    # attempt to read message from socket
			#msg, address = sock.recvfrom(65507)
		    msg, address = sock.recvfrom(65536)
	    else: 
		    sock.sendto("camera", cameraAddress)
		    msg = None
		    address = None

    except Exception:

    #    # set received fields to none when exception received
    #    # (an exception is generated each time one attempts to read from a socket and nothing is there)
        msg = None
        address = None

    # if a message was received...
    if msg and (len(msg) >= 8):

        # process current message.

        msgId, msgLength = struct.unpack('!2I', msg[0:8])

        # If this is message 10....
        if msgId == 10:

            # process message 10

            fragmentSize = msgLength - (15 * 4)

            robotSpeed, \
            robotX, \
            robotY, \
            robotZ, \
            robotH, \
            robotP, \
            robotR, \
            cameraX, \
            cameraY, \
            cameraZ, \
            cameraH, \
            cameraP, \
            cameraR, \
            flattenedFrame = \
                struct.unpack("!8x13f{0}s".format(fragmentSize), msg)

            #print("{0}, {1}, {2}, {3}".format(msgId, msgLength, 0, 0))

            state = 'loading'

        # If this is message 11....
        elif msgId == 11:

            if state == 'loading':

                # process message 11

                fragmentSize = msgLength - 16

                #print(len(msg), fragmentSize)

                fragmentNumber, \
                last, \
                fragment = \
                    struct.unpack("!8x2I{0}s".format(fragmentSize), msg)

                #print("{0}, {1}, {2}, {3}".format(
                #          msgId, msgLength, fragmentNumber, last))

                flattenedFrame += fragment

                if last == 1:
                    #print('show')
                    state = 'show'

    if state == 'show':

        try:
            #print('now')
            #print(type(flattenedFrame))
            #print(len(flattenedFrame))
            imgencode = pickle.loads(flattenedFrame)
            frame = cv2.imdecode(imgencode, 1)
            #print(type(frame))
            #print(frame)
            cv2.imshow("Frame", frame)
            cv2.waitKey(100)
        except Exception:
            None
        state = 'idle'

# from fps_testing
vs.stop()
