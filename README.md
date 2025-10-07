# **2025 WRO Future Engineers Competition** 
# Team **Pink Boba Pearls** 🌸🧋🫧
This repository is for the 2025 WRO Future Engineers competition. We are a team of 2 high-school girls from Ontario, Canada 🇨🇦 We are passionate about all things engineering - specifically computer science and space 

This repository has the below folders
1. [`models`](/models) - Contains STL files we used for our 3D prints 
2. [`other`](/other) - Contains miscellanous files used for README.md
3. [`schemes`](/schemes) - Contains our connection schematic and power distribution schematic
4. [`src`](/src) - Contains our source code 
5. [`t-photos`](/t-photos) - Contains team photos
6. [`v-photos`](/v-photos) - Contains vehicle photos
7. [`videos`](/videos) - Contains links to vehicle demo youtube videos`

# The problem


# The Idea
We are a new team, and started late in June, so we need something that we can build that aligns with our abilities


To be successful, we will need to go with:
1. A simple chassis - Either buy one, or modify an existing chassis
2. Use Raspberry Pi to be the brain, and a camera with OpenCV library to be the eyes
3. Use Arduino or Microbit for micro controller
4. Use ultrasonic sensor, color sensor and IMU sensor as needed
5 Use simple power management setup to distribute power to micro processor, micro controller and the DC Motor


This notebook documents our journey and the decisions we made for each component as we iterated to the final working product


# Chassis
The chassis underwent 3 iterations to the final product


## Iteration 1
For the first iteration, we started with a simple chassis purchased from Amazon


### Advantages
* Light weight and easy to build
* Allowed some level of customization to add 3D printed parts
* Gained understanding of lack of fine steering control with DC motor (and its limitations)




### Disadvantages
* Too flimsy - the structure can’t handle the weight of all the components, about 600 grams of it.
* Underpowered - The small wheels with the gearing ratios with the DC motor did not allow for enough speed or enough torque to drive the weight
* Steering was either fully to the left or right with the DC motor. Finer direction control was not possible - although we could’ve replaced it with a servo motor


## Iteration 2
We experimented with a RC car that we got from a thrift store after removing its top and control circuitry


### Advantages
* The chassis was just available. Nothing to build. It was also very stable and not flimsy
Light weight
* We could add 3D printed parts to it
* Rubber wheels had good grip


### Disadvantages
* The chassis was too wide at 15cms. It was hard to park where we needed it
* DC drive motor based drive axle kept rolling and didn’t stop where we needed it to stop, unless we reversed the motor direction.
* Steering was either left or right with the DC motor. Finer direction control was not possible - although we could’ve replaced it with a servo motor




## Iteration 3 - Final
Finally, we settled on a Lego technic chassis that we built ourselves and it worked for us


### Advantages
* Ability to customize as needed without having to 3D print many parts
* 9V Lego motor provides the power and torque we need, and it easily mounts on the chassis


### Disadvantages
* 9v Lego motor isn’t ideal. However, with a L298N motor driver we were able to handle that.
* Couldn’t get a Lego servo motor to work with the L298N motor driver. We had to build 3D printed mount for SG90 servos instead.
* The final chassis looks bulky. There is room for optimization
* Heavier than the other 2 chassis, however it is still within allowed weight




# 3D printed parts
Since we used a Lego Chassis, we needed a way to mount
* The servo motor to the front wheels for steering.
    * Initially we tried to 3D print our own design.
    * Later, we found a 3D file that we found on Thingiverse that worked better for our purpose


* Mount for the wide angle camera.
    * This is to attach to the Lego chassis, and to hold the camera at a specific angle.
    * This design allowed us to experiment with various heights and mount angles before we got it right.
    * We designed and 3D printed this ourselves.


# System control


This section explains the control system setup i.e, the raspberry pi, the camera, the microbit and the shield, the motor driver, the motors themselves, and the design choices that led to selection of each component


## To see or to sense?
### Iteration 1 - Use of sensors
We originally wanted to connect a few sensors and motors to Arduino and test it. Then we had a better idea which is what we experimented with on the first 2 iteration of the chassis
* Use of sensors connected to the Microbit
    * Ultrasonic sensors for wall detection
    * Color sensors for line detection.
    * IMU for accurate turns
* We tested with one Ultrasonic sensor and one color sensor in iteration 2 of our chassis and we were successful.


### Iteration 2 - Computer Vision
* In our subsequent research we were able to find inspiration to do it all with just one camera. We tested it out and found success - as explained in the program logic section
* Since we had success with using the camera alone, we removed all the sensors from the design and decided to go with only camera vision


## Mobility Control
### Drive motor
* Used Lego 9v DC motor because it had the ideal torque and speed characteristics we needed
* Used L298N motor driver with 12v power input from the battery and PWM control input from the Microbit to control the 9V Lego DC motor
* L293D motor driver was considered, but was not used since it can only handle 600mA, whereas the Lego 9V motor has a stalled current draw of 850mA


### Steering Servo
* Used SG90 180 degree servo motor with analog output from the Microbit.
    * 90 degree points the wheels straight
    * 30 degree is the farthest right steering, limited by the code
    * 150 degrees is the farthest left steering, limited by the code


## Choice of micro controller - Microbit
We experimented with an Arduino Uno R3 and  board early on with a motor control shield for both DC motor control and Servo motor control.
### Why not Arduino
We had issues getting the motor control shield to work due to an outdated library. As we were troubleshooting that, we discovered that Microbit is more powerful than the Arduino Uno R3 board. Also the coding was to be done in C++ which we were not familiar with.
### Why not ESP32 S3 WROOM Camera board
We wanted to try using it with Edge impulse image classification for object detection. However,  we could never get the camera to respond. Also the coding was to be done in C++ which we were not familiar with.
### Microbit Advantages
* More processing power than the Arduino
* Smaller form factor compared to an Arduino
* Similar number of I/O pinouts as the Arduino
* Easy to learn. We used python for programming
* Extensive library support for common sensor modules
* Inbuilt buttons were used to start / stop the car
* Inbuilt LED array display and speakers were used for troubleshooting
* Inbuilt Inertial Movement Sensor unit for precise turns. We did not need this.
* Very low power supply requirements
### Microbit Disadvantages
* Harder to natively connect to the pins. We used the Siyeenove Microbit shield to overcome this
* Inadequate information online to understand interfacing with Raspberry Pi over USB serial connection, but it was quite easy to figure out with a bit of experimentation.
### Microbit Motor Control
Siyeenove Microbit shield allows us to conveniently interface with
* The Servo motor via the P0 pin. We use analog signal to position the servo motor
* The DC motor control via the PWM pins connected to the L298N motor driver.
### Microbit Serial connection with Raspberry Pi
The Microbit connects with the Raspberry Pi via a USB cable for serial data transfer. This serial data connection is used by the Raspberry Pi to achieve bi-directional data exchange with the Microbit
* TX to Raspberry Pi - Control signals to start and stop the car operation
* RX from Raspberry Pi - Steering and Servo control values
### Use of Microbit buttons
* Button A is programmed to start and stop the car. When car is stopped by pressing the A button, pressing it again will commence a new run
* Button B is the kill command. It is programmed to stop all motor activity by signalling the Raspberry Pi to exit the Python program execution
### Function Outline
* As soon as it starts, it initializes the motor speed to 0 and servo direction to 90 (which keeps the car straight)
* It awaits signal from the Raspberry Pi to confirm its program has started successfully. When it receives the confirmation, it displays an 'S' on the LED array
* When the user presses the 'A' button, it transmits a 'go' signal to the Raspberry Pi and awaits acknowledgement from the Raspberry Pi. When the acknowledgement is received, it displays a '+' on the LED array indicating that the car has started.
* As the car runs, Raspberry Pi transmits the servo steering turn data and DC motor speed data as byte stream which the Microbit will convert to numerical data, and split to integer values to be used for motor control
* The servo turn angle is sent as analog signal to the servo motor directly. The 5V input required by the Servo is supplied by the Siyeenove Mshield board.
* The speed data is sent as PWM signal to the L298N motor driver which uses the PWM signal and the power input from the 12V battery to drive the 9V DC motor.
* If the user wants to stop the car (and reset its values so the car can run again), they can simply press the 'A' button again which will signal the Raspberry Pi to stop the loop that processes vision data. This will display a minus '-' on the LED array.
* If the user wants to kill the car (completely end the program), they can press the 'B' button which will signal the Raspberry Pi to exit the Python program
## Choice of SBC - Raspberry Pi
* Raspberry Pi was an easy choice. We were familiar with it. Also, during our research we also noticed many other teams using it with a camera module.
### Advantages
* Familiar platform with abundant support, especially for vision processing using OpenCV libraries with a basic camera module
* Allows programming in Python which we are comfortable with
* Ability to connect serial interface via USB
### Disadvantages
* We used R-Pi 4B which requires a 2.5A portable power supply which was initially hard to manage.
* We tried driving the motors with Raspberry Pi directly, but that didn’t go well. The motor behaviors were unpredictable and the Raspberry Pi shutdown whenever the Servo stalled. So we decided to have the Microcontroller handle the motor control signals with the vision input parameters from the Raspberry Pi
### Choice of camera
**Iteration 1: Raspberry Pi Camera V2**


We used this until 3 weeks before competition simply because we already had it and it seemed to work fine for the open challenge. We were able to get 40 fps processing speeds with it but that didn’t really matter to us.


However, it wasn’t able to see either of the walls properly, which was OK for the straight runs, but for the turns, our logic worked based on the white spaces of the openings (instead of turning at the curves. In this case, the car would run up to the wall ahead and then try to make the turn which resulted in the car running into the walls.


So we researched online and switched to a wide angle camera.
**Iteration 2: Sainsmart 160 degree wideangle 5MP Camera**
This worked for us with some tweaking.
* Since it was a 5MP camera, we had to downscale it to 480p and achieved about 25 fps.
* The lens had a pink hue depending on the lightning and we had to adjust the hue on the HSV configuration
* The camera angle pointing ahead had to be lowered since the camera was being affected by ambient lighting conditions
* The color detection areas had to be adjusted (mostly lowered) to avoid external objects influencing the steering
* Thankfully, we could reuse our 3D printed mounts without having to redesign it.
### Function Outline
* Python program obs_ch.py is loaded from the crontab, which launches the program when the Raspberry Pi boots up
* Once it is ready, it sends a signal to the Microbit indicating that it is ready. If there is a problem with the Python Program loading, the signal to the Microbit will not be sent which will allow the user to fix the program.
* Then it listens to the Microbit's A button to be pressed to start the car which starts calculating and transmitting DC motor speed and Servo turn data to the Microbit.
* As the car runs, the program reads visual data from the camera frame by frame and processes it using proportional-derivative controller (https://en.wikipedia.org/wiki/PID_controller) to get the servo turn values, which is transmitted to the Microbit in real-time to control the cars turns
* The program has 2 distinct vision processing logic inside it
    * For the open run, it looks at the walls and uses PD control to keep the car between the walls
    * For the obstacle run, it looks at the color blocks and uses PD control to turn the car to avoid the blocks.
* Detailed explanation of the code is provided in the Program Logic section

# Bill of Materials
We experimented with many boards and components before settling on our final design. The below list is for the final design only.

| Part | Reference Cost - As of Sep 1, 2025 - Taxes not included | Purchase Link for Future Reference |
| ------------ | ------------: | ------------ |
| **Micro:Bit** |  |  |
| Micro:Bit | $48.59  |  https://www.amazon.ca/KEYESTUDIO-MICROBIT-V2-2-KIT-Beginners/dp/B0BNKTGGB7
| Micro:Bit Motor Shield (DC Motor and Servo) | $16.00 | https://www.amazon.ca/dp/B0F24V8X31 |
| **Raspberry Pi**  |   |   |
| Raspberry Pi 4  | $62.95  | https://www.pishop.ca/product/raspberry-pi-4-model-b-2gb/  |
| Sainsmart Wideangle 5MP Camera 160 degree FoV  | $16.99  | https://www.amazon.ca/SainSmart-Fish-Eye-Camera-Raspberry-Arduino/dp/B00N1YJKFS  |
| **Other Accessories to build the car**  |   |   |
| 9v-12 Battery bank  | $41.79  | https://www.amazon.ca/dp/B01M7Z9Z1N  |
| 12V to 5V Step-down converter  | $5.28  | https://www.aliexpress.com/item/1005006655110785.html  |
| L298N motor driver  | $11.99  | https://www.amazon.ca/Controller-Module-Bridge-Stepper-Arduino/dp/B0D8G2PZBB  |
| SG90 Servo motors  | $19.99   | https://www.amazon.ca/dp/B0CP98TZJ2  |
| Short USB to USB-C cable  | $10.99  | https://www.amazon.ca/etguuds-Charging-Charger-Braided-Compatible/dp/B08933P982  |
| Short USB to Micro-USB cable  | $8.99  | https://www.amazon.ca/Micro-CableCreation-High-Speed-Triple-Shielded/dp/B013G4D2OM  |
| Lego Parts to build the chassis  |   |   |
| 3D printed parts to complete the chassis  |   |   |
| **Total**  | **\$251.44**  |   |


# Power Management


Initially, as we were testing vision, all the components were powered with a wall outlet power source. Once we fully understood the power requirements, we found a 12V rechargeable power supply that can supply 3A of current to be able to concurrently supply power to
* Raspberry Pi 4B - Needs 5V 2.5A
* Siyeenove shield for the Microbit - Needs 5V 0.5A
* L298N motor driver (which in turn powers the 9V lego motor) - Needs 12V 0.5A


We used a 12V to 5V step-down power converter to supply 5V power to the Raspberry Pi and the Microbit shield.


The Microbit itself did not require separate power since it was powered by the shield.


# Program Logic
## Microbit - pi2mb_motors_control.py
### Summary
* Microbit powers up, then plays a tone, initializes motors & serial.
* **Button A** sends "go" to R-Pi (start/stop car).
* **Button B** sends "quit" to R-Pi (exit program).
* **Raspberry Pi** to **Microbit** Serial Connection data transmission via USB:
    * Sends **status codes ("startt", "stoppp", etc.)** → Microbit shows icons.
    * Sends **numeric codes (e.g., "120250")** → Microbit sets servo angle + motor speed.
* Servo Motor is controlled using analog signals via the **Siyeenove mShield**
* Drive Motor is controlled using PWM signals sent to the **L298N motor driver**


---
### Imports and Setup
```
from microbit import *
import music
import mShield
```
* `microbit`: gives access to Microbit’s hardware (pins, buttons, display, etc.).
* `music`: allows sounds to be played.
* `mShield`: library for controlling the **Siyeenove motor shield** (PWM outputs for motors/servos).


### Startup Signal
```
music.play(music.tone_playable(Note.C, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)
```
As soon as the Microbit is started or reset, it plays a tone to indicate the Microbit is active.


### Serial Communication Setup
```
serial.redirect_to_usb()
serial.set_baud_rate(BaudRate.BAUD_RATE115200)
serial.set_rx_buffer_size(7)
```
* Setting up serial connection parameters. This is how the Microbit exchanges commands/data with the Raspberry Pi.
* Notice the buffer size of 7. This means all the inputs received from the Raspberry Pi should be 7 characters including the newline character used a delimiter


### Motor Shield Setup
```
mShield.set_s1_to_s4_type(mShield.S1ToS4Type.PWM)
```
Configures ports **S1–S4** on the Siyeenove Mshield to output **PWM** (used for motor speed/servo control).


### Default Values
```
deg = 90
speed = 0
pins.servo_write_pin(AnalogPin.P0, deg)   # Servo straight
mShield.extend_pwm_control(mShield.PwmIndex.S3, 0)  # Stop motor
mShield.extend_pwm_control(mShield.PwmIndex.S4, speed)
```
* Servo is set to **90° (straight)**
* Motor PWM is set to **0 (stopped)**


Button Controls
def on_button_pressed_a():
    basic.pause(100)
    serial.write_string("go")


input.on_button_pressed(Button.A, on_button_pressed_a)
When Button A is pressed → Microbit sends "go" over serial to R-Pi.
R-Pi decides whether to start/stop the car.


Main Loop
while True:
    try:
        data_in = serial.read_until(serial.delimiters(Delimiters.NEW_LINE))
Continuously listens for messages from the R-Pi.
Status Messages from R-Pi
if (data_in[0] == "s"):
    if data_in == "startt":   # Show "start" icon
    elif data_in == "stoppp": # Show "stop" icon
    elif data_in == "ssssss": # Show another status pattern
If the incoming data starts with "s", it’s a status message.
Different LED patterns indicate whether the car is:
S indicates Raspberry Pi Ready (also a tribute to the initials of the team member names, Swara and Shadya)
+ indicates Starting
- indicates Stopping
Motor/Servo value parsing
else:
    deg, speed = int(data_in[:3])-100, int(data_in[3:6])-200
If it’s not a status message, it’s a control command (numbers only).
The first 3 characters → servo angle (shifted by 100).
The next 3 characters → motor speed (shifted by 200).
Sample: "150250" → servo = 150-100 = 50°, motor speed = 250-200 = 50.
Motor/Servo control
    pins.servo_write_pin(AnalogPin.P0, deg)
    if speed < 0:
        mShield.extend_pwm_control(mShield.PwmIndex.S4, 0)
        mShield.extend_pwm_control(mShield.PwmIndex.S3, abs(speed))
    else:
        mShield.extend_pwm_control(mShield.PwmIndex.S3, 0)
        mShield.extend_pwm_control(mShield.PwmIndex.S4, speed)


Send deg, the servo turn angle as analog input to the P0 Pin connected to the Servo motor
Check of the speed value is positive (forward) or negative (reverse)
If positive, drive the motor forward by keeping S3 as 0, and providing the speed value as PWM input to S4
If negative, drive the motor backward by keeping S4 as 0, and providing the absolute of the negative speed value as PWM input to S3
Potential Improvements: Ideally, we would want to have a PD loop to ensure the steering turns and drive motor speed changes are smooth, but with the Microbit we don’t have a way to implement a close loop feedback system by reading the servo angles or the current drive speed of the DC motor. So, we had to forgo PD control at the component level and favor the implementation of PD control in the Raspberry Pi before it sends the values to the Microbit.
Error Handling
except:
    basic.show_leds("""
        # . . . #
        . . . . .
        . . . . .
        . . . . .
        # . . . #
    """)
    pass


If something goes wrong (bad serial data, etc.), shows an error pattern on the LED grid.










Raspberry Pi - obs_ch.py
Pseudo code for keeping the car between the walls and to avoid obstacles
Use the blue and orange lines to determine the direction of the lap (clockwise or counter clockwise) and to count if 3 laps have been achieved (by counting 12 lines of either color)
When the number of lines counted is less than 12
Look for red or green blocks in the center of the image up to the bottom of the image.
If red or green block is found, find the biggest blocks respectively
Determine the direction of turn (left for green blocks; right for Red blocks)
Apply proportional logic to determine the amount of turn by evaluating the X and Y coordinates of the block (nearer blocks will need tighter turns)
When the turn values are determined for both red and green blocks, use the biggest turn value since that would apply to the nearest block
If red or green block is not found (as when making turns or in open challenge conditions) look for the amount of black on either edges of the lower part of the image received from the camera
Use proportional derivative logic to determine the amount of steering. Error is the difference in the black areas of right and left walls. Greater black on the right side will steer the car to the left, and vice versa
During the laps, if a wall is detected to be too close, make a small reverse movement and reattempt.
At the end of 3 laps, depending on the direction the car will make a parking (non parallel) attempt between the purple blocks
Defining global constants and variables
Library imports
from picamera2 import Picamera2
import cv2
import numpy as np
import serial, time
Picamera2 → controls the Raspberry Pi camera.
cv2 (OpenCV) → image processing (drawing, masks, contours, etc.).
numpy → used for arrays (e.g. HSV color ranges).
serial → to transmit to Microbit over USB.
time → for delays.


Constants
DRAW = True
DEFAULT_SPEED = 0
DEFAULT_STEER = 90
MAX_R_STEER = 15
MAX_L_STEER = 165
STEER_ADJ = 25
Flag: if True, draw debug rectangles/contours on the image so we can see what the car sees.
The other constants are used to define default values for the motor and servo control


PD controller gains
KP = 0.025
KD = 0.1
These tune the car’s steering smoothness.
KP (proportional gain) → how strongly to steer based on error.
KD (derivative gain) → how much to react to changes in rate of error.


Block detection scaling
K_X = 0.12
K_Y = 0.2
K_X is used to control the steering based on the blocks position on the X axis.
K_Y is used to control the steering based on the blocks position on the Y axis. Closer the object is, the greater the influence will be.


HSV color thresholds
These define which pixels belong to a given color range. HSV is used because it’s more reliable than RGB in challenging light conditions where the Hue of a color falls within a specific range. An upper range and lower range are defined to create a mask which filters these colors
Black - for walls and lines.
Green and Red - for block detection.
Blue and Orange - for line detection
We used a HSV color palette and converted the actual HSV values to OpenCV values (to be contained within the 0-255 range) using the below formula
H (Hue) - 0 to 360 values converted to 0-180 values by dividing by 2
S (Saturation - 0-100 values converted to 0-255 values by multiplying by 2.55
V (Value) - 0-100 values converted to 0-255 values by multiplying by 2.55


Camera image dimensions
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
Scaled down resolution from the OV5647 sensor for faster image processing. We are able to achieve up to 25 frames per second because of this.
All the rectangle coordinates below use this.


Regions of interest
We split the camera view into smaller zones, each with a specific purpose.
For block detection
X1_CUB = 40
X2_CUB = 600
Y1_CUB = 220
Y2_CUB = 440
Rectangle in the center of the image.
Used to look for green/red blocks.
For wall following (PD controller)
X1_1_PD = 610
X2_1_PD = 640


X1_2_PD = 0
X2_2_PD = 30


Y1_PD = 220
Y2_PD = 480
Used to make two rectangles:
Left zone (pd_l) = from 0 to 30 along the X axis on the far left.
Right zone (pd_r) = from 610 to 640 along the X axis on the far right
Used to measure wall area left vs right.
Both at the same height (220–480).
For line counting
X1_LINE = 280
X2_LINE = 360
Y1_LINE = 400
Y2_LINE = 480
Small horizontal strip at the bottom of the frame.
Used to detect black crossing lines (to count laps/checkpoints).


Frames class


Summary
This is a helper class for working with specific regions of the camera image by dividing its camera view into regions (Frames), and each region specializes in finding a specific thing (wall, line, block).
A Frames object = “a rectangular window” into one part of the camera image.
It knows:
Where to look (rectangle coordinates).
What color to look for (HSV range).
It can:
Crop & process that rectangular window.
Detect contours (outlined regions) of desired colors.


Initialization (__init__)
def __init__(self, img, x_1, x_2, y_1, y_2, low, up):
Takes:
img: the current camera image
x_1, x_2, y_1, y_2: rectangle coordinates (the window of the image to look at)
low, up: HSV color boundaries (of the colors to be processed in the image)
It stores those values and then calls self.update(img) to process the image.


Update function (update)
def update(self, img):
    cv2.rectangle(img, (self.x_1, self.y_1), (self.x_2, self.y_2), (0,255,220), 1)
    self.frame = img[self.y_1:self.y_2, self.x_1:self.x_2]
    self.frame_gaussed = cv2.GaussianBlur(self.frame, (1,1), cv2.BORDER_DEFAULT)
    self.hsv = cv2.cvtColor(self.frame_gaussed, cv2.COLOR_BGR2HSV)
Draws a rectangle on the original image (for debugging/visualization).
Crops out just that rectangle → self.frame.
Applies a tiny blur (to reduce noise).
Converts it from BGR (camera colors) to HSV (better for color detection).
So now this Frames object has a pre-processed image region ready for analysis.


Find contours (find_contours)
def find_contours(self, n=0, to_draw=True, color=(0,0,255), min_area=50, red_dop=0):
    self.mask = cv2.inRange(self.hsv, self.low[n], self.up[n])
    if red_dop == 1:
        mask_1 = cv2.inRange(self.hsv, self.low[n+1], self.up[n+1])
        self.mask = cv2.bitwise_or(self.mask, mask_1)
Creates a mask: keeps only the pixels in the HSV range (low[n]–up[n]), everything else becomes black.
Example: if low, up are for green → only green things show up.
If red_dop == 1: combines two red ranges (since red in HSV wraps around 0°/180°).
Finds the contours (shapes) of the detected areas.
Filters out very small ones (min_area).
Optionally draws them on the image (if to_draw=True).
Returns the list of “good” contours.


pd() function
Summary
Uses a PD controller to make the steering smooth, not jerky. The logic looks at how much wall is on the left vs right.
If the right wall looks closer → steer left
If the left wall looks closer → steer right.
If both are equal → go straight.


Measure wall area on the right side
contours = pd_r.find_contours(...)
if contours:
    area_r = max(map(cv2.contourArea, contours))
else:
    area_r = 0
Looks in the right region of the camera view.
Finds black areas (walls).
Keeps the biggest contour’s area (so ignores tiny specks).


Measure wall area on the left side
contours = pd_l.find_contours(...)
if contours:
    area_l = max(map(cv2.contourArea, contours))
else:
    area_l = 0
Same as above, but on the left side.


Calculate the error
err = area_r - area_l
If the right wall looks bigger (closer), error is positive → car should steer left.
If the left wall looks bigger, error is negative → car should steer right.
If both areas are equal → car is centered.


Apply PD control
steer = 90 + steer_adj + int(err * KP + ((err - err_old) / dT) * KD)
err_old = err
90: Default steering for driving straight. The Proportional and Derivative calculations add or subtract from this value to drive left or right.
+ steer_adj: adds camera correction based on whether the car is driving clockwise or counter clockwise.
Proportional term (err * KP): steers proportionally to how off-center it is.
Derivative term ((err - err_old) / dT * KD): reacts to how fast the error is changing (to avoid overshoot/wobble). Note that dT is a constant defined at the start and NOT calculated at runtime, since we already know that the camera processes 25 frames per second which means the time between frames is approximately 40ms.
Updates err_old to hold the current err value for the next frame.


Limit the steering range and return the final value
if steer > MAX_L_STEER :
    steer = MAX_L_STEER
if steer < MAX_R_STEER :
    steer = MAX_R_STEER


return steer
Prevents steering from going too far left or right (to protect servo) than the servo of the car can physically handle without damaging the steering.
Returns the final steering value


pd_block() function


Summary
Looks for either a green block or a red block in a predefined region of the camera frame.
If a block is found, it calculates how far the block is from the desired position.
It then produces a control signal (e_block) that tells the car how much to adjust its steering when approaching the block.




Choose color filter
    if color == 'green':
        contours = block.find_contours(to_draw=DRAW, color=(0, 255, 0), min_area=1000)
    elif color == 'red':
        contours = block.find_contours(1, DRAW, min_area=1000, red_dop=1)
    else:
        print('color error')
        return -1  # if the color is not right, return -1
If color == 'green', it looks for green contours in the image.
If color == 'red', it looks for red contours (red needs two HSV ranges, so it combines them).
If no valid color is given, it just returns -1 (error).


Find the largest block
    if contours:
        contours = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contours)
        x = (2 * x + w) // 2
        y = y + h


If any contours (shapes) are detected, it picks the biggest one (to ignore noise or small specks).
From this contour, it calculates the bounding rectangle and extracts its center x (horizontal) and bottom y (vertical).


Set the “target” position
        if color == 'red':
            time_red = time.time()
            x_tar = 0
        elif color == 'green':
            time_green = time.time()
            x_tar = block.x_2 - block.x_1


For red blocks, the “target x” is the left side of the detection zone.
For green blocks, the “target x” is the right side of the detection zone.
This means the car is supposed to go toward the left for red blocks and toward the right for green blocks.


Calculate error
e_x: how far the block’s x-position is from where it should be.
e_y: how far down the block is (so closer blocks give higher y).
These are scaled by tuning constants K_X and K_Y.
Both are combined into one error signal e_block. This makes the car steer differently depending on the block’s color and the car’s driving direction.


Show debug info (optional)
Writes the error value (e_block) on the video feed in either green (for green blocks) or red (for red blocks).


Return the control value
If a block is found → returns the steering correction (e_block).
If no block is found → returns -1.
restart() function


This function is used to reset all the variables including the flags and timers. This is used when the car needs to stop and start a fresh run without exiting the main loop.


Main code (including the main loop while True)
Serial Connection
Opens a USB serial connection to the Microbit at 115200 baud rate.
Flushes buffers and confirms the connection is open.
This serial connection is used in the main loop to receive start / stop signals from the microbit (ser.read_all()) and to send steering + speed values to the microbit (ser.write()).
Variables & Flags
Initializes counters for detected lines (orange, blue).
Steering, speed, and turn direction values (steer, speed, direction, etc.).
Timers for different actions (line detection, blocks detection, turning, stopping, etc).
Flags to track car states:
start_flag, stop_flag, reverse_flag, pause_flag
Line detection flags (flag_line_blue, flag_line_orange)
Camera Setup
Starts Picamera2 with a 640×480 preview stream.
Captures the initial frame.
Creates Frames objects for different regions:
pd_r and pd_l: detect black walls (right & left).
line: detect blue/orange crossing lines.
block: detect green/red blocks.
black_wall_stop: detect walls in front (stop condition).
Main Loop (while True)


Get New Frame
frame = picam2.capture_array("main")
if frame is None:
    print("No image captured")
    break
Takes a snapshot from the PiCamera2.
If no frame → stop the loop.
Start/Stop Command Handling
mb_msg = ser.read_all().decode("utf-8")
if mb_msg == 'go':
    if start_flag:
        restart()
        speed = 0
        ser.write("stoppp\n".encode('utf-8'))
    else:
        start_flag = True
        speed = DEFAULT_SPEED
        ser.write("startt\n".encode('utf-8'))
Reads Microbit messages.
If message is "go":
If already started → stop by setting speed to 0.
Otherwise → start car by setting speed to the default speed.
Stop and reverse if Wall is detected
black_wall_stop.update(frame)
contours_stop = black_wall_stop.find_contours(...)
if contours_stop:
    area_stop = cv2.contourArea(max(contours_stop, key=cv2.contourArea))
    if area_stop > 1000:
        speed = 0
        reverse_flag = True
        time_stop = time.time()
Looks for a big black wall in front of the car.
If found → stop and set reverse_flag.
while reverse_flag:
    if time.time() - time_stop < 0.9:  # reversing for 0.5 seconds
        speed = -50
        if direction == "CW":
            steer = 140
        elif direction == "CCW":
            steer = 40
Then inside the while reverse_flag: loop:
Car goes backward briefly (speed = -50).
Turns slightly (different steering if CW or CCW).
After reversing time ends → return to normal speed.
Block Detection (Red/Green)
block.update(frame)
u_red = pd_block('red')
u_green = pd_block('green')
if u_green != -1 or u_red != -1:
    steer = 90 + max(u_green, u_red, key=abs)
else:
    pd_r.update(frame)
    pd_l.update(frame)
    steer = pd()
Updates block-detection area.
Checks for red or green blocks:
If block found → calculate steering correction for red and green blocks (u_red or u_green) and determine which value is most influential and use that as the steering value.
If no red or green blocks are found in the frame (as in Open Challenge condition) → Update the wall detection areas on either edges and use the wall-following (pd()) function to calculate the steering values.
Line Detection (Blue/Orange)
line.update(frame)
contours_blue = line.find_contours(0, ...)
contours_orange = line.find_contours(1, ...)
Detects blue and orange line markers on the floor.
Each line crossing is counted.
Also determines car’s driving direction based on the line color that is detected in the very first section crossing:
Blue line → counter-clockwise (CCW).
Orange line → clockwise (CW).




The direction value is used for navigation and to decide when to stop.
Stop Condition
if (max(orange, blue) > 11 and time.time() - tim > 1.2) or stop_flag:
    ...
If car crosses 12+ lines OR stop flag is set :
Briefly brake (reverse for 0.3s).
Then set speed = 0 to force the car to stop completely.
FPS Calculation
if time.time() - time_fps > 1:
    time_fps = time.time()
    fps_last = fps
    fps = 0
Counts frames per second (useful for performance monitoring).
Send Commands to Microbit
if not stop_flag:
    frame = cv2.putText(frame, ' '.join([str(speed), str(steer), str(fps_last)]), ...)
    mesg = str(steer + 100) + str(speed + 200) + '\n'
    ser.write(mesg.encode('utf-8'))
Sends steering + speed command to Microbit.
Also overlays speed/steering/fps text on the video frame.


## The Hardware
1. **Microcontroller - [Microbit v2](https://microbit.org/buy/bbc-microbit-single/):** Together with the Siyeenove Mshield Pinout board - For controlling drive motor and steering servo motor based on input from the Raspberry Pi
2. **Single Board Computer (SBC) - [Raspberry Pi 4 Model B 2GB](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/):** Vehicle mobility control

Other parts used
1. Sainsmart 160 degree wideangle 5PM camera for Raspberry Pi
2. Lego Technic pieces - to build the chassis
3. 12V Lithium battery power supply - Power supply for all the components
4. 12v to 5V Step-down converter - To supply power to Raspberry Pi and Microbit
5. L298N Motor Driver - To drive the 9V Lego DC motor
6. 9V Lego Motor
7. SG90 Micro Servo Motor
8. Various cables for power connections to the devices, USB cable for serial connection between Microbit and Raspberry Pi, and wires to transmit data from Microbit to the motors.  

Refer to the component schematic to connect all the above hardware together to make the car

![Component Schematic](/schemes/WRO%20Future%20Engineeers%202025%20-%20Component%20Schematic.png)



## The Software

There are 2 important programs that make the car run

* `obs_ch.py` - loaded to the Raspberry Pi to process the vision input from the camera. 
  * It is part of the crontab, which launches the program when the Raspberry Pi boots up 
  * Once it is ready, it sends a signal to the Microbit indicating that it is ready. If there is a problem with the Python Program loading, the signal to the Microbit will not be sent which will allow the user to fix the program. 
  * Then it listens to the Microbit's A button to be pressed to start the car which starts calculating and transmitting DC motor speed and Servo turn data to the Microbit. 
  * As the car runs, the program reads visual data from the camera frame by frame and processes it using proportional-derivative controller (https://en.wikipedia.org/wiki/PID_controller) to get the servo turn values, which is transmitted to the Microbit in real-time to control the cars turns
  * The program has 2 distinct vision processing logic inside it
    1. For the open run, it looks at the walls and uses PD control to keep the car between the walls
    2. For the obstacle run, it looks at the color blocks and uses PD control to turn the car to avoid the blocks. 
  * Detailed explanation of the code is provided in the engineering documentation

* `pi2mb_motors_control.py` - loaded to the Microbit to drive the pi2mb_motors_control
  * As soon as it starts, it initializes the motor speed to 0 and servo direction to 90 (which keeps the car straight)
  * It awaits signal from the Raspberry Pi to confirm it has started successfully. When it receives the confirmation, it displays an 'S' on the LED array
  * When the user presses the 'A' button, it transmits a 'go' signal to the Raspberry Pi and awaits acknowledgement from the Raspberry Pi. When the acknowledgement is received, it displays a '+' on the LED array indicating that the car has started.
  * As the car runs, Raspberry Pi transmits the servo steering turn data and DC motor speed data as byte stream  which the Microbit will convert to numerical data, and split to integer values to be used for motor control
  * The servo turn angle is sent as analog signal to the servo motor directly. The 5V input required by the Servo is supplied by the Siyeenove Mshield board.
  * The speed data is sent as PWM signal to the L298N motor driver which uses the PWM signal and the power input from the 12V battery to drive the 9V DC motor. 
  * If the user wants to stop the car (and reset its values so the car can run again), they can simply press the 'A' button again which will signal the Raspberry Pi to stop the loop that processes vision data. This will display a minus '-' on the LED array.
  * If the user wants to kill the car (completely end the program), they can press the 'B' button which will signal the Raspberry Pi to exit the Python program

## Loading the software on to the hardware
Below section explains how to load each program on to their respective hardwares

**Getting `obs_ch.py` to run on the Raspberry Pi**

* Follow the Raspberry Pi **[Getting Started page](https://www.raspberrypi.com/documentation/computers/getting-started.html)** and follow all the instructions to get the OS distribution loaded and Raspberry Pi booted up
* `Tip` - Ensure you follow the instruction at the tail end of the above page to setup the **Raspberry Pi Connect". This will allow you to remotely connect to your Raspberry Pi with your laptop over Wifi. Otherwise, a separate monitor, HDMI cable, keyboard and mouse will be required every time you connect the Raspberry Pi. 
* When you access the Raspberry Pi, install a good Python editor like Geany or Thonny. It is possible to install Visual Studio Code, but we had performance issues since our Raspberry Pi only had 2GB RAM
* We used Picamera2 libraries to access the camera. The instructions to follow are all over the place. Follow these instructions carefully to get the camera setup. 
  * Access Raspberry Pi and open the terminal window
  * [Update all the software](https://www.raspberrypi.com/documentation/computers/os.html#update-software) running on the Raspberry Pi. You may need to do this every few weeks 
  * Picamera2 libraries would be preinstalled as part of the full software update. However, run ``sudo apt install -y python3-picamera2` on the terminal to install the libraries, if they are not installed. If they were installed this will NOT redo it. [Detailed instructions here](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
  * Now, we need to configure the settings to use the Sainsmart Wideangle camera which uses the Omnivision 5647 sensor. 
    * Open the firmware config by entering the following command on the terminal `sudo nano /boot/firmware/config.txt`
    * Change `camera_auto_detect=1` to `camera_auto_detect=0`
    * Under the `[all]` section, add the line `dtoverlay=ov5647`
    * Press `Ctrl+x` to save the file and exit the program
  * Test the camera with one of these commands - `rpicam-hello` or `libcamera-hello`
* Download the [`obs_ch.py`](/src/obs_ch.py) file from the `src` folder
* Ensure you can run this program by opening terminal and running `python obs_ch.py`. This should start running the program. If it does not, open the file and check if `DRAW` variable is set to `True` to troubleshoot.

* To automatically run this program when Raspberry Pi boots up, it needs to be part of the crontab. Follow these instructions to set it up
  * Open the crontab with the command `sudo crontab -e`
  * Add the python program to run upon bootup by adding this statement to the end of the crontab `@reboot /usr/bin/python3 </path/to>/obs_ch.py >/dev/null 2>&1 &`
  `Tip` - The above will redirect the standard print output and errors to `/dev/null` which is not useful if you want to access them. If you want debug print messages to be saved, ensure you create a log file with the command `sudo touch /dev/cronlog` and adding this file path to the above crontab statement instead. 

* Now you are all setup. If you reboot your Raspberry Pi, `obs_ch.py` file will start running. If it is not, check the `/dev/cronlog` for error messages to troubleshoot the problem.

**Getting `pi2mb_motors_control.py` to run on the Microbit**

* Note that the Microbit should be physically connected to the device you are using to upload the code, with a micro USB cable. It can be connected either to your workstation, or your Raspberry Pi. 
* The instructions to load this program is relatively easier because we followed the simpler method by accessing https://makecode.microsoft.org using the Chrome browser on the Raspberrry Pi (or any browser on your laptop). There are alternatives to use the Thonny Python editor or Visual Studio code, but we found it too tedious just to get the Microbit connected to take the program. 
* Open a new Python program on makecode by clicking on **New Project**. Give it a name and select **Python Only** in the code options drop-down. Then click on **Create** button.
![Creating a new Python program on makecode](/other/image.png)
* When the program is open, copy the entire content of [`pi2mb_motors_control.py`](/src/pi2mb_motors_control.py) from the `src` folder, on to the new Python program on makecode.
* Click on **Download** button to deploy the binary code to Microbit. You will hear an audible beep when the program is loaded to indicated the Microbit has successfully received the code (***Note:*** The audible beep is not a default behavior. We included the beep as a way for the Microbit to convey its readiness everytime it starts or is reset)
* That is all! When connected to the Raspberry Pi over USB cable (as shown in the [schematic](/schemes/WRO%20Future%20Engineeers%202025%20-%20Component%20Schematic.png) and powered on, the program will be ready to transmit to and receive data from the Raspberry Pi and move your car. 









