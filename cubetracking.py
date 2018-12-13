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

help()

# defines server address for raspberry pi
HOST = "0.0.0.0"
PORT = 5555
address = (HOST, PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(address)

inputs = [sock]
outputs = []

# define the lower and upper boundaries of the yellow
# cube in the HSV color space, then initialize the
# list of tracked points
yellowLower = (0, 80, 120)
yellowUpper = (50, 201, 180)

# starts camera feed
camera = WebcamVideoStream(src=0).start()

# camera calibration
pixelHeight = 480
pixelWidth = 640

#actualHeight = 
#actualWidth =


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
		((a, b), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		pixelX = int(M["m10"] / M["m00"])
                pixelY = int(M["m01"] / M["m00"])

                # finding the extreme values
                extLeft = tuple(c[c[:, :, 0].argmin()][0])
                extRight = tuple(c[c[:, :, 0].argmax()][0])
                extTop = tuple(c[c[:, :, 1].argmin()][0])
                extBot = tuple(c[c[:, :, 1].argmax()][0])

                #approx = cv2.approxPolyDP(c,0.01*cv2.arcLength(c,True),True)
                #print len(approx)

                #fieldY = ((480-pixelY)/pixelHeight)(actualHeight)
                #print fieldY

        
		# only proceed if the radius meets a minimum size
		if radius > 50:
		    # img, top left, bottom right, color, line thickness
		    cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 255), 2)
		    cv2.circle(frame, (int(a), int(b)), int(radius), (0, 255, 255), 2)
			
		    cv2.circle(frame, center, 5, (0, 255, 255), -1)  #yellow center point
		    cv2.circle(frame, extLeft, 5, (0, 0, 255), -1)  #red left point
		    cv2.circle(frame, extRight, 5, (0, 255, 0), -1)  #green right point
		    cv2.circle(frame, extTop, 5, (255, 0, 0), -1)  #blue top point
		    cv2.circle(frame, extBot, 5, (255, 255, 0), -1)  #teal bottom point
			
		    #cv2.drawContours(frame, cnts, -1, (0,255,0), 3)

		    #if msg.startsWith("cube"):
                        #sock.sendto(center, address)
                        
                
        
	# show the frame to our screen
	#cv2.imshow("Frame", frame)
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
cv2.destroyAllWindows()
