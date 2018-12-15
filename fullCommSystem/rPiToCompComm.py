#!/usr/bin/env python
"""Webcam video streaming



Using OpenCV to capture frames from webcam.
Compress each frame to jpeg and save it.
Using socket to read from the jpg and send
it to remote address.
!!!press q to quit!!!
"""
import numpy as np
import cv2
from socket

cap = cv2.VideoCapture(0)

MESSAGE = "5,6,7"
#implement receiving messages from the NAze most importantly Attitude and IMU data to send back to the computer


#Ratio of actual FPS speed to wanted FPS speed
ratio = 10
    
#Put the RECEIVING IP Adddress
UDP_IP_RECEIVE = "10.142.36.101"
UDP_PORT_VIDEO = 4096
UDP_PORT_INFO = 5005
addr = (UDP_IP_RECEIVE, UDP_PORT_VIDEO)
buf = 1024

def sendFile(fName):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(fName, addr)
    f = open(fName, "rb")
    data = f.read(buf)
    while data:
        if(s.sendto(data, addr)):
            data = f.read(buf)
    f.close()
    s.close()

def captureFunc():
    count = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            cv2.imshow('frame', frame)
            count = count + 1
            if count == ratio:
                cv2.imwrite("img.jpg", frame)
                sendFile("img.jpg")
                count = 0            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            print "sending message:", MESSAGE
            sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
            sock.sendto(MESSAGE, (UDP_IP_RECEIVE, UDP_PORT_INFO))
        else:
            break

if __name__ == '__main__':
    # captureFunc()
    # cap.release()
    # cv2.destroyAllWindows()
    main()
