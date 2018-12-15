import os     #importing os library so as to communicate with the system
import time   #importing time library to make Rpi wait because its too impatient 
os.system ("sudo pigpiod") #Launching GPIO library
time.sleep(1) # As i said it is too impatient and so if this delay is removed you will get an error
import pigpio #importing GPIO library
from numpy import absolute as abs
import numpy as np
import socket
import cv2



pi = pigpio.pi(); #initializes object
# gpio numbers on Raspi for each esc, see picture I sent you on messenger
command = [1000,1000,1000,1000]
UDP_IP = "127.0.0.1"
UDP_PORT = 6000

sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

ESC = [4,17,27,22]
for i in range(0,4):
    pi.set_servo_pulsewidth(ESC[i], 0)

max_inp = 2000 #max input - semi-arbitrary
min_inp = 1000 #min input - semi-arbitrary
base_inp = 1200 # ideally find 'equillibrium' value to fight gravity

# start is our "main" function in a way. all the PID stuff goes on in the for loop
def start():
    
    
    max_inp = 1600
    min_inp = 1200
    
    
    # arm all of the motors, we should hear a double beep for each one and/or see each one move
    arm(ESC1)
    arm(ESC2)
    arm(ESC3)
    arm(ESC4)
    time.sleep(5) # have motors wait 5 seconds before they start going
    
    while true:
        command = getCommandFromUDP()
        if (command = [0,0,0,0]):
            for i in range(0,4):
                pi.set_servo_pulsewidth(ESC[i], command[i])
            print "quit program"
            exit()

        for i in range(0,4):
            pi.set_servo_pulsewidth(ESC[i], min(command[i], max_inp))




def getCommandFromUDP():
    #This function is to retrieve motor PWM vlaues from UDP


    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", data

    command_list = data.split(",")
    data = map(int, data)
    print "parsed:", data
    return data


#This is the arming procedure of an ESC. I don't fully understand it, but whatever
def arm(ESC): 
    print "Connect the battery and press Enter"
    inp = raw_input()    
    if inp == '':
        pi.set_servo_pulsewidth(ESC, 0)
        time.sleep(1)
        pi.set_servo_pulsewidth(ESC, 2000)
        time.sleep(1)
        pi.set_servo_pulsewidth(ESC, 700)
        time.sleep(1)

start()


# sets all motors to zero before the code completes
pi.set_servo_pulsewidth(ESC1, 0)
pi.set_servo_pulsewidth(ESC2, 0)
pi.set_servo_pulsewidth(ESC3, 0)
pi.set_servo_pulsewidth(ESC4, 0)
pi.stop()


