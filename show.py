#!/usr/bin/env python

# import the necessary packages
import argparse

try:
    import cPickle as pickle
except:
    import pickle

import cv2
import socket
import sys
import struct

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())


# define the lower and upper boundaries of the "yellow"
# cube in the HSV color space, then initialize the
# list of tracked points
yellowLower = (23, 155, 110)
yellowUpper = (30, 217, 221)

# define frame fragment maximum send size
maxFragmentSize = 61440

# defines server address to work on all TCP stacks
HOST    = "0.0.0.0"
PORT    = 9999
ADDRESS = (HOST, PORT)

# defines camera frame provider address
cameraHost    = "127.0.0.1"
cameraPort    = 8888
cameraAddress = (cameraHost, cameraPort)

# create a UDP socket endpoint
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# attaches socket to server address
sock.bind(ADDRESS)

# defines socket as non blocking
#sock.setblocking(0)

sock.sendto("camera", cameraAddress)

state = 'idle'

# keep looping
while True:

    # try to catch all exceptions from socket reads
    #try:

    # attempt to read message from socket
    #msg, address = sock.recvfrom(65507)
    msg, address = sock.recvfrom(65536)

    #except Exception:

    #    # set received fields to none when exception received
    #    # (an exception is generated each time one attempts to read from a socket and nothing is there)
    #    msg = None
    #    address = None

    # if a message was received...
    if len(msg) >= 8:

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

    #    sent = sock.sendto(msg, address)

    #print(msg)
    continue

    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:

        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        # c = max(cnts, key=cv2.contourArea)
        for c in cnts:

            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 20:

                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.rectangle(frame,
                              (int(x) - int(radius),
                              int(y) - int(radius)),
                              (int(x) + int(radius),
                              int(y) + int(radius)),
                              (0, 255, 255), 2)
                #cv2.rectangle(frame, center, 5, (0, 0, 255), -1)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break


# cleanup the camera and close any open windows
# camera.release()
cv2.destroyAllWindows()

# from fps_testing
vs.stop()
