import cv2
import numpy as np
import RPi.GPIO as GPIO
import serial
import time
from picamera2 import Picamera2
import time
# ~ import board
import busio
import adafruit_vl53l0x

# IMPORTANT: For the actual run, please change the DRAW value to False
# True enables the display to show on screen and also display the contour borders
# False will disable the display so the cron will not fail looking for a display
DRAW = True

# Change this to False for the open run
# Change to true if the car needs to park at the end of run
PARKING = True

# Configure GPIO Pins
PWM_PIN = 10
FG_PIN = 8
DIR_PIN = 12

DEFAULT_SPEED = 100 # Speed for all sections other than walls - (for new motor 0 is full speed, 100 is stop)
# ~ DEFAULT_WALL_SPEED = 0 # Speed for wall PD code only - 0 for OPEN round, 0 for OBSTACLE round
PARK_SPEED = 100 # Speed at which the robot will attempt to park
STOP_SPEED = 100 # Stop the robot
DEFAULT_STEER = 90 # 90 for straight driving
MAX_R_STEER = 15 # 15 is maximum right steer
MAX_L_STEER = 165 # 165 is maximum left steer
DEF_LINE_COUNT = 1 # 12 to count the sections crossed based on the lines. Change to lower to test just one section

# initializing constants of ratio for controllers
KP = 0.017 # OG - 0.025, 0.25 the proportional gain, a tuning parameter for walls
KD = 0.1 # 0.1 the derivative gain, a tuning parameter for walls
dT = 40 # 40 in milliseconds. This is the time step for each frame processing based on measured value of average 25 frames per second
K_X = 0.11 # 0.16 the proportional gain, a tuning parameter for X coordinate of the blocks
K_Y = 0.08 # 0.12 the proportional gain, a tuning parameter for Y coordinate of the blocks

# initializing constants for hsv
BLACK_UP = np.array([180, 255, 50])  # for walls
BLACK_LOW = np.array([0, 0, 0])    # S = 0
ORANGE_UP = np.array([22, 255, 255])  # for orange lines
ORANGE_LOW = np.array([4, 160, 40])
BLUE_UP = np.array([150, 255, 255])  # for blue lines
BLUE_LOW = np.array([90, 75, 70])
GREEN_UP = np.array([85, 255, 255])  # for green blocks
GREEN_LOW = np.array([40, 50, 50])  # S = 50
RED_UP_1 = np.array([2, 255, 255])   # for red blocks
RED_LOW_1 = np.array([0, 128, 50])
RED_UP_2 = np.array([180, 255, 255])
RED_LOW_2 = np.array([170, 128, 50])
MGNTA_UP = np.array([168, 255, 255]) # for magenta parking blocks
MGNTA_LOW = np.array([155, 100, 50])

# initializing constants for coordinates of areas in the image - 640 x 480
X1_1_PD = 610  # for walls
X2_1_PD = 640
X1_2_PD = 0
X2_2_PD = 30
Y1_PD = 200 #200
Y2_PD = 480

X1_LINE = 280  # for counting lines
X2_LINE = 360
Y1_LINE = 400
Y2_LINE = 480

X1_BLOCK = 40  # for block detection
X2_BLOCK = 600
Y1_BLOCK = 180 #160
Y2_BLOCK = 440

X1_1_PARK = 320  # for walls
X2_1_PARK = 600
X1_2_PARK = 40
X2_2_PARK = 320
Y1_PARK = 240 #200
Y2_PARK = 430

Y1_PARK_STOP = 430
Y2_PARK_STOP = 480

Y1_STOP = 380
Y2_STOP = 440
BLACK = False

class Frames:  # class for areas on the picture
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
    
    # Returns all the contours of specific colors provided in the input
    # Parameter inputs: n = Required borders of hsv (based on the order of color supplied to the frame), 
    # to_draw = if the borders should be drawn; color = color of the contour outline,
    # min_area = minimum area of the contour, and is_red = whether it is used for red blocks
    def find_contours(self, n=0, to_draw=True, color=(255, 255, 255), min_area=50, is_red=False):
        
        self.mask = cv2.inRange(self.hsv, self.low[n], self.up[n])  # getting the mask
        
        if is_red:
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

    # function for selecting
    # the contours, it gets, the needed borders of hsv, if the borders should be drawn, color of the outlining,
    # minimum area of the contour, and if it is used for red blocks
    def find_all_contours(self, to_draw=True, color=(255, 255, 255), min_area=50):  

        for n in range(len(self.low)):
            print("Contour Upper ", self.up[n])
            self.mask = cv2.bitwise_or(self.mask, cv2.inRange(self.hsv, self.low[n], self.up[n]))

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
    global time_green, time_red, direction, steer # needed global variables for this function

    # find all the black countours on the right wall
    contours = pd_r.find_contours(0, to_draw=DRAW, color=(255, 255, 255))  # getting the contours for right area
    area_r = map(cv2.contourArea, contours)  # getting the area of the biggest contour`
    if contours:
        area_r = max(area_r)
    else:
        area_r = 0

    # find all the black countours on the left wall
    contours = pd_l.find_contours(0, to_draw=DRAW, color=(255, 255, 255))  # same for left area
    area_l = map(cv2.contourArea, contours)
    if contours:
        area_l = max(area_l)
    else:
        area_l = 0

    # ~ print(f"WALL --- Right: {area_r} Left: {area_l} Difference: {area_l-area_r}")
    
    if (direction == 'CCW'):
        if (time.time() - time_red < 0.4):
            area_r += 500 # SHADYA: This was originally 3500 so we could avoid a specific situation. But this causes problems in other situations. 
        elif (time.time() - time_green < 1.3 and area_l < 500):
            area_r += 1000
        elif (area_l < 200 and area_r < 800):
            area_r += 1500           
    elif (direction == 'CW'):
        if (time.time() - time_green < 0.4):
            area_l += 500 # SHADYA: This was originally 3500 so we could avoid a specific situation. But this causes problems in other situations. 
        elif (time.time() - time_red > 0.8 and time.time() - time_red < 1.3 and area_r < 500):
            area_l += 1000
        elif (area_r < 200 and area_l < 800):
            area_l += 1500

    err = area_r - area_l # counting the error and the final value of pd
    steer = DEFAULT_STEER + int(err * KP + ((err - err_old) // dT * KD))
    err_old = err

    if steer > MAX_L_STEER:  # limiting the left turn of servo
        steer = MAX_L_STEER
    if steer < MAX_R_STEER:  # limiting the right turn for servo
        steer = MAX_R_STEER    
    
    # ~ print (f'Steer: {steer}')
    return(steer)

def pd_align():  # function of proportional–derivative controller for walls
    global pd_r, pd_l, KD, KP, err_old, timer_flag, time_turn, tim
    global time_green, time_red, direction, steer # needed global variables for this function
    
    if (direction == 'CCW'):
        # find all the black countours on the right wall
        tgt_r = 3450
        
        contours = pd_r.find_contours(0, to_draw=DRAW, color=(255, 255, 255))  # getting the contours for right area
        area_r = map(cv2.contourArea, contours)  # getting the area of the biggest contour`
        if contours:
            area_r = max(area_r)
        else:
            area_r = 0
        
        err = tgt_r - area_r # counting the error and the final value of pd
        print(f"WALL --- Right: {area_r} Error: {err}")

    elif (direction == 'CW'):
        tgt_l = 3450
        
         # find all the black countours on the left wall
        contours = pd_l.find_contours(0, to_draw=DRAW, color=(255, 255, 255))  # same for left area
        area_l = map(cv2.contourArea, contours)
        if contours:
            area_l = max(area_l)
        else:
            area_l = 0
        
        err = tgt_l - area_l # counting the error and the final value of pd
        print(f"WALL --- Left: {area_l} Error: {err}")
        
    else:
        err = 0

    steer = DEFAULT_STEER + int(err * KP + ((err - err_old) // dT * KD))
    err_old = err

    if steer > MAX_L_STEER:  # limiting the left turn of servo
        steer = MAX_L_STEER
    if steer < MAX_R_STEER:  # limiting the right turn for servo
        steer = MAX_R_STEER    
    
    # ~ print (f'Steer: {steer}')
    return(steer)

def pd_park():  # function of proportional–derivative controller for parking between the magenta blocks
    global park_r, park_l, KD, KP, err_old, timer_flag, time_turn, tim
    global direction, steer # needed global variables for this function

    # find all the magenta countours on the right parking block
    contours = park_r.find_contours(to_draw=DRAW, color=(255, 255, 255))  # getting the contours for right area
    area_r = map(cv2.contourArea, contours)  # getting the area of the biggest contour`
    if contours:
        area_r = max(area_r)
    else:
        area_r = 0

    # find all the magenta countours on the left parking block
    contours = park_l.find_contours(to_draw=DRAW, color=(255, 255, 255))  # same for left area
    area_l = map(cv2.contourArea, contours)
    if contours:
        area_l = max(area_l)
    else:
        area_l = 0

    # ~ print(f"PARKING --- Right: {area_r} Left: {area_l} Difference: {area_l-area_r}")

    err = area_r - area_l # counting the error and the final value of pd
    steer = DEFAULT_STEER + int(err * 0.005 + ((err - err_old) // dT * 0.02))
    err_old = err

    if steer > MAX_L_STEER:  # limiting the left turn of servo
        steer = MAX_L_STEER
    if steer < MAX_R_STEER:  # limiting the right turn for servo
        steer = MAX_R_STEER    
    
    # ~ print (f'Steer: {steer}')
    return(steer)

def pd_block(color):  # function of proportional controller for color blocks
    global direction, K_X, K_Y, frame, time_red, time_green, block

    if color == 'green':  # getting the contours depending on the color
        countors = block.find_contours(to_draw=DRAW, color=(0, 255, 0), min_area=600)
    elif color == 'red':
        countors = block.find_contours(1, to_draw=DRAW, color=(255, 0, 0), min_area=600, is_red=True)
    else:
        print('color error')
        return -1  # if the color is not right, return -1

    if countors:
        countors = max(countors, key=cv2.contourArea)  # if there is contours, getting the biggest of them
        x, y, w, h = cv2.boundingRect(countors)  # getting the coordinates of the contour
        x_ctr = x + w // 2 
        y_btm = y + h

        # If the color is green, the target X coordinate should be to the left edge of the rectangle
        if color == 'green':
            time_green = time.time()
            x_tgt = block.x_2 - block.x_1 # This represents the right edge of the rectangle - X coordinate would be 560 (as measured by X2 being 600 - X1 being 40)
        elif color == 'red':  # If the color is red, the target X coordinate should be to the right edge of the rectangle
            time_red = time.time()
            x_tgt = 0 # This represents the left edge of the rectangle - X coordinate would be 0

        err_x = round((x_tgt - x_ctr) * K_X, 3)  # error for x coordinate
        if color == 'green': # error for y coordinate
            err_y = round((y_btm - 100) * K_Y, 3)
        elif color == 'red':
            err_y = round((100 - y_btm) * K_Y, 3)
        err_block = int(err_y + err_x)  # getting the error for both coordinates
                
        # ~ print(f'color: {color}, x: {x}, y: {y}, w: {w}, h: {h}, x_tgt: {x_tgt}, x_ctr: {x_ctr}, y_btm: {y_btm}, err_x: {err_x}, err_y: {err_y}, err_block: {err_block}')
        if color == 'green':  # printing the error on the image
            frame = cv2.putText(frame, str(err_block), (20, 60),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        else:
            frame = cv2.putText(frame, str(err_block), (500, 60),
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        return err_block  # returning the error

    return -1  # if there's no blocks in the area, return -1

# Function to mimic Arduino's pulseIn
def pulseIn(pin, level, timeout):
    start_time = time.time()
    
    # Wait for pin to go to the desired level
    while GPIO.input(pin) != level:
        if (time.time() - start_time) > timeout:
            return 0
    
    t1 = time.time()
    
    # Wait for pin to change from the desired level
    while GPIO.input(pin) == level:
        if (time.time() - t1) > timeout:
            return 0
    
    t2 = time.time()
    
    return (t2 - t1) * 1000000  # return in microseconds
    
    
def getRpm():
    i = 0
    rpm = 0
    # Measure pulse input 8 times and average
    for j in range(8):
        i += pulseIn(FG_PIN, GPIO.HIGH, 0.5)  # 500ms timeout

    i = i/8  # divide by 8 (average)
    if i > 0:
        rpm = 111111 / i  # speed r/min (60 sec * 1000000 microsec / (45 Gear Ratio * 6 Pulse Freq * 2 pulses * i measured pulse))

    return round(rpm, 1)


def maintainRpm(target_rpm):
    # ~ current_rpm = 0

    #KP Value
    kp = 1.3
    pulse_width = 99
    # ~ kd = 0.3
    pwm.ChangeDutyCycle(pulse_width)
    time.sleep(0.5)
    
    for _ in range(10):
        current_rpm = getRpm()
        if current_rpm > 130:
            print(f'{current_rpm} too high')
            current_rpm = 0
            break
        err = round(target_rpm - current_rpm, 1)
        p = round(err * kp, 1)
        pulse_width = pulse_width - p
        print(f"Target: {target_rpm}rpm  Current: {current_rpm}rpm  Error: {err}  P: {p} Duty Cycle: {pulse_width}%")
        if (pulse_width > 100):
            pulse_width = 100
        elif (pulse_width < 0):
            pulse_width = 0
        pwm.ChangeDutyCycle(pulse_width)
        time.sleep(0.5)


def restart():  # function for resetting all the variables
    global orange, blue, steer, park_step, err_old, tim, time_orange, time_blue, time_turn, time_green, time_red, time_speed, time_extra_turn, time_stop
    global stop_flag, restart_flag, pause_flag, reverse_flag, turn_flag, park_flag, has_blocks, flag_line_blue, flag_line_orange, direction, timer_flag, extra_turn, line_count

    orange = 0
    blue = 0

    timer_flag = False

    steer = DEFAULT_STEER
    speed = DEFAULT_SPEED
    line_count = DEF_LINE_COUNT
    park_step = 0
    err_old = 0

    tim = time.time()
    time_orange = time.time() - 5
    time_blue = time.time() - 5
    time_turn = time.time() - 5
    time_green = time.time() - 2
    time_red = time.time() - 2
    time_speed = time.time() + 200
    time_stop = time.time()

    stop_flag = True
    restart_flag = False
    reverse_flag = False
    turn_flag = False
    pause_flag = False
    flag_line_orange = False
    flag_line_blue = False
    has_blocks = False

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

GPIO.setmode(GPIO.BOARD)  # or GPIO.BCM depending on your wiring
GPIO.setup(11, GPIO.OUT)  # PWM pin
GPIO.setup(13, GPIO.OUT)  # direction control pin
GPIO.setup(15, GPIO.IN)   # Encoder Frequency Generator signal input pin

orange = 0  # variables, for counting lines
blue = 0

steer = DEFAULT_STEER
speed = DEFAULT_SPEED
line_count = DEF_LINE_COUNT
park_step = 0
err_old = 0

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
stop_flag = True  # for stopping the robot
restart_flag = False
reverse_flag = False
turn_flag = False
park_flag = False
pause_flag = False  # for pausing the robot
flag_line_orange = False  # for tracking orange lines
flag_line_blue = False  # for tracking blue lines
after_block = False  # for tracking turns after blocks
has_blocks = False

direction = ''  # direction variable

# Setup GPIO
GPIO.setmode(GPIO.BOARD)  # or GPIO.BCM depending on your wiring
GPIO.setup(PWM_PIN, GPIO.OUT)  # BLUE PWM pin
GPIO.setup(DIR_PIN, GPIO.OUT)  # YELLOW Direction control pin
GPIO.setup(FG_PIN, GPIO.IN)   # GREEN Encoder Frequency Generator signal input pin

# Setup PWM
pwm = GPIO.PWM(PWM_PIN, 10000)  # 10kHz frequency, adjust if needed
pwm.start(100) # 100 for this motor actually means 0 pulse width
GPIO.output(DIR_PIN, True)

flag = True
last_time = time.time()

print("\n\n\n* * * * * * * PINK BOBA PEARLS!!! Beti is READY!!!! * * * * * * * \n\n\n")

cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640,480)}))
picam2.start()

frame = picam2.capture_array("main")

if frame is None:
    print("No image captured - main")

# initializing objects for different areas
pd_r = Frames(frame, X1_1_PD, X2_1_PD, Y1_PD, Y2_PD, [BLACK_LOW, MGNTA_LOW], [BLACK_UP, MGNTA_UP])  # for the right wall
pd_l = Frames(frame, X1_2_PD, X2_2_PD, Y1_PD, Y2_PD, [BLACK_LOW, MGNTA_LOW], [BLACK_UP, MGNTA_UP])  # for the left wall

# for counting lines
line = Frames(frame, X1_LINE, X2_LINE, Y1_LINE, Y2_LINE, [BLUE_LOW, ORANGE_LOW], [BLUE_UP, ORANGE_UP])

# for detecting red abd green blocks
block = Frames(frame, X1_BLOCK, X2_BLOCK, Y1_BLOCK, Y2_BLOCK, [GREEN_LOW, RED_LOW_1, RED_LOW_2], [GREEN_UP, RED_UP_1, RED_UP_2])

# for detecting walls or color blocks, so the car can stop and reverse
stop_reverse = Frames(frame, 240, 400, Y1_STOP, Y2_STOP, [BLACK_LOW, GREEN_LOW, RED_LOW_1, RED_LOW_2, MGNTA_LOW], [BLACK_UP, GREEN_UP, RED_UP_1, RED_UP_2, MGNTA_UP]) 

# for detecting walls or color blocks, so the car can stop and reverse
park = Frames(frame, 240, 400, Y1_PARK_STOP, Y2_PARK_STOP, [BLACK_LOW, MGNTA_LOW], [BLACK_UP, MGNTA_UP]) 

# for detecting the parking blocks
park_r = Frames(frame, X1_1_PARK, X2_1_PARK, Y1_PARK, Y2_PARK, [MGNTA_LOW], [MGNTA_UP])  # for the right parking block
park_l = Frames(frame, X1_2_PARK, X2_2_PARK, Y1_PARK, Y2_PARK, [MGNTA_LOW], [MGNTA_UP])  # for the left parking block

# variables for counting fps
time_fps = time.time()
fps = 0
fps_last = 0

ser.write("sss\n".encode('utf-8')) # sending message to Microbit
time.sleep(0.1)

GPIO.output(DIR_PIN, True)

# ~ pwm.ChangeDutyCycle(30)
# ~ time.sleep(0.03)
# ~ ser.write("265\n".encode('utf-8'))
# ~ time.sleep(3.9)
# ~ ser.write("115\n".encode('utf-8'))
# ~ time.sleep(2.3)
# ~ pwm.ChangeDutyCycle(100)

# ~ ser.write("115\n".encode('utf-8'))
# ~ time.sleep(0.5)
# ~ pwm.ChangeDutyCycle(20)
# ~ time.sleep(4)
# ~ pwm.ChangeDutyCycle(100)
# ~ time.sleep(0.1)

# ~ ser.write("265\n".encode('utf-8'))
# ~ time.sleep(0.1)
# ~ GPIO.output(DIR_PIN, False) 
# ~ pwm.ChangeDutyCycle(60)
# ~ time.sleep(1.3)
# ~ pwm.ChangeDutyCycle(100)
# ~ time.sleep(0.1)
# ~ GPIO.output(DIR_PIN, True)
# ~ ser.write("125\n".encode('utf-8'))
# ~ time.sleep(0.2)
# ~ pwm.ChangeDutyCycle(20)
# ~ time.sleep(4)
# ~ pwm.ChangeDutyCycle(100)

while True:  # main loop
    fps += 1
    
    frame = picam2.capture_array("main")
    if frame is None:
        print("No image captured")
        break
    
    mb_msg = ser.read_all().decode("utf-8")
    if mb_msg == 'go':
        if stop_flag:
            if restart_flag:
                restart()
            stop_flag = False
            speed = DEFAULT_SPEED
            ser.write("str\n".encode('utf-8'))  # sending message to Microbit 
        else:
            restart()
            ser.write("190\n".encode('utf-8'))  # sending message to Microbit
            speed = STOP_SPEED
            pwm.ChangeDutyCycle(100)
            time.sleep(0.2)
            ser.write("stp\n".encode('utf-8'))  # sending message to Microbit
        
    # ~ if mb_msg == 'quit':
        # ~ ser.write('190\n'.encode('utf-8'))
        # ~ pwm.ChangeDutyCycle(100)
        # ~ time.sleep(0.1)  
        # ~ print("Ciao...")
        # ~ ser.write('sqt\n'.encode('utf-8'))
        # ~ time.sleep(0.1)
        # ~ break 
        
    if (not stop_flag):
                 
        # In the stop and reverse frame, look for blacks, greens and reds
        stop_reverse.update(frame)
        
        # The car should avoid bumping into walls or the color blocks. This section of code takes care of that
        # The first line gets a list of all black contours
        # The second line gets the list of all green contours and adds it to the orignal list
        # The third line gets the list of all red contours and adds it to the orignal list
        contours_stop = stop_reverse.find_contours(0, to_draw=DRAW, min_area=200, color=(255, 255, 255))
        contours_stop.extend(stop_reverse.find_contours(1, to_draw=DRAW, min_area=800, color=(0, 255, 0)))
        contours_stop.extend(stop_reverse.find_contours(2, to_draw=DRAW, min_area=600, color=(255, 0, 0), is_red=True))

        # If there are any contours large enough, reverse the robot a bit 
        if contours_stop:
            contours_stop = max(contours_stop, key=cv2.contourArea)
            area_stop = cv2.contourArea(contours_stop)
            if area_stop > 200:
                speed = STOP_SPEED
                reverse_flag = True
                time_stop = time.time()
                steer = 90
                if direction == "CW":
                    steer = 150
                elif direction == "CCW":
                    steer = 30
                print ("REVERSING....")
                
        while reverse_flag:
            if time.time() - time_stop < 1.2:  # reversing for a bit original 0.7
                speed = 80
                GPIO.output(DIR_PIN, False) #Reverse
                
            else:
                reverse_flag = False
                GPIO.output(DIR_PIN, True)
                speed = DEFAULT_SPEED       
            mesg = str(steer + 100) + '\n'  # forming the message for Microbit
            pwm.ChangeDutyCycle(speed)
            print("Reverse: ", mesg)
            ser.write(mesg.encode('utf-8'))  # sending message to Microbit
            
        # Look for obstacle blocks, both red and green
        block.update(frame)  # updating block area

        u_red = pd_block('red')  # getting controlling influence for red blocks
        u_green = pd_block('green')  # getting controlling influence for green blocks
        
        # If7 there are colored blocks, find the one that largely influences the steering value
        # This would generally be the block that is closer to the camera
        if u_green != -1 or u_red != -1:
            steer = 90 + max(u_green, u_red, key=abs)  # if there are blocks, counting final controlling influence
            speed = DEFAULT_SPEED
            
            # this checks if the run has had any color blocks. 
            # This is used only for parking, so it wont attempt parking 
            # at the end of the open challenge            
            has_blocks = True 

        # if there are no blocks, the robot will drive between walls
        else:
            pd_r.update(frame)  # updating wall areas
            pd_l.update(frame)
            steer = pd()  # counting controlling influence
            speed = DEFAULT_SPEED

        line.update(frame)  # updating line-counting area
        contours_blue = line.find_contours(0, DRAW, min_area=500)  # getting bue and orange areas
        contours_orange = line.find_contours(1, DRAW, min_area=500, color=(255, 255, 0))

        if contours_blue:  # if there is blue contour, checking, if the line is new, and adding it
            contours_blue = max(contours_blue, key=cv2.contourArea)
            ar = cv2.contourArea(contours_blue)
            if ar > 10:
                if not flag_line_blue and time.time() - time_blue > 1.4:
                    if not direction:
                        direction = 'CCW'
                    blue += 1
                    if blue == 1 and orange == 0:
                        time_speed = time.time()
                    # ~ print(f'direction: {direction} --- blue: {blue} --- orange: {orange}')
                    time_blue = time.time()  # resetting timer for blue lines
                    tim = time.time()  # resetting timer for stopping
                flag_line_blue = True
        else:
            flag_line_blue = False

        if contours_orange:  # if there is orange contour, checking, if the line is new, and adding it
            contours_orange = max(contours_orange, key=cv2.contourArea)
            ar = cv2.contourArea(contours_orange)
            if ar > 10:
                if not flag_line_orange and time.time() - time_orange > 1.4:
                    if not direction:
                        direction = 'CW'
                    orange += 1
                    if orange == 1 and blue == 0:
                        time_speed = time.time()
                    time_orange = time.time()
                    # ~ print(f'direction: {direction} --- orange: {orange} --- blue: {blue}')
                    tim = time.time()
                flag_line_orange = True
        else:
            flag_line_orange = False
        
        # SHADYA: REMEMBER TO SET PARKING TO FALSE for OPEN RUN
        # ALSO DURING OPEN RUN, THIS ENTIRE IF/ELSE BLOCK NEEDS TO BE COMMENTED
        # AND the STATEMENT BELOW THAT NEEDS TO BE UNCOMMENTED
        if PARKING:
            stop_time_delay = 3.5 if direction == 'CW' else 3.5 #this is for stopping AND parking in OBSTACLE ROUND
        else:
            stop_time_delay = 2.8 if direction == 'CW' else 2.5 #this is for stopping ONLY in OBSTACLE ROUND
            # ~ stop_time_delay = 1 if direction == 'CW' else 1.2 #this is for stopping OPEN ROUND 
            # ~ IMPORTANT: MAKE SURE PARKING IS SET TO FALSE FOR OPEN ROUND           
        if (max(orange, blue) >= line_count and time.time() - tim > stop_time_delay):  # checking if the robot must stop
            time_stop = time.time()
            speed = STOP_SPEED
            steer = 90
            stop_flag = True
            restart_flag = True
            tim = time.time()
            # Set parking to True only if the global PARKING flag is set, 
            # and if the code detected colored blocks in the run
            if PARKING and has_blocks:
                park_flag = True
                park_time = time.time()

        if pause_flag:  # checking if the robot is paused
            steer = DEFAULT_STEER
            speed = STOP_SPEED
        
        if time.time() - time_fps > 1:  # counting fps
            time_fps = time.time()
            fps_last = fps
            fps = 0

        frame = cv2.putText(frame, ' '.join([str(speed), str(steer), str(fps_last)]), (20, 30),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # printing parameters on the image
        mesg = str(steer + 100) + '\n'  # sending message to Microbit
        # ~ print(mesg)
        pwm.ChangeDutyCycle(speed)
        ser.write(mesg.encode('utf-8'))  # sending message to Microbit

    # Attempt parking if the parking flag has been set
    # and 0.1 second after the car has fully stopped
    # If parking is not set, the car just stops and the execution waits 
    # for the next start command 
    if (park_flag and stop_flag and time.time() - tim > 0.1):
        
        print("Attempting to park")
        
        direction = "CW"
        
        pd_r.update(frame)  # updating wall areas
        pd_l.update(frame)
        steer = pd_align()
        speed = PARK_SPEED

        if park_flag:
            mesg = str(steer + 100) + '\n'  # forming the message for Microbit
            # ~ print("Attempting to park:", mesg, end='')
            pwm.ChangeDutyCycle(speed)
            ser.write(mesg.encode('utf-8'))  # sending message to Microbit
        else:
            pwm.ChangeDutyCycle(100)
            ser.write('190\n'.encode('utf-8'))  # sending message to Microbit
    
    # ~ #### THIS IS TO ATTEMPT PARKING STRAIGHT INTO THE PARKING AREA ####
    
    # ~ # Attempt parking if the parking flag has been set and 0.1 second
    # ~ # after the car has fully stopped
    # ~ # If parking is not set, the car just stops and the execution  
    # ~ # waits for the next start command 
    # ~ if (park_flag and stop_flag and time.time() - tim > 0.1):
        # ~ park.update(frame)
        # ~ park_r.update(frame)  # updating wall areas
        # ~ park_l.update(frame)
        
        # ~ # This block of code is to prevent the car from touching the wall or the parking blocks
        # ~ # This is the window at the bottom of the screen which looks for nearby colors
        # ~ # The first line is to detect black wall ahead in the bottom window and STOP
        # ~ # it is optimized to stop as close to the wall as possible without knocking down the wall
        # ~ # if need to stop earlier increase the height (Y1 parameter) of the window by 5 pixel
        # ~ # Alternatively, the area_stop value can be reduced from 600 to a smaller value to stop early
        # ~ contours_stop = park.find_contours(0, to_draw=DRAW, min_area=200, color=(255, 255, 255))
        # ~ # This line is to reverse the car slightly if it sees magenta in the bottom window
        # ~ # so it can reattempt the approach
        # ~ contours_reverse = park.find_contours(1, to_draw=DRAW, min_area=100, color=(255, 0, 255))
        
        # ~ if contours_stop:
            # ~ contours_stop = max(contours_stop, key=cv2.contourArea)
            # ~ area_stop = cv2.contourArea(contours_stop)
            # ~ # If black contour is found, set the speed to zero so the robot will stop
            # ~ # The area_stop value can be reduced from 600 to a smaller value to stop earlier if needed
            # ~ if area_stop > 600:
                # ~ speed = STOP_SPEED
                # ~ steer = 90
                # ~ park_step = 2
                # ~ print('SAW BLACK. STOPPING.....')
        # ~ elif contours_reverse:
            # ~ contours_reverse = max(contours_reverse, key=cv2.contourArea)
            # ~ area_reverse = cv2.contourArea(contours_reverse)
            # ~ # If magenta contour is found, flag the car to commence reversing.
            # ~ # Also, set appropriate steering values based on the direction of the run
            # ~ if area_reverse > 100:
                # ~ reverse_flag = True
                # ~ time_stop = time.time()
                # ~ steer = 90
                # ~ if direction == "CW":
                    # ~ steer = 30
                # ~ elif direction == "CCW":
                    # ~ steer = 150
                # ~ print('SAW MAGENTA. REVERSING....')
            # ~ while reverse_flag:
                # ~ if time.time() - time_stop < 1.2:  # reversing for a bit original 0.7
                    # ~ speed = 20
                    # ~ GPIO.output(DIR_PIN, False) 
                # ~ else:
                    # ~ reverse_flag = False
                    # ~ GPIO.output(DIR_PIN, True)
                    # ~ speed = DEFAULT_SPEED       
                # ~ mesg = str(steer + 100) + '\n'  # forming the message for Microbit
                # ~ print('Reverse: ', mesg)
                
                # ~ pwm.ChangeDutyCycle(speed)

                # ~ ser.write(mesg.encode('utf-8'))  # sending message to Microbit
                    
        # ~ # This block of code is a 3 step approach to parking the car
        # ~ # Step 1: When the car ends the run clockwise, it reverses and turns to align to the parking blocks
        # ~ #        When counter clockwise, it just turns forward to align to the parking blocks
        # ~ #        This step is not always a guarantee, but it has a 50:50 chance 
        # ~ if park_step == 0:
            # ~ print("STEP 1: Turning to align", end='')
            # ~ if (not turn_flag and time.time() - tim < 0.6):
                # ~ time_turn = time.time()
                # ~ turn_flag = True
                # ~ print('Setting Turn Flag')
            
            # ~ turn_time = 2.5
            
            # ~ if turn_flag and time.time() - time_turn < turn_time:
                # ~ print(f'Making the turn for {turn_time} seconds')
                # ~ if direction == 'CW':
                    ## ~ wall = pd_l.update(frame)
                    # ~ steer = 30
                    # ~ speed = 0 # But Reverse here
                # ~ else:
                    ## ~ wall = pd_r.update(frame)
                    # ~ steer = 30
                    # ~ speed = 0
            # ~ else:
                # ~ turn_flag = False
                # ~ park_step = 1
                # ~ print('Exiting turn')
                
        # ~ # Step 2: This is where the car just moves ahead at a set speed
        # ~ #         It will drive straight until magenta is seen in the center windows
        # ~ #         There are 2 windows to either side of the screen int he middle that will look for magenta contours
        # ~ #         Depending on which contour is larger the car will steer to the other side
        # ~ #         The car will keep going forward until the main code detects black and sets the speed to 0
        # ~ elif park_step == 1:
            # ~ print('STEP 2: Parking inside the blocks')
            # ~ steer = pd_park()
            # ~ speed = 80
            
        # ~ # Step 3: When the car has come to a stop when it sees the black wall ahead, 
        # ~ # parking flag is set to false to end the execution of this logic
        # ~ elif park_step == 2:
            # ~ park_flag = False
            # ~ print('***** DONE *****')
        
        # ~ if park_flag:
            # ~ mesg = str(steer + 100) + '\n'  # forming the message for Microbit
            # ~ print("Attempting to park:", mesg, end='')
            # ~ pwm.ChangeDutyCycle(speed)
            # ~ ser.write(mesg.encode('utf-8'))  # sending message to Microbit
        # ~ else:
            # ~ pwm.ChangeDutyCycle(100)
            # ~ ser.write('190\n'.encode('utf-8'))  # sending message to Microbit

    if DRAW:
        cv2.imshow("Video Frame", frame)

        key = cv2.waitKey(1) & 0xFF
            
        if key != -1:
            if key == ord('q'):
                ser.write('190\n'.encode('utf-8'))
                pwm.ChangeDutyCycle(100)
                print("Ciao...")
                break
            elif key == ord('p'):  # if s is clicked, pausing the robot
                pause_flag = True
            elif key == ord('g'):  # if g is clicked unpausing the robot
                pause_flag = False
            elif key == ord('r'):  # if r is clicked restarting the robot
                restart()

pwm.stop()
GPIO.cleanup()
ser.close()
cv2.destroyAllWindows()
