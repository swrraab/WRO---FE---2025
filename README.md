# **2025 WRO Future Engineers** - Team **Pink Boba Pearls** 🌸🧋🫧
This repository is for the 2025 WRO Future Engineeers competition. We are a team of 2 high-school girls from Ontario, Canada 🇨🇦 We are passionate about all things engineering - specifically computer science 💻 and space 🚀 

This repository has the below folders
    
    1. models - # Contains STL files we used for our 3D prints 
    2. other - # This has nothing
    3. schemes - # Contains our connection schematic and power distribution schematic
    4. src - # Contains our source code 
    5. t-photos - # Contains team photos
    6. v-photos - # Contains vehicle photos
    7. videos - # Contains links to vehicle demo youtube videos

## The Hardware
1. **Microcontroller - [Microbit v2](https://microbit.org/buy/bbc-microbit-single/):** Together with the Siyeenove Mshield Pinout board - For controlling drive motor and steering servo motor based on input from the Raspberry Pi
2. **Single Board Computer (SBC) - [Raspberry Pi 4 Model B 2GB](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/):** Vehicle mobility control
---

We also used
1. Sainsmart 160 degree wideangle 5PM camera for Raspberry Pi
2. Lego Technic - to build the chassis
3. 12V Lithium battery power supply
4. 12v to 5V Step-down converter - To supply power to Raspberry Pi and Microbit
5. L298N Motor Driver - To drive the 9V Lego DC motor
6. 9V Lego Motor
7. SG90 Micro Servo Motor
8. Various cables for power connections to the devices, USB cable for serial connection between Microbit and Raspberry Pi, and wires to transmit data from Microbit to the motors.  

Refer to the component schematic to connect all the above hardware together to make the car

[Component Schematic](/schemes/WRO%20Future%20Engineeers%202025%20-%20Component%20Schematic.png)

## The Software

There are 2 important programs

1. `obs_ch.py` - loaded to the Raspberry Pi to process the vision input from the camera
2. `pi2mb_motors_control.py` - loaded to the Microbit to drive the pi2mb_motors_control

