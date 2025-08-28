from picamera2 import Picamera2
import cv2
import numpy as np
import serial
import time

# IMPORTANT: For the actual run, please change the DRAW value to False
# True enables the display to show on screen and also display the contour borders
# False will disable the display so the cron will not fail looking for a display
DRAW = False
DEFAULT_SPEED = 150
DEFAULT_STEER = 90
STEER_ADJ = 25

# initializing constants for hsv
BLACK_UP = np.array([180, 255, 60])  # for walls
BLACK_LOW = np.array([0, 0, 0])
ORANGE_UP = np.array([22, 255, 255])  # for orange lines
ORANGE_LOW = np.array([8, 160, 40])
BLUE_UP = np.array([140, 250, 255])  # for blue lines
BLUE_LOW = np.array([90, 80, 40])

# initializing constants for coordinates of wall areas in the image
X1_1_PD = 770  # for walls
X2_1_PD = 799
X1_2_PD = 0
X2_2_PD = 30
Y1_PD = 240
Y2_PD = 600 #480

X1_LINE = 350  # for counting lines
X2_LINE = 450
Y1_LINE = 500
Y2_LINE = 600 #480

X1_CUB = 40  # for block detection
X2_CUB = 760
Y1_CUB = 300
Y2_CUB = 500 #400

# initializing constants of ratio for controllers
KP = 0.02 # the proportional gain, a tuning parameter for walls
KD = 0.02  # the derivative gain, a tuning parameter for walls

class Frames:  # clsss for areas on the picture
    def __init__(self, img, x_1, x_2, y_1, y_2, low, up):  # init gains coordinates of the area, and hsv boders
        self.x_1 = x_1  # initializing variables in class
        self.x_2 = x_2
        self.y_1 = y_1
        self.y_2 = y_2
        self.up = up
        self.low = low

        self.contours = 0
        self.frame = 0
        self.hsv = 0
        self.mask = 0
        self.frame_gaussed = 0

        self.update(img)

    def update(self, img):  # function for updating the image
        # getting the needed area on the image and outlining it
        cv2.rectangle(img, (self.x_1, self.y_1), (self.x_2, self.y_2), (150, 0, 50), 2)

        self.frame = img[self.y_1:self.y_2, self.x_1:self.x_2]
        self.frame_gaussed = cv2.GaussianBlur(self.frame, (1, 1), cv2.BORDER_DEFAULT)  # blurring the image

        self.hsv = cv2.cvtColor(self.frame_gaussed, cv2.COLOR_BGR2HSV)  # turning the image from bgr to hsv

    def find_contours(self, n=0, to_draw=True, color=(0, 0, 255), min_area=50, line_size=1):  # function for selecting
        # the contours, it gets, the needed borders of hsv, if the borders should be drawn, color of the outlining,
        # minimum area of the contour
        self.mask = cv2.inRange(self.hsv, self.low[n], self.up[n])  # getting the mask

        contours, _ = cv2.findContours(self.mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # getting contours
        r_contours = []
        for cntr in contours:  # outlining and selecting only big enough contours
            if cv2.contourArea(cntr) > min_area:
                r_contours.append(cntr)
                if to_draw:
                    cv2.drawContours(self.frame, cntr, -1, color, line_size)

        return r_contours  # returning contours

def pd():  # function of proportional–derivative controller for walls
    global pd_r, pd_l, KD, KP, err_old, timer_flag, time_turn, tim
    global flag_left, flag_right, time_green, time_red, steer # needed global variables for this function

    steer_adj = 0  # getting the addition to pd, to compensate the angle of the camera
    # ~ if direction == 'CW':
        # ~ steer_adj = 5
    # ~ if direction == 'CCW':
        # ~ steer_adj = 5

    # find all the black countours on the right of the car = area_1
    contours = pd_r.find_contours(to_draw=DRAW, color=(255, 255, 255))  # getting the contours for right area
    area_r = map(cv2.contourArea, contours)  # getting the area of the biggest contour`
    if contours:
        area_r = max(area_r)
    else:
        area_r = 0

    # find all the black countours on the left of the car = area_2
    contours = pd_l.find_contours(to_draw=DRAW, color=(255, 255, 255))  # same for 2_nd area
    area_l = map(cv2.contourArea, contours)
    if contours:
        area_l = max(area_l)
    else:
        area_l = 0
        
    # print(f"Area 1: {area_r} Area 2: {area_l} Difference: {area_l-area_r}")

    err = area_r - area_l  # counting the error and the final value of pd
    steer = int(err * KP + ((err - err_old) // 10 * KD + 90 + steer_adj))
    err_old = err

    if steer > 150:  # limiting the left turn of servo
        steer = 150
    if steer < 30:  # limiting the right turn for servo
        steer = 30        

    # ~ if area_r != 0 and area_l == 0:  # if there is no wall in one of ares, turning to the max to needed side
        # ~ flag_right = True  # changing the flag or turning
        # ~ if not timer_flag:  # resetting the timer of turning
            ### if time.time() - time_green < 0.2:  # if the turn, right after the inner sing, turn to the max
            # ~ if direction == 'CW':
                # ~ time_turn = time.time() - 2
            # ~ else:
                # ~ time_turn = time.time()
            # ~ timer_flag = True

        # ~ if time.time() - time_turn > 0.1:
            # ~ steer = 30
        # ~ else:
            # ~ steer = 50

    # ~ elif area_r != 0 and area_l == 0:  # same as the previous
        # ~ flag_left = True
        # ~ if not timer_flag:
            ### if time.time() - time_red < 0.2:
            # ~ if direction == 'CCW':
                # ~ time_turn = time.time() - 2
            # ~ else:
                # ~ time_turn = time.time()

            # ~ timer_flag = True

        # ~ if time.time() - time_turn > 0.1:
            # ~ steer = 150
        # ~ else:
            # ~ steer = 130

    # ~ elif area_r == 0 and area_l == 0:  # if there's no wall in any area, turn to the same side as before
        # ~ if flag_right:
            # ~ if time.time() - time_turn > 0.1:
                # ~ steer = 30
            # ~ else:
                # ~ steer = 50

        # ~ elif flag_left:
            # ~ if time.time() - time_turn > 0.1:
                # ~ steer = 150
            # ~ else:
                # ~ steer = 130

    # ~ else:  # else resetting the flags
        # ~ flag_left = False
        # ~ flag_right = False
        # ~ timer_flag = False


    return int(steer)  # returning controlling influence of pd

def restart():  # function for resetting all the variables
    global orange, blue, speed, steer, err_old, tim, time_orange, time_blue, stop_flag, time_turn, time_speed, time_stop
    global start_flag, stop_flag, pause_flag, flag_line_blue, flag_line_orange, direction, flag_left, flag_right, timer_flag

    orange = 0
    blue = 0

    steer = DEFAULT_STEER
    speed = 0
    err_old = 0

    tim = time.time()
    time_orange = time.time() - 5
    time_blue = time.time() - 5
    time_turn = time.time() - 5
    time_speed = time.time() + 10
    time_stop = time.time()

    timer_flag = False
    start_flag = False
    stop_flag = False
    pause_flag = False
    flag_left = False
    flag_right = False
    flag_line_orange = False
    flag_line_blue = False

    direction = ''

# Establish Serial connection to the Microbit over USB
ser = serial.Serial(
    port='/dev/ttyACM0',  # Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
    baudrate=115200,
    stopbits=serial.STOPBITS_ONE
)
ser.bytesize = serial.EIGHTBITS
ser.timeout  = 1

ser.reset_input_buffer()
ser.flushInput()
ser.flushOutput()

if not ser.isOpen():
    ser.open()
    print("***** Serial connection to Microbit Open *****")

# variables, for counting lines
orange = 0  
blue = 0

speed = 0
steer = DEFAULT_STEER  # variables for pd
err_old = 0

# initializing timers
tim = time.time()  # for finish
time_orange = time.time() - 5  # for counting orange lines
time_blue = time.time() - 5  # for counting blue lines
time_turn = time.time() - 5  # for turns
time_speed = time.time() + 10  # for slowing down at the start(optional)
time_stop = time.time()  # for stopping the robot

# variables for counting fps
time_fps = time.time()
fps = 0
fps_last = 0

# initializing flags
timer_flag = False  # for resetting other variables only once
start_flag = False
stop_flag = False  # for stopping the robot
pause_flag = False  # for pausing the robot
flag_left = False  # for tracking turns to the left
flag_right = False  # for tracking turns to the right
flag_line_orange = False  # for tracking orange lines
flag_line_blue = False  # for tracking blue lines

direction = ''  # direction variable

print("Heyyy....")

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (800,600)}))
picam2.start()
frame = picam2.capture_array("main")

# initializing objects for different areas
pd_r = Frames(frame, X1_1_PD, X2_1_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP])  # for the right wall
pd_l = Frames(frame, X1_2_PD, X2_2_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP])  # for the left wall
blue_line = Frames(frame, X1_LINE, X2_LINE, Y1_LINE, Y2_LINE, [BLUE_LOW], [BLUE_UP])  # for counting
orange_line = Frames(frame, X1_LINE, X2_LINE, Y1_LINE, Y2_LINE, [ORANGE_LOW], [ORANGE_UP])  # for counting lines

ser.write("ssssss\n".encode('utf-8')) # sending message to Microbit

while True:  # main loop

    # resetting controlling influence and speed
    # steer = DEFAULT_STEER
    fps += 1
   
    frame = picam2.capture_array("main")
    mb_msg = ser.read_all().decode("utf-8")
    if mb_msg == 'go':
        if start_flag:
            restart()
            ser.write("stoppp\n".encode('utf-8'))  # sending message to Microbit
        else:
            start_flag = True
            speed = DEFAULT_SPEED
            ser.write("startt\n".encode('utf-8'))  # sending message to Microbit

    if (start_flag):

        # ~ if time.time() - time_speed > 2:  # Slow speed until the first orange or blue line
            # ~ speed = DEFAULT_SPEED-50

        # if there is no sings, the robot will drive between walls
        pd_r.update(frame)  # updating wall areas
        pd_l.update(frame)
        steer = pd()  # counting controlling influence

        blue_line.update(frame)  # updating line-counting area
        contours_blue = blue_line.find_contours(0, DRAW, min_area=100, color=(250, 200, 0))  # getting blue and orange areas
        
        orange_line.update(frame)  # updating line-counting area
        contours_orange = orange_line.find_contours(0, DRAW, min_area=100, color=(0, 250, 250))

        if contours_blue:  # if there is blue contour, checking, if the line is new, and adding it
            contours_blue = max(contours_blue, key=cv2.contourArea)
            ar = cv2.contourArea(contours_blue)
            # this if condition is an overkill because we've already ensured the contours have a minimum area of 100 pixels
            if ar > 100:
                # ~ steer  = steer + STEER_ADJ
                # this condition checks if the blue flag is false which happens when there are NO blue lines
                # and if at least one second had passed since the last frame with a blue line was processed
                # if so, then it sets the blue line flag to true, so the condition is not met while subsequent frames
                # see the blue line. 
                if not flag_line_blue and time.time() - time_blue > 1:
                    if not direction:
                        direction = 'CCW'
                        # flag_left = True
                    blue += 1
                    print(f'orange: {orange} --- blue: {blue}')                     
                    if blue == 1 and orange == 0:
                        time_speed = time.time()
                    time_blue = time.time()  # resetting timer for blue lines
                    tim = time.time()  # resetting timer for stopping
                flag_line_blue = True
        else:
            flag_line_blue = False

        if contours_orange:  # same as for blue line
            contours_orange = max(contours_orange, key=cv2.contourArea)
            ar = cv2.contourArea(contours_orange)
            if ar > 100:
                # ~ steer = steer - STEER_ADJ
                if not flag_line_orange and time.time() - time_orange > 1:
                    if not direction:
                        direction = 'CW'
                        # flag_right = True
                    orange += 1
                    print(f'blue: {blue} --- orange: {orange}')
                    if orange == 1 and blue == 0:
                        time_speed = time.time()
                    time_orange = time.time()
                    tim = time.time()
                flag_line_orange = True
        else:
            flag_line_orange = False
            
        if (max(orange, blue) > 11 and time.time() - tim > 1.2) or stop_flag:  # checking if the robot must stop
            if not stop_flag:
                time_stop = time.time()
            if time.time() - time_stop < 0.3:  # braking for 0.3 seconds
                speed = -50
            else:  # stopping the robot
                speed = 0
            steer = DEFAULT_STEER
            mesg = str(steer + 100) + str(speed + 200) + '\n'  # forming the message for Microbit
            ser.write(mesg.encode('utf-8'))  # sending message to Microbit
            # print(mesg)
            stop_flag = True

        # ~ if (max(orange, blue) > 11):
            # ~ ser.write("s33333\n".encode('utf-8')) # sending message to Microbit
        # ~ elif (max(orange, blue) > 7):
            # ~ ser.write("s22222\n".encode('utf-8')) # sending message to Microbit
        # ~ elif (max(orange, blue) > 3):
            # ~ ser.write("s11111\n".encode('utf-8')) # sending message to Microbit                

        if pause_flag:  # checking if the robot is paused
            steer = DEFAULT_STEER
            speed = 0

        if time.time() - time_fps > 1:  # counting fps
            time_fps = time.time()
            fps_last = fps
            fps = 0

    if not stop_flag:  # checking if robot is not stopped/breaking
        frame = cv2.putText(frame, ' '.join([str(speed), str(steer), str(fps_last)]), (20, 30),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # printing parameters on the image
        mesg = str(steer + 100) + str(speed + 200) + '\n'  # sending message to Microbit
        # print(mesg)
        ser.write(mesg.encode('utf-8'))  # sending message to Microbit

    if mb_msg == 'quit':
        ser.write('190200\n'.encode('utf-8'))
        print("Ciao...")
        break       

    if DRAW:
        cv2.imshow("Video Frame", frame)

        key = cv2.waitKey(1) & 0xFF
            
        if key != -1:
            if key == ord('q'):
                ser.write('190200\n'.encode('utf-8'))
                print("Ciao...")
                break
            elif key == ord('p'):  # if s is clicked, pausing the robot
                pause_flag = True
            elif key == ord('g'):  # if g is clicked unpausing the robot
                pause_flag = False
            elif key == ord('r'):  # if r is clicked restarting the robot
                restart()

ser.close()
cv2.destroyAllWindows()
