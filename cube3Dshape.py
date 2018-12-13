import cv2
# Importing the Opencv Library
import numpy as np
# Importing NumPy,which is the fundamental package for scientific computing with #Python
from imutils.video import WebcamVideoStream


camera = WebcamVideoStream(src=0).start()

while True:
    
    img = camera.read()

    # RGB to Gray scale conversion
    img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)

    # Noise removal with iterative bilateral filter(removes noise while preserving edges)
    noise_removal = cv2.bilateralFilter(img_gray,9,75,75)

    # Thresholding the image
    ret,thresh_image = cv2.threshold(noise_removal,0,255,cv2.THRESH_OTSU)

    # Applying Canny Edge detection
    canny_image = cv2.Canny(thresh_image,250,255)
    canny_image = cv2.convertScaleAbs(canny_image)

    # dilation to strengthen the edges
    kernel = np.ones((3,3), np.uint8)
    # Creating the kernel for dilation
    dilated_image = cv2.dilate(canny_image,kernel,iterations=1)

    contours = cv2.findContours(dilated_image.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
    contours= sorted(contours, key = cv2.contourArea, reverse = True)[:1]
    pt = (180, 3 * img.shape[0] // 4)

    if len(contours) > 0:
        cnt = max(contours, key=cv2.contourArea)
        approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
        print len(approx)
        if len(approx) ==6 :
            print "Cube"
            cv2.drawContours(img,[cnt],-1,(255,0,0),3)
            cv2.putText(img,'Cube', pt ,cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2, [0,255, 255], 2)
        elif len(approx) == 7:
            print "Cube"
            cv2.drawContours(img,[cnt],-1,(255,0,0),3)
            cv2.putText(img,'Cube', pt ,cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2, [0, 255, 255], 2)


    corners    = cv2.goodFeaturesToTrack(thresh_image,6,0.06,25)
    corners    = np.float32(corners)
    
    for    item in    corners:
        x,y    = item[0]
        cv2.circle(img,(x,y),10,255,-1)


    # show the frame to our screen
    #cv2.imshow("Frame", frame)
    cv2.imshow("Frame", img)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
	    break


cv2.waitKey()
