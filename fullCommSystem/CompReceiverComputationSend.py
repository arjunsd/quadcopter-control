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
from socket import *
import keyboard

UDP_HOST = "172.20.10.7"
UDP_SEND_IP  = "172.20.10.6"
UDP_PORT_VIDEO = 4096
UDP_PORT_INFO = 5005
UDP_PORT_MOTOR = 50005
buf = 1024
addr = (UDP_HOST, UDP_PORT_VIDEO)
fName = 'img.jpg'
timeOut = 0.05
#Motor info sent CC from back right
motorPWM = [0,0,0,0]
quitNum = 0





def checkQuit():
    #failsafe by pressing spacebar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        socksend = socket(AF_INET, # Internet
                     SOCK_DGRAM) # UDP
        socksend.sendto("0,0,0,0", (UDP_SEND_IP, UDP_PORT_MOTOR))
        socksend.sendto("0,0,0,0", (UDP_SEND_IP, UDP_PORT_MOTOR)) # redundancy
        cv2.destroyAllWindows()
        exit()

def video_reception():
    checkQuit()
    print("in video reception")
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(addr)
    data, address = s.recvfrom(buf)
    print("1")
    f = open(fName, 'wb')
    data, address = s.recvfrom(buf)
    try:
        while(data):
            f.write(data)
            s.settimeout(timeOut)
            data, address = s.recvfrom(buf)
    except timeout:
        f.close()
        s.close()
    image = cv2.imread(fName)
    cv2.imshow('recv', image)

def infoReception():
    checkQuit()
    sock = socket(AF_INET, SOCK_DGRAM) # UDP
    sock.bind((UDP_HOST, UDP_PORT_INFO ))
    data, temp_addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", data

def cvComputationOnData():
    checkQuit()
    #Still need to implement
    #update motor pwm

def sendMotorCoordinates():
    checkQuit()
    quitNum = 0
    print("did you get here")
    #Put default values... CHANGEEEEEEEE
    motorPWM = [1200,1200,1200,1200]
    socksend = socket(AF_INET, SOCK_DGRAM) # UDP
    comma = ","
    if keyboard.is_pressed("q"):
        quitNum = 1
    socksend.sendto(str(quitNum)+ comma + str(motorPWM[0]) + comma + str(motorPWM[1]) + comma + str(motorPWM[2]) + comma + str(motorPWM[3]), (UDP_SEND_IP, UDP_PORT_MOTOR))

def foo():
    print("starting receiver")
    while True:

        video_reception()

        infoReception()

        cvComputationOnData()

        sendMotorCoordinates()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    foo()
    cv2.destroyAllWindows()
