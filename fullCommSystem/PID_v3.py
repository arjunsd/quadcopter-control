import os     #importing os library so as to communicate with the system
import time   #importing time library to make Rpi wait because its too impatient 
os.system ("sudo pigpiod") #Launching GPIO library
time.sleep(1) # As i said it is too impatient and so if this delay is removed you will get an error
import pigpio #importing GPIO library
from numpy import absolute as abs
import numpy as np

# Instructions
# 1. Run python outline.py in terminal
# 2. Hit enter when prompted (4 times). Each esc should in order make a double beep sound and/or pulse. This means that they are armed.
# 3. After this the main code will run. All motors should move at the same time.

# Axes explanation
# We have three defined axes and angles.
# The first axis 'zz' goes through the middle of the drone in the normal direction (upwards).
# The angle about this axis is the 'yaw'. All motors effect yaw. 
# The second axis 'xx' goes through the 2nd and 4th motors and is parallel to the arms.
# The angle about this axis is the 'roll'. This means that only motors 1 and 3 affect 'roll'.
# The third axis 'yy' goes through the 1st and 3rd motors and is parallel to the arms (perpendicular to axis 'xx')
# The angle about this axis is the 'pitch'. This means only motors 2 and 4 affect 'pitch'.

# PID Explanation
# We have 3 types of error:
# 1. Regular error (roll_err, etc)
# 2. Previous Error (roll_prev_err, etc). This is exactly what it sounds like. We use it to determine how much the error has changed since
# the last time step. This is a rudimentary way to do Derivative controller. I'll probably imporve it if we have time.
# 3. Cummalitive error (roll_sum_err, etc). This adds up the cumalative error and allows us to do Integral Control.
# We have 3 gains
# Kp: proportional gain -> increasing this will increase how strong the response to an error is. Making this too high will lead to oscillations.
# Kd: derivative gain -> This should be lower than Kp
# Ki: integral gain -> This should be lower than Ki

pi = pigpio.pi(); #initializes object
# gpio numbers on Raspi for each esc, see picture I sent you on messenger
ESC1 = 4 
ESC2 = 17
ESC3 = 27
ESC4 = 22
pi.set_servo_pulsewidth(ESC1, 0)
pi.set_servo_pulsewidth(ESC2, 0)
pi.set_servo_pulsewidth(ESC3, 0)
pi.set_servo_pulsewidth(ESC4, 0)

max_inp = 2000 #max input - semi-arbitrary
min_inp = 700 #min input - semi-arbitrary
base_inp = 1200 # ideally find 'equillibrium' value to fight gravity

# start is our "main" function in a way. all the PID stuff goes on in the for loop
def start():
    ESC1 = 4
    ESC2 = 17
    ESC3 = 27
    ESC4 = 22
    
    # initialize error terms
    roll_prev_err = 0
    pitch_prev_err = 0
    yaw_prev_err = 0

    roll_sum_err = 0
    pitch_sum_err = 0
    yaw_sum_err = 0
    
    max_inp = 2000
    min_inp = 700
    base_inp = 1200
    
    # this ensures all of the motors will begin at our equilibrium value
    inp1 = base_inp
    inp2 = base_inp
    inp3 = base_inp
    inp4 = base_inp
    
    # PID gains. These will likely have to be tuned a bunch. I'd recommend starting with Kp when tuning. It can also be useful to initially set
    # Ki to zero while figuring approximate Kp and Kd out.
    Kp = 20
    Kd = 2
    Ki = 2
    
    # arm all of the motors, we should hear a double beep for each one and/or see each one move
    arm(ESC1)
    arm(ESC2)
    arm(ESC3)
    arm(ESC4)
    time.sleep(5) # have motors wait 5 seconds before they start going
    
    for i in range(0,4):
        pi.set_servo_pulsewidth(ESC1, base_inp)
        pi.set_servo_pulsewidth(ESC2, base_inp)
        pi.set_servo_pulsewidth(ESC3, base_inp)
        pi.set_servo_pulsewidth(ESC4, base_inp)

        #whatever the command is get vision or gyro data
        # in this case it is a predefined signal
        command = getCommand(i)
        
        # determine the error based off the command, this is just a dummy function for now
        roll_err = setError(command, 'roll')
        pitch_err = setError(command, 'pitch')
        yaw_err = setError(command, 'yaw')
        
        # calculation of total error with all gains
        tot_roll_err = Kp*roll_err+Kd*(roll_err-roll_prev_err)+Ki*roll_sum_err
        tot_pitch_err = Kp*pitch_err+Kd*(pitch_err-pitch_prev_err)+Ki*pitch_sum_err
        tot_yaw_err = Kp*yaw_err+Kd*(yaw_err-yaw_prev_err)+Ki*yaw_sum_err
        print("Roll is: %d" % roll_err + "| Pitch is: %d" % pitch_err + "| Yaw is: %d" % yaw_err)
        
        # this is based on drone dynamics and is not super accurate. I may adjust if we get other things working enough
        inp1 += tot_roll_err/2 + tot_yaw_err/4
        inp2 += tot_pitch_err/2 - tot_yaw_err/4
        inp3 += -tot_roll_err/2 + tot_yaw_err/4
        inp4 += -tot_pitch_err/2 - tot_yaw_err/4
        
        # saturation
        inp1 = min(max(inp1,min_inp),max_inp)
        inp2 = min(max(inp2,min_inp),max_inp)
        inp3 = min(max(inp3,min_inp),max_inp)
        inp4 = min(max(inp4,min_inp),max_inp)
        print("inp1: %d" % inp1 + "| inp2: %d" % inp2 + "| inp3: %d" % inp3 + "| inp4: %d" % inp4)
        
        # set next prev_err's
        roll_prev_err = roll_err
        pitch_prev_err = pitch_err
        yaw_prev_err = yaw_err
        
        # set next sum_err's
        roll_sum_err += roll_err
        pitch_sum_err += pitch_err
        yaw_sum_err += yaw_err
        print(i)
        # I have it pause so I can better analyze data as it happens. Obviously we'd get rid of this and instead wait for camera data
        time.sleep(5)

# dummy function
def setError(COMMAND, TYPE):
    out = 0
    if TYPE == 'roll':
        out = COMMAND*1
        return out
    elif TYPE == 'pitch':
        out = COMMAND*-1
        return out
    else:
        return out

# dummy function
def getCommand(index):
    store = [4,4,4,3,3,2,2,1,1,0,0,-1]
    return store[index]

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
#print('type arm, start, or stop, and then hit enter')
#inp = raw_input()
#if inp == "arm":
#    arm(ESC1)
#    arm(ESC2)
#    arm(ESC3)
#    arm(ESC4)
#elif inp == "start":
#    start()
#elif inp == "stop":

# sets all motors to zero before the code completes
pi.set_servo_pulsewidth(ESC1, 0)
pi.set_servo_pulsewidth(ESC2, 0)
pi.set_servo_pulsewidth(ESC3, 0)
pi.set_servo_pulsewidth(ESC4, 0)
pi.stop()


