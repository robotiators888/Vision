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
vs = WebcamVideoStream(src=1).start()

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

# sockets from which we expect to read
inputs = [ sock ]
# sockets to which we expect to write
outputs = [ ]
# outgoing message queues
message_queues = {}

# keep looping
while True:

    readable, writable, exceptional = select.select(inputs, outputs, inputs, 0.067)
    
    # get frame from camera frame queue
    frame = vs.read()
    
    for s in readable:
        if s is sock:
            connection, client_address = s.accept()
            connection.setblocking(0)
            inputs.append(connection)
        
            message_queues[connection] = Queue.Queue()
            
        else:
            data = s.recv(1024)


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
                if data.startswith("camera"):

                    # add new client to the address list.

                    print('received {0} bytes from {1}'.format(len(data), address))
                    print(data)
                    
                    message_queues[s].put(data)

                    # if new client add to address list
                    if address not in addressList:
                        addressList.append(address)

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),40]
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            # flatten image into single array
            #d = frame.flatten ()
            d = pickle.dumps(imgencode)
            #print(d)
            #print(type(d))
            #exit()
            dLen = len(d)
            #s = d.tostring ()
            #print('frame',frame)
            #print('flat',d)
            #exit(1)

            # start and stop indices of fragments
            start = 0
            stop  = maxFragmentSize

            # first message in message list
            msg = struct.pack("!2I13f{0}s".format(maxFragmentSize),
                          10, # message Id
                          (15 * 4) + maxFragmentSize, # message length
                          0.0, # robot speed
                          0.0, 0.0, 0.0, # robot position
                          0.0, 0.0, 0.0, # robot orientation
                          0.0, 0.0, 0.0, # camera position
                          0.0, 0.0, 0.0, # camera orientation
                          d[start:stop])

            #if address in addressList:
            #    print(dLen)
            

    #print('msgLength = ({0})'.format(len(msg)))
    # For each address in the address list...
    for address in addressList:

        # send the current message.
        sent = sock.sendto(msg, address)

    # initislize fragment counter to 1
    fragmentNumber = 1

    # increment start and stop to next frame interval
    start += maxFragmentSize
    stop = min(stop + maxFragmentSize, dLen)

    #if address in addressList:
    #    print(stop-start)

    # Loop once for each message fragment
    while start < dLen:

        #print(1 if stop >= dLen else 0, fragmentNumber, start,stop,stop - start, stop - start - 1)

        # Add another frame frament message to the message list
        msg = struct.pack("!4I{0}s".format(stop-start),
                          11, # message Id
                          16 + (stop - start), # message length
                          fragmentNumber,
                          1 if stop >= dLen else 0,
                          d[start:stop])

        # For each address in the address list...
        for address in addressList:

            # send the current message.
            sent = sock.sendto(msg, address)

        # increment the the frame counter
        fragmentNumber += 1

        # increment start and stop to next frame interval
        start += maxFragmentSize
        stop = min(stop + maxFragmentSize, dLen)



# from fps_testing
vs.stop()



