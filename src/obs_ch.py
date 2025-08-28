# import RobotAPI as Rapi
import cv2
import numpy as np
import serial
import time
from picamera2 import Picamera2

# IMPORTANT: For the actual run, please change the DRAW value to False
# True enables the display to show on screen and also display the contour borders
# False will disable the display so the cron will not fail looking for a display
DRAW = False
DEFAULT_SPEED = 95
DEFAULT_STEER = 90
STEER_ADJ = 25

# initializing constants for hsv
BLACK_UP = np.array([180, 255, 60])  # for walls
BLACK_LOW = np.array([0, 0, 0])
ORANGE_UP = np.array([22, 255, 255])  # for orange lines
ORANGE_LOW = np.array([8, 160, 40])
BLUE_UP = np.array([140, 250, 255])  # for blue lines
BLUE_LOW = np.array([90, 80, 40])
GREEN_UP = np.array([75, 255, 255])  # for green blocks
GREEN_LOW = np.array([50, 110, 20])
RED_UP_1 = np.array([7, 255, 255])   # for red blocks
RED_LOW_1 = np.array([0, 128, 50])
RED_UP_2 = np.array([180, 255, 255])
RED_LOW_2 = np.array([170, 128, 50])

# initializing constants for coordinates of areas in the image
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
KP = 0.022  # the proportional gain, a tuning parameter for walls
KD = 0.02  # the derivative gain, a tuning parameter for walls
K_X = 0.025  # the proportional gain, a tuning parameter for blocks
K_Y = 0.03  # the derivative gain, a tuning parameter for blocks

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
        cv2.rectangle(img, (self.x_1, self.y_1), (self.x_2, self.y_2), (0, 255, 220), 1)

        self.frame = img[self.y_1:self.y_2, self.x_1:self.x_2]
        self.frame_gaussed = cv2.GaussianBlur(self.frame, (1, 1), cv2.BORDER_DEFAULT)  # blurring the image

        self.hsv = cv2.cvtColor(self.frame_gaussed, cv2.COLOR_BGR2HSV)  # turning the image from bgr to hsv

    def find_contours(self, n=0, to_draw=True, color=(0, 0, 255), min_area=50, red_dop=0):  # function for selecting
        # the contours, it gets, the needed borders of hsv, if the borders should be drawn, color of the outlining,
        # minimum area of the contour, and if it is used for red blocks
        self.mask = cv2.inRange(self.hsv, self.low[n], self.up[n])  # getting the mask
        if red_dop == 1:
            mask_1 = cv2.inRange(self.hsv, self.low[n + 1], self.up[n + 1])
            self.mask = cv2.bitwise_or(self.mask, mask_1)

        contours, _ = cv2.findContours(self.mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # getting contours
        r_contours = []
        for i in contours:  # outlining and selecting only big enough contours
            if cv2.contourArea(i) > min_area:
                r_contours.append(i)
                if to_draw:
                    cv2.drawContours(self.frame, i, -1, color, 2)

        return r_contours  # returning contours


def pd():  # function of proportional–derivative controller for walls
    global pd_r, pd_l, KD, KP, err_old, timer_flag, time_turn, tim
    global flag_left, flag_right, time_green, time_red, steer # needed global variables for this function

    steer_adj = 0  # getting the addition to pd, to compensate the angle of the camera
    if direction == 'CW':
        steer_adj = 5
    if direction == 'CCW':
        steer_adj = 5

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
        
    return(steer)

# ~ def pd():  # function of proportional–derivative controller for walls
    # ~ global pd_1, pd_2, KD, KP, err_old, timer_flag, time_turn, tim
    # ~ global flag_left, flag_right, time_green, time_red, steer, after_block  # needed global variables for this function

    # ~ steer_adj = 0  # getting the addition to pd, to compensate the angle of the camera
    # ~ if direction == 'CW':
        # ~ steer_adj  = -10
    # ~ if direction == 'CCW':
        # ~ steer_adj = -15

    # ~ contours = pd_r.find_contours(to_draw=DRAW, color=(255, 255, 255))  # getting the contours for 1_st area
    # ~ area_r = map(cv2.contourArea, contours)  # getting the area of the biggest contour
    # ~ if contours:
        # ~ area_r = max(area_r)
    # ~ else:
        # ~ area_r = 0

    # ~ contours = pd_l.find_contours(to_draw=DRAW, color=(255, 255, 255))  # same for 2_nd area
    # ~ area_l = map(cv2.contourArea, contours)
    # ~ if contours:
        # ~ area_l = max(area_l)
    # ~ else:
        # ~ area_l = 0

    # ~ err = area_r - area_l # counting the error and the final value of pd
    # ~ steer = int(err * KP + ((err - err_old) // 10) * KD + 90 + steer_adj)
    # ~ err_old = err

    # ~ if area_l != 0 and area_r == 0:  # if there is no wall in one of ares, turning to the max to needed side
        # ~ flag_right = True  # changing the flag or turning
        # ~ if not timer_flag:  # resetting the timer of turning
            # ~ if time.time() - time_green < 0.2:  # if the turn, right after the inner block, turn to the max
                # ~ after_block = True
                # ~ if direction == 'CW':
                    # ~ time_turn = time.time() - 5
            # ~ else:
                # ~ time_turn = time.time()
            # ~ timer_flag = True

        # ~ if time.time() - time_turn > 0.5:
            # ~ steer = 30

        # ~ else:
            # ~ steer = 55

    # ~ elif area_r != 0 and area_l == 0:  # same as the previous
        # ~ flag_left = True
        # ~ if not timer_flag:
            # ~ if time.time() - time_red < 0.2:
                # ~ after_block = True
                # ~ if direction == 'CCW':
                    # ~ time_turn = time.time() - 5
            # ~ else:
                # ~ time_turn = time.time()

            # ~ timer_flag = True

        # ~ if time.time() - time_turn > 0.5:
            # ~ steer = 150
        # ~ else:
            # ~ steer = 125

    # ~ elif area_r == 0 and area_l == 0:  # if there's no wall in any area, turn to the same side as before
        # ~ if flag_right:
            # ~ if time.time() - time_turn > 0.5:
                # ~ steer = 30
            # ~ else:
                # ~ steer = 55

        # ~ elif flag_left:
            # ~ if time.time() - time_turn > 0.5:
                # ~ steer = 150
            # ~ else:
                # ~ steer = 125

    # ~ else:  # else resetting the flags
        # ~ after_block = False
        # ~ flag_left = False
        # ~ flag_right = False
        # ~ timer_flag = False

    # ~ if steer > 150:  # limiting the turning of servo
        # ~ steer = 150
    # ~ elif steer < 30:  # limiting the max turning for servo
        # ~ steer = 30
        
    # ~ return steer  # returning controlling influence of pd


def pd_block(color):  # function of proportional–derivative controller for blocks
    global direction, K_X, K_Y, frame, time_red, time_green, block

    if color == 'green':  # getting the contours depending on the color
        countors = block.find_contours(to_draw=DRAW, color=(0, 255, 0), min_area=1000)
    elif color == 'red':
        countors = block.find_contours(1, DRAW, min_area=1000, red_dop=1)
    else:
        print('color erorr')
        return -1  # if the color is not right, return -1

    if countors:
        countors = max(countors, key=cv2.contourArea)  # if there is contours, getting the biggest of them
        x, y, w, h = cv2.boundingRect(countors)  # getting the coordinates of the contour
        x = (2 * x + w) // 2
        y = y + h

        if color == 'red':  # defining the needed coordinate, depending on the color
            time_red = time.time()
            x_tar = 0
        elif color == 'green':
            time_green = time.time()
            x_tar = block.x_2 - block.x_1
        else:
            print('color erorr')
            return -1

        e_x = round((x_tar - x) * K_X, 3)  # error for x coordinate
        e_y = round(y * K_Y, 3)  # error for y coordinate
        e_block = int(abs(e_y) + abs(e_x))  # getting the error for both coordinates

        if color == 'green':
            if direction == 'wise':
                e_block = int(e_block * -1.5)
            else:
                e_block = int(e_block * -1.8)
        if color == 'red':
            if direction == 'wise':
                e_block = int(e_block * 1.25)
        if color == 'green':  # printing the error on the image
            frame = cv2.putText(frame, str(e_block), (20, 60),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        else:
            frame = cv2.putText(frame, str(e_block), (20, 90),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        return e_block  # returning the erorr

    return -1  # if there's no blocks in the area, return -1


def restart():  # function for resetting all the variables
    global orange, blue, steer, err_old, tim, time_orange, time_blue, start_flag, stop_flag, time_turn, time_green, time_red, time_speed
    global pause_flag, flag_line_blue, flag_line_orange, direction, time_stop, flag_left, flag_right, timer_flag

    orange = 0
    blue = 0

    timer_flag = False

    steer = DEFAULT_STEER
    speed = 0
    err_old = 0

    tim = time.time()
    time_orange = time.time() - 5
    time_blue = time.time() - 5
    time_turn = time.time() - 5
    time_green = time.time() - 2
    time_red = time.time() - 2
    time_speed = time.time() + 200
    time_stop = time.time()

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

orange = 0  # variables, for counting lines
blue = 0

steer = DEFAULT_STEER  # variables for pd
err_old = 0
speed = 0

# initializing timers
tim = time.time()  # for finish
time_orange = time.time() - 5  # for counting orange lines
time_blue = time.time() - 5  # for counting blue lines
time_turn = time.time() - 5  # for turns
time_green = time.time() - 2  # for green blocks
time_red = time.time() - 2  # for red blocks
time_speed = time.time() + 200  # for slowing down at the start(optional)
time_stop = time.time()  # for stopping the robot

# initializing flags
timer_flag = False  # for resetting other variables only once
start_flag = False
stop_flag = False  # for stopping the robot
pause_flag = False  # for pausing the robot
flag_left = False  # for tracking turns to the left
flag_right = False  # for tracking turns to the right
flag_line_orange = False  # for tracking orange lines
flag_line_blue = False  # for tracking blue lines
after_block = False  # for tracking turns after blocks

direction = ''  # direction variable

print("Heyyy....")

cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (800,600)}))
picam2.start()

# robot = Rapi.RobotAPI(flag_serial=False)  # initializing object needed to manage the camera
# robot.set_camera(100, 640, 480)  # setting up the camera
# frame = robot.get_frame(wait_new_frame=1)
frame = picam2.capture_array("main")

if frame is None:
    print("No image captured - main")

# initializing objects for different areas
pd_r = Frames(frame, X1_1_PD, X2_1_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP])  # for the right wall
pd_l = Frames(frame, X1_2_PD, X2_2_PD, Y1_PD, Y2_PD, [BLACK_LOW], [BLACK_UP])  # for the left wall
line = Frames(frame, X1_LINE, X2_LINE, Y1_LINE, Y2_LINE, [BLUE_LOW, ORANGE_LOW], [BLUE_UP, ORANGE_UP])  # for counting
# lines
# for detection blocks
block = Frames(frame, X1_CUB, X2_CUB, Y1_CUB, Y2_CUB, [GREEN_LOW, RED_LOW_1, RED_LOW_2], [GREEN_UP, RED_UP_1, RED_UP_2])

# variables for counting fps
time_fps = time.time()
fps = 0
fps_last = 0

ser.write("ssssss\n".encode('utf-8')) # sending message to Microbit

while True:  # main loop
    # ~ if time.time() - time_speed > 3:  # checking of the speed raising
        # ~ speed_def = 35
    # ~ # resetting controlling influence and speed
    fps += 1
#    frame = robot.get_frame(wait_new_frame=1)  # getting image from camera

    frame = picam2.capture_array("main")
    if frame is None:
        print("No image captured")
        break

    mb_msg = ser.read_all().decode("utf-8")
    if mb_msg == 'go':
        if start_flag:
            restart()
            speed = 0
            ser.write("stoppp\n".encode('utf-8'))  # sending message to Microbit
        else:
            start_flag = True
            speed = DEFAULT_SPEED
            ser.write("startt\n".encode('utf-8'))  # sending message to Microbit    

    if (start_flag):
        block.update(frame)  # updating block area

        u_red = pd_block('red')  # getting controlling influence for red blocks
        u_green = pd_block('green')  # getting controlling influence for green blocks
        if u_green != -1 or u_red != -1:
            steer = 125 + max(u_green, u_red, key=abs)  # if there are blocks, counting final controlling influence

        # if there are no blocks, the robot will drive between walls
        else:
            pd_r.update(frame)  # updating wall areas
            pd_l.update(frame)
            steer = pd()  # counting controlling influence

        line.update(frame)  # updating line-counting area
        contours_blue = line.find_contours(0, DRAW, min_area=500)  # getting bue and orange areas
        contours_orange = line.find_contours(1, DRAW, min_area=500, color=(255, 255, 0))

        if contours_blue:  # if there is blue contour, checking, if the line is new, and adding it
            contours_blue = max(contours_blue, key=cv2.contourArea)
            ar = cv2.contourArea(contours_blue)
            if ar > 10:
                if not flag_line_blue and time.time() - time_blue > 1:
                    if not direction:
                        direction = 'CCW'
                    blue += 1
                    if blue == 1 and orange == 0:
                        time_speed = time.time()
                    print(f'blue: {blue} --- orange: {orange}')
                    time_blue = time.time()  # resetting timer for blue lines
                    tim = time.time()  # resetting timer for stopping
                flag_line_blue = True
        else:
            flag_line_blue = False

        if contours_orange:  # same as for blue line
            contours_orange = max(contours_orange, key=cv2.contourArea)
            ar = cv2.contourArea(contours_orange)
            if ar > 10:
                if not flag_line_orange and time.time() - time_orange > 1:
                    if not direction:
                        direction = 'CW'
                    orange += 1
                    if orange == 1 and blue == 0:
                        time_speed = time.time()
                    time_orange = time.time()
                    print(f'orange: {orange} --- blue: {blue}')
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
            steer = 90
            mesg = str(steer + 100) + str(speed + 200) + '\n'  # forming the message for pyboard
            # print(mesg)
            ser.write(mesg.encode('utf-8'))  # sending message to pyboard
            stop_flag = True

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
        mesg = str(steer + 100) + str(speed + 200) + '\n'  # sending message to pyboard
        # print(mesg)
        ser.write(mesg.encode('utf-8'))  # sending message to pyboard

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
