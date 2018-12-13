import socket
import sys
import io
import cv2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

HOST = "localhost"
PORT = 8888
address = (HOST, PORT)
message = "camera"

# send data
print >>sys.stderr, 'sending "%s"' % message
sent = sock.sendto(message, address)


try:
    while True:
        # receive response
        print >>sys.stderr, "waiting to receive"
        data, server = sock.recvfrom(4096)
        print >>sys.stderr, 'received "%s"' % data

    
        # show the frame to our screen
        # cv2.imshow("Frame", frame)
        # key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        #if key == ord("q"):
            #break
    
finally:
    print >>sys.stderr, "closing socket"
    sock.close()


