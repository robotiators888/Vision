#!/usr/bin/env python

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2
import imutils
from imutils.video import WebcamVideoStream

import socket
import sys
import time

# defines server address for raspberry pi
HOST = "0.0.0.0"
PORT = 5555
address = (HOST, PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(address)

# define the lower and upper boundaries of the yellow
# cube in the HSV color space, then initialize the
# list of tracked points
yellowLower = (0, 80, 120)
yellowUpper = (50, 201, 180)

# starts camera feed
camera = WebcamVideoStream(src=0).start()


# keep looping
while True:
	# grab the current frame
	frame = camera.read()
	

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, yellowLower, yellowUpper)
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
		c = max(cnts, key=cv2.contourArea)
		x, y, w, h = cv2.boundingRect(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if width > 10:
			# img, top left, bottom right, color, line thickness
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)


        # receive message from rio for vision data
        data, rioAddress = sock.recvfrom(4096)

        # send center point to rio through udp
        if data:
                print(data)
                print(address)
                sent = sock.sendto(center, rioAddress)
                
        
	# show the frame to our screen
	#cv2.imshow("Frame", frame)
	cv2.imshow("Frame", mask)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
