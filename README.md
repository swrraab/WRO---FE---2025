# **2025 WRO Future Engineers Competition** 
# Team **Pink Boba Pearls** 🌸🧋🫧
This repository is for the 2025 WRO Future Engineers competition. We are a team of 2 high-school girls from Ontario, Canada 🇨🇦 We are passionate about all things engineering - specifically computer science and space 

This repository has the below folders
1. [**`models`**](/models) - Contains STL files we used for our 3D prints 
2. [**`other`**](/other) - Contains miscellanous files used for README.md
3. [**`schemes`**](/schemes) - Contains our connection schematic and power distribution schematic
4. [**`src`**](/src) - Contains our source code 
5. [**`t-photos`**](/t-photos) - Contains team photos
6. [**`v-photos`**](/v-photos) - Contains vehicle photos
7. [**`video`**](/video) - Contains links to vehicle demo youtube videos

---

# Table of Contents - Engineering Documentation
* [**The Problem**](#the-problem)
* [**The Idea**](#the-idea)
* [**Chassis**](#chassis)
	* [**Iteration 1**](#iteration-1)
	* [**Iteration 2**](#iteration-2)
	* [**Iteration 3 - Final**](#iteration-3---final)
* [**3D printed parts**](#3d-printed-parts)
* [**System control**](#system-control)
	* [**To see or to sense?**](#to-see-or-to-sense?)
* [**Mobility Control**](#mobility-control)
	* [**Drive Motor**](#drive-motor)
 	* [**Steering Servo**](#steering-servo)
	* [**Choice of micro controller - Microbit**](#choice-of-micro-controller-microbit)
	* [**Choice of SBC - Raspberry Pi**](#choice-of-sbc-raspberry-pi)
 	* [**Choice of Camera**](#choice-of-camera)
* [**Power Management**](#power-management)
* [**Bill of Materials**](#bill-of-materials)
* [**Program Logic for mobility control**](#program-logic-for-mobility-control)
	* [**Microbit - pi2mb_motors_control.py**](#microbit---pi2mbmotorscontrolpy)
	* [**Raspberry Pi - obs_ch.py**](#raspberry-pi---obschpy)
	* [**Loading the software on to the hardware**](#loading-the-software-on-to-the-hardware)

---

# The problem

For WRO Future Engineers 2025, the challenge is to design an autonomous vehicle that can
* Complete 3 laps around an open course without incurring penalties
* Complete 3 laps around an obstacle courses without bumping into the red and green blocks, while navigating around them as per the rules
* Optionally start from a parking area at the start of the obstacle challenge
* Optionally parallel park in the parking area at the end of the obstacle challenge

Additionally, there were constraints imposed on the field setup, size of the robot and the drive train and steering mechanisms that can be used.

---

# The Idea
We are a new team, and we needed to build a car that suits our abilities

To be successful, we will need to go with:
1. A simple chassis - Either buy one, or modify an existing chassis
2. Use Raspberry Pi to be the brain, and a camera with OpenCV library to be the eyes
3. Use Arduino or Microbit for micro controller
4. Use ultrasonic sensor, color sensor and IMU sensor as needed
5 Use simple power management setup to distribute power to micro processor, micro controller and the DC Motor

This journal documents our journey and the decisions we made for each component as we iterated to the final working product

---

# Chassis
The chassis underwent 3 iterations to the final product

![chassis iterations](https://github.com/swrraab/WRO---FE---2025/blob/main/other/Car_evolution_iterations.png)

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
* Lego chassis allowed us to mount motors and camera with 3D printed attachment that are compatible with the Lego technic beam dimensions

### Disadvantages
* The final chassis looks bulky. There is room for optimization
* Heavier than the other 2 chassis at 900 gms, however it is still within allowed weight

![Car Composite View](https://github.com/swrraab/WRO---FE---2025/blob/main/v-photos/Car%20Images.png)

**Note:** Full resolution pictures of the car can be downloaded from the [**`v-photos`**](/v-photos) folder

---

# 3D printed parts
Since we used a Lego Chassis, we used 3D printed parts made from Carbon Fiber infused PLA to mount the following
* **The servo motor to the front wheels for steering**
    * Initially we tried to 3D print our own design.
    * Later, we found a 3D file that we found on [Thingiverse](https://www.thingiverse.com/thing:4303585) that worked better for our purpose
	![Servo Mount](https://github.com/swrraab/WRO---FE---2025/blob/main/models/s90%20Servo%20Mount%20v1_small.PNG)

* **The BLDC motor to the drive axle**
	* We 3D printed a custom mount for the BLDC motor that connects to Lego Technic beams and fits the chassis dimensions
 
   ![Brushless DC Motor Mount](https://github.com/swrraab/WRO---FE---2025/blob/main/models/bldc_motor_mount_small.png)
   
	* We also 3D printed a connector to connect the motor shaft to the Lego axle to which the drive gear was attached

   ![Motor Axle Connector](https://github.com/swrraab/WRO---FE---2025/blob/main/models/motor%20axle%20connector_small.PNG)

* **TOF200C Distance Sensor to the back of the Lego Chassis**
    * It is a 2 part 3D model - One that holds the TOF200C sensor and a lid that holds in place with a bit of instant glue
    * This model too mounts on to Lego Technic beams and connects to the back of the chassis

	![TOF200C Distance Sensor mount](https://github.com/swrraab/WRO---FE---2025/blob/main/models/TOF200C%20enclosure_small.PNG)

* **Wide angle camera**
    * This is to attach to the Lego chassis, and to hold the camera at a specific angle.
    * This design which connects to a standard Lego Technic beam allowed us to experiment with various heights and mount angles before we got it right.
  
	![Camera Mount Extension](https://github.com/swrraab/WRO---FE---2025/blob/main/models/Camera%20Mount%20Extension_small.png)
	![Camera Mount](https://github.com/swrraab/WRO---FE---2025/blob/main/models/Camera%20Mount%20small.png)

**Note:** Full resolution pictures and 3D models can be downloaded from the [**`models`**](/models) folder

---

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
![Iteration 1 Schematic](https://github.com/swrraab/WRO---FE---2025/blob/main/schemes/schematic%20early.png)

### Iteration 2 - Computer Vision
* In our subsequent research we were able to find inspiration to do it all with just one wideangle camera. We tested it out and found success - as explained in the program logic section
* For the final iteration, we used the wideangle camera to detect walls, blocks and lines while driving forward and a TOF200C sensor in the back to assist with reverse parking

![Iteration 2 Schematic](https://github.com/swrraab/WRO---FE---2025/blob/main/schemes/Component_Schematic.png)

![Circuit Schematic](https://github.com/swrraab/WRO---FE---2025/blob/main/schemes/Circuit_Schematic.png)

# Power Management

Initially, as we were testing vision, all the components were powered with a wall outlet power source. Once we fully understood the power requirements, we found a 12V rechargeable power supply that can supply 3A of current to be able to concurrently supply power to
* Raspberry Pi 4B - Needs 5V 2.5A
* Siyeenove shield for the Microbit - Needs 5V 0.5A
* 12V BLDC motor - Needs 12V 0.13A (0.35A at stall)

We used a 12V to 5V step-down power converter to supply 5V power to the Raspberry Pi and the Microbit shield.

The Microbit itself did not require separate power since it was powered by the shield.

![Power Distribution](https://github.com/swrraab/WRO---FE---2025/blob/main/schemes/Power_Management.png)

---

# Mobility Control
## Drive motor
* In the design that was employed for the Canadian competition, we used Lego 9v DC motor because it had the ideal torque and speed characteristics we needed. This motor was paired with a L298N motor driver with 12v power input from the battery and PWM control input from the Microbit to control the 9V Lego DC motor. However this motor offered no feedback and we had no control over the speed. For this reason, we couldn’t use it to get out of parking or the perform parallel parking
* In the current design, we use a 12V BLDC (Brushless DC) motor which has the following characteristics
	* Inbuilt motor driver. No external driver required
	* Uses 12V power supply
	* Inbuilt planetary gearbox with a 34:1 reduction which provides 130RPM at no load
	* 550gm/cm of torque which is ideal for our use
	* Draws 130mA of current nominally, 350mA of current at stall which can be supported by our power supply
	* Inbuilt encoder for feedback
	* Separate inputs for speed and direction control with PWM signals
 * This DC motor is coupled with the drive axle using lego gears achieving a 1.5 reduction thus increasing torque. This is unintended. We have more torque than we need. We would've favored more speed. However, the chassis design limited us from using other gears

During the course of open and obstacle challenge runs, the motor runs at full speed - and it feels like it is not enough because of the unintended gear reduction. Proportional speed control is employed only when getting out of parking and when parallel parking

## Steering Servo
* Used SG90 180 degree servo motor with **analog signal** from the Microbit.
    * 90 degree points the wheels straight
    * 15 degree is the farthest right steering, limited by the code
    * 165 degrees is the farthest left steering, limited by the code

During the lap runs, the steering angles are determined by a proportional derivative control logic based on
* Whether there are blocks, the position and proximity of the blocks
* When there are no walls, the relative position of the camera between the walls

Detailed explanation of this logic is provided in the code.

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
Siyeenove Microbit shield allows us to conveniently interface with the Servo motor via the P0 pin. We use analog signal to position the servo motor. The shield also accepts 5V input which it uses to drive the servo.

### Microbit Serial connection with Raspberry Pi
The Microbit connects with the Raspberry Pi via a USB cable for serial data transfer. This serial data connection is used by the Raspberry Pi to achieve bi-directional data exchange with the Microbit
* TX to Raspberry Pi - Control signals to start and stop the car operation
* RX from Raspberry Pi - Steering and Servo control values

### Use of Microbit buttons
* Button A is programmed to start and stop the car. When car is stopped by pressing the A button, pressing it again will commence a new run
* Button B is the kill command. It is programmed to stop all motor activity by signalling the Raspberry Pi to exit the Python program execution

### Function Outline
* As soon as it starts, it initializes the servo direction to 90 (which keeps the car straight)
* It awaits signal from the Raspberry Pi to confirm its program has started successfully. When it receives the confirmation, it displays an 'S' on the LED array
* When the user presses the 'A' button, it transmits a 'go' signal to the Raspberry Pi and awaits acknowledgement from the Raspberry Pi. When the acknowledgement is received, it displays a '+' on the LED array indicating that the car has started.
* As the car runs, Raspberry Pi transmits the servo steering turn data as byte stream which the Microbit will convert to numerical data
* The servo turn angle is sent as analog signal to the servo motor directly. The 5V input required by the Servo is supplied by the Siyeenove Mshield board.
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
* We tried driving the servo with Raspberry Pi directly, but that didn’t go well. The servo turns were jittery and the Raspberry Pi shutdown whenever the Servo experienced quick successive movements. So we decided to have the Microcontroller handle the servo control with the vision input parameters from the Raspberry Pi

## Choice of camera
**Iteration 1: Raspberry Pi Camera V2**

We used this until 3 weeks before the canadian competition simply because we already had it and it seemed to work fine for the open challenge. We were able to get 40 fps processing speeds with it but that didn’t really matter to us.

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

---

# Bill of Materials
We experimented with many boards and components before settling on our final design. The below list is for the final design only.

| Part | Reference Cost - As of Sep 1, 2025 - Taxes not included | Purchase Link for Future Reference |
| ------------ | ------------: | ------------ |
| **Micro:Bit** |  |  |
| Micro:Bit | $48.59  |  [amazon.ca](https://www.amazon.ca/KEYESTUDIO-MICROBIT-V2-2-KIT-Beginners/dp/B0BNKTGGB7) |
| Micro:Bit Motor Shield (DC Motor and Servo) | $16.00 | [amazon.ca](https://www.amazon.ca/dp/B0F24V8X31) |
| **Raspberry Pi**  |   |   |
| Raspberry Pi 4  | $62.95  | [pishop.ca](https://www.pishop.ca/product/raspberry-pi-4-model-b-2gb/)  |
| Sainsmart Wideangle 5MP Camera 160 degree FoV  | $16.99  | [amazon.ca](https://www.amazon.ca/SainSmart-Fish-Eye-Camera-Raspberry-Arduino/dp/B00N1YJKFS)  |
| **Other Accessories to build the car**  |   |   |
| 9v-12 Battery bank  | $41.79  | [amazon.ca](https://www.amazon.ca/dp/B01M7Z9Z1N)  |
| 12V to 5V Step-down converter  | $5.28  | [aliexpress.com](https://www.aliexpress.com/item/1005006655110785.html)  |
| 12V Brushless DC motor with Encoder  | $17.43  | [robotshop.ca](https://ca.robotshop.com/products/e-s-motor-24mm-brushless-dc-gear-motor-12v-130rpm?qd=7ce66187395fa1fb2558d4bb6c21548c)  |
| SG90 Servo motors  | $19.99   | [amazon.ca](https://www.amazon.ca/dp/B0CP98TZJ2)  |
| Short USB to USB-C cable  | $10.99  | [amazon.ca](https://www.amazon.ca/etguuds-Charging-Charger-Braided-Compatible/dp/B08933P982)  |
| Short USB to Micro-USB cable  | $8.99  | [amazon.ca](https://www.amazon.ca/Micro-CableCreation-High-Speed-Triple-Shielded/dp/B013G4D2OM)  |
| Lego Parts to build the chassis  |   |   |
| 3D printed parts to complete the chassis  |   |   |
| **Total**  | **\$256.88**  |   |

---

# Program Logic for mobility control

## Microbit - pi2mb_motors_control.py

### Summary
* Microbit powers up, then plays a tone, initializes motors & serial.
* **Button A** sends "go" to R-Pi (start/stop car).
* **Button B** sends "quit" to R-Pi (exit program).
* **Raspberry Pi** to **Microbit** Serial Connection data transmission via USB which needs to be a 4 byte character including the delimiting newline (\n) character:
    * Sends **status codes ("str", "stp", etc.)** → Microbit shows icons.
    * Sends **servo angle value (e.g., "120")** → Microbit drives servo angle.
* Servo Motor turn angle is controlled using analog signals on the P0 pin via the **Siyeenove mShield**

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

---
### Startup Signal
```
music.play(music.tone_playable(Note.C, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)
```
As soon as the Microbit is started or reset, it plays a tone to indicate the Microbit is active.

---
### Serial Communication Setup
```
serial.redirect_to_usb()
serial.set_baud_rate(BaudRate.BAUD_RATE115200)
serial.set_rx_buffer_size(4)
```
* Serial connection parameters are initialized for Microbit to exchange commands/data with the Raspberry Pi.
* Note the buffer size of 4. This means all the inputs received from the Raspberry Pi should be 4 characters including the newline character used a delimiter. The first 3 characters are the numerical value of the steering angle
---
### Default Values
```
deg = 90
pins.servo_write_pin(AnalogPin.P0, deg)   # Servo straight
```
* Servo is set to **90° (straight)**
---
### Button Controls
```
def on_button_pressed_a():
    basic.pause(100)
    serial.write_string("go")

input.on_button_pressed(Button.A, on_button_pressed_a)
```
* When **Button A** is pressed → Microbit sends "go" over serial to R-Pi.
* R-Pi decides whether to start/stop the car.
---
### Main Loop
```
while True:
    try:
        data_in = serial.read_until(serial.delimiters(Delimiters.NEW_LINE))
```
* Continuously listens for messages from the R-Pi.

**Status Messages from R-Pi**
```
if (data_in[0] == "s"):
    if data_in == "str":   # Show "+" icon
    elif data_in == "stp": # Show "-" icon
    elif data_in == "sss": # Show ‘S’ indicating successful start up
```
* If the incoming data starts with "s", it’s a status message.
* Different LED patterns indicate whether the car is:
    * `S` indicates Raspberry Pi Ready (also a tribute to the initials of the team member names, Swara and Shadya)
    * `+` indicates Starting
    * `-` indicates Stopping

**Motor/Servo value parsing**
```
else:
    deg = int(data_in[:3])-100
```
* If it’s not a status message, it’s a **servo control value** (numbers only).
* The first 3 characters → servo angle (shifted by 100).
* Example: `"150"` → servo = 150-100 = 50°

**Servo control**
```
    pins.servo_write_pin(AnalogPin.P0, deg)
```
* Send `deg`, the servo turn angle as analog input to the P0 Pin connected to the Servo motor
* **Potential Improvements:** Ideally, we would want to have a PD loop to ensure the steering turns are smooth, but with the Microbit and SG90 servo we don’t have a way to implement a closed loop feedback system. So, we had to forgo PD control at the component level and favor the implementation of PD control in the Raspberry Pi before it sends the values to the Microbit.

### Getting `pi2mb_motors_control.py` to run on the Microbit

* Note that the Microbit should be physically connected to the device you are using to upload the code, with a micro USB cable. It can be connected either to your workstation, or your Raspberry Pi. 
* The instructions to load this program is relatively easier because we followed the simpler method by accessing https://makecode.microsoft.org using the Chrome browser on the Raspberrry Pi (or any browser on your laptop). There are alternatives to use the Thonny Python editor or Visual Studio code, but we found it too tedious just to get the Microbit connected to take the program. 
* Open a new Python program on makecode by clicking on **New Project**. Give it a name and select **Python Only** in the code options drop-down. Then click on **Create** button.
![Creating a new Python program on makecode](/other/image.png)
* When the program is open, copy the entire content of [`pi2mb_motors_control.py`](/src/pi2mb_motors_control.py) from the [`src`](/src) folder, on to the new Python program on makecode.
* Click on **Download** button to deploy the binary code to Microbit. You will hear an audible beep when the program is loaded to indicated the Microbit has successfully received the code (***Note:*** The audible beep is not a default behavior. We included the beep as a way for the Microbit to convey its readiness everytime it starts or is reset)
* When connected to the Raspberry Pi over USB cable (as shown in the [schematic](/schemes/WRO%20Future%20Engineeers%202025%20-%20Component%20Schematic.png) and powered on, the program will be ready to transmit to and receive data from the Raspberry Pi to start your car. 

---

## Raspberry Pi - obs_ch.py
### Pseudo code for keeping the car between the walls and to avoid obstacles
* Use the blue and orange lines to determine the direction of the lap (clockwise or counter clockwise) and to count if 3 laps have been achieved (by counting 12 lines of either color)
* When the number of lines counted is less than 12
* Look for red or green blocks in the center of the image up to the bottom of the image.
* If red or green block is found, find the biggest blocks respectively
	* Determine the direction of turn (left for green blocks; right for Red blocks)
	* Apply proportional logic to determine the amount of turn by evaluating the X and Y coordinates of the block (nearer blocks will need tighter turns)
	* When the turn values are determined for both red and green blocks, use the biggest turn value since that would apply to the nearest block
* If red or green block is not found (as when making turns or in open challenge conditions) look for the amount of black on either edges of the lower part of the image received from the camera
	* Use proportional derivative logic to determine the amount of steering. Error is the difference in the black areas of right and left walls. Greater black on the right side will steer the car to the left, and vice versa
* During the laps, if a wall or block is detected to be too close, make a small reverse movement and reattempt.
* At the end of 3 laps, the car will attempt a parallel parking manuever by reverse parking into the parking area, guided by the camera and the TOF200C sensor
---
### Important Libraries Used

* **`Picamera2`** - This is to read images from the Sainsmart OV5647 camera connected to the Raspberry Pi
* **`cv2`** - This is OpenCV library for image processing to determine relative position and size of objects seen by the camera
* **`serial`** - To transmit servo control values to the Microbit over serial port
* **`board`** - Provides a hardware abstraction layer for accessing the General Purpose Input/Output (GPIO) pins (in the context of Adafruit CircuitPython)
* **`busio`** - Provides a standardized, high-level interface for interacting with various hardware communication protocols, I2C in this case (in the context of Adafruit CircuitPython)
* **`adafruit_vl53l0x`** - Provides an user-friendly interface to interact with the VL53L0X Time-of-Flight (ToF) distance sensor

### Defining important global constants and variable

**HSV color thresholds**

These define which pixels belong to a given color range. HSV is used because it’s more reliable than RGB in challenging light conditions where the Hue of a color falls within a specific range. An upper range and lower range are defined to create a mask which filters these colors
* **Black** - for walls and lines.
* **Green and Red** - for block detection.
* **Blue and Orange** - for line detection

We used a HSV color palette and converted the actual HSV values to OpenCV values (to be contained within the 0-255 range) using the below formula
* **H (Hue)** - 0 to 360 values converted to 0-180 values by dividing by 2
* **S (Saturation)** - 0-100 values converted to 0-255 values by multiplying by 2.55
* **V (Value)** - 0-100 values converted to 0-255 values by multiplying by 2.55

**Regions of interest**
We split the camera view into smaller zones, each with a specific purpose.

_For block detection_
* Rectangle in the **center** of the image.
* Used to look for green/red blocks.
  
_For wall following (PD controller)_
* Used to make two rectangles:
    * Left zone (pd_l) = from 0 to 30 along the X axis on the far left.
    * Right zone (pd_r) = from 610 to 640 along the X axis on the far right
    * Used to measure wall area left vs right.
* Both at the same height (220–480).

_For line counting_
* Small horizontal strip at the bottom of the frame.
* Used to detect black crossing lines (to count laps/checkpoints)

---

### Frames class
This is a helper class for working with specific regions of the camera image by dividing its camera view into regions (Frames), and each region specializes in finding a specific thing (wall, line, block).
* A `Frames` object = “a rectangular window” into one part of the camera image.
* It knows:
    * **Where** to look (rectangle coordinates).
    * **What color** to look for (HSV range).
* It can:
    * Crop & process that rectangular window.
    * Detect contours (outlined regions) of desired colors.

### pd() function
Uses a **PD controller** to make the steering smooth, not jerky. The logic looks at how much wall is on the **left** vs **right**.
* If the right wall looks closer → steer left
* If the left wall looks closer → steer right.
* If both are equal → go straight.

![Wall detection frame](https://github.com/swrraab/WRO---FE---2025/blob/main/other/wall%20detection%20frame.png)

### pd_block() function
* Looks for either a green block or a red block in a predefined region of the camera frame.
* If a block is found, it calculates **how far** the block is from the desired position.
* It then produces a control signal (e_block) that tells the car how much to adjust its steering when approaching the block.
	* For red blocks, the “target x” is the right side of the detection zone.
	* For green blocks, the “target x” is the left side of the detection zone.
	* This means the car is supposed to go toward the right for red blocks and toward the left for green blocks..
	* These are scaled by tuning constants K_X and K_Y.
	* Both are combined into one error signal e_block. This makes the car steer differently depending on the block’s color and the car’s driving direction.

![Color block detection frame](https://github.com/swrraab/WRO---FE---2025/blob/main/other/block%20detection%20frame.png)

### restart() function
* This function is used to reset all the variables including the flags and timers. 
* This is used when the car needs to stop and start a fresh run without exiting the main loop.

### Main code (including the main loop while True)

* Initialize image areas to detect walls and color blocks
* Main Loop (while True)
	* If message is "go" from the Microbit, execute the below logic
   	* At the end of each loop, the calculated steering values are sent to Microbit for turning
   	* DC Motor control PWM values are handled by the Raspberry Pi
	
* Anytime during the run, stop and reverse if Wall is detected

* Checks for red or green blocks:
	* If block found → calculate steering correction for red and green blocks (u_red or u_green) and determine which value is most influential and use that as the steering value.
* If no red or green blocks are found in the frame (as in Open Challenge condition)
	* Update the wall detection areas on either edges and use the wall-following (pd()) function to calculate the steering values.

* Detects blue and orange line markers on the floor and keep count
* Also determines car’s driving direction based on the line color that is detected in the very first section crossing:
	* Blue line → counter-clockwise (CCW).
	* Orange line → clockwise (CW).

* The count of lines is used for navigation and to decide when to stop.

### Getting `obs_ch.py` to run on the Raspberry Pi

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
