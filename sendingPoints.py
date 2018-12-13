from collections import deque
import numpy as np
import argparse
import cv2
import imutils
from imutils.video import WebcamVideoStream
import socket

# defines udp server address for jetson
HOST = "0.0.0.0"
PORT = 5806

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

camera = WebcamVideoStream(src=0).start()

message = None

# keep looping until a message is received from the rio
while(message = None):
    try:
        message, rioAddress = sock.recvfrom(65507)
        print data
        print address

    except Exception:
        message = None
        address = None

frame = camera.read()

x = None
y = None

sock.sendto((x, y), rioAddress)

    
