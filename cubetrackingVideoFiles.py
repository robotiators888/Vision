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
import select

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the yellow
# cube in the HSV color space, then initialize the
# list of tracked points
yellowLower = (5, 25, 130)
yellowUpper = (60, 220, 320)

highestY = 0
farLeft = 600
farRight = 0


camera = cv2.VideoCapture(args["video"])


# keep looping
while True:
        
	# grab the current frame
	(grabbed, frame) = camera.read()

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if not grabbed:
                print('ERROR:not grabbed')
		continue
	
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "yellow", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, yellowLower, yellowUpper)
	mask = cv2.erode(mask, None, iterations=3)
	mask = cv2.dilate(mask, None, iterations=3)
	cv2.imshow("mask", mask)


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

		extBot = tuple(c[c[:, :, 1].argmax()][0])
			
		cv2.drawContours(frame, c, -1, (0,255,0), 3)

		for point in c:
                        for i in point:
                                x = i[0]
                                y = i[1]

                                if highestY < y:
                                        highestY = y
                        for i in point:
                                if x < farLeft:
                                        farLeft = x
                                if x > farRight:
                                        farRight = x
                                #print "far left " + str(farLeft)
                                #print "far right " + str(farRight)

                targetX = (farLeft + farRight) / 2
                print targetX

                                
                
	# show the frame to our screen
	#cv2.imshow("Frame", frame)
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
cv2.destroyAllWindows()
