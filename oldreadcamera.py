#!/usr/bin/env python

# import the necessary packages
from collections import deque
from imutils.video import WebcamVideoStream
import argparse
import imutils
import numpy as np
import argparse
import cv2
import socket
import sys
import time
import struct


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define frame fragment maximum send size
maxFragmentSize = 6100

# begins thread to read camera frames
vs = WebcamVideoStream(src=0).start()
	
# defines server address to work on all TCP stacks
HOST = "localhost"
PORT = 8888
address = (HOST, PORT)

# create a UDP socket endpoint
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print >>sys.stderr, 'starting up on %s port %s' % address

# attaches socket to server address
sock.bind(address)

# defines socket as non blocking
sock.setblocking(0)

# creates a list of addresses for those who want camera frames
addressList = [] 


# keep looping
while True:
	
	# get frame from camera frame queue
	frame = vs.read()
	
	print >>sys.stderr, '\nwaiting to receive message'
	
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
                
                # if new client add to address list
                if address not in addressList:
                    addressList.append(address)

        # flatten image into single array
        d = frame.flatten ()
        dLen = len(d)
        #s = d.tostring ()

        # start and stop indices of fragments
        start = 0
        stop  = maxFragmentSize + 1
           
        # first message in message list
        msgList = [ struct.pack("IIfffffffffffffI{0}I".format(maxFragmentSize),
                                10, # message Id
                                (15 * 4) + (4 * maxFragmentSize), # message length
                                0, # robot speec
                                0, 0, 0, # robot position
                                0, 0, 0, # robot orientation
                                0, 0, 0, # camera position
                                0, 0, 0, # camera orientation
                                *d[start:stop]) ]
        
        # initislize fragment counter to 1
        fragmentNumber = 1
        
        # increment start and stop to next frame interval
        start += maxFragmentSize
        stop = min(stop + maxFragmentSize, dLen + 1)
        
        # Loop once for each message fragment
        while start <= dLen:
            
            #print(1 if (stop == dLen) else 0, fragmentNumber, start,stop,stop - start, stop - start - 1)
            
            # Add another frame frament message to the message list
            msgList.append(struct.pack("IIII{0}I".format(stop-start),
                                       11, # message Id
                                       (4 * 4) + (4 * (stop-start)), # message length
                                       fragmentNumber,
                                       1 if (stop == dLen) else 0,
                                       *d[start:stop]))

            # increment the the frame counter
            fragmentNumber += 1
            
            # increment start and stop to next frame interval
            start += maxFragmentSize
            stop = min(stop + maxFragmentSize, dLen)
            

        # For each message in the message list...
        for msg in msgList:
            
            # send the message to each address in the address list.
            
            # For each address in the address list...
            for address in addressList:

                # send the current message.
                sent = sock.sendto(msg, address)   
 
# from fps_testing
vs.stop()
