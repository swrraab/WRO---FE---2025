# Approach


## Considerations
- Since we are a rookie team and the time is short, several important decisions were to be made to ensure the team is able to learn and compete in the available time
- We will go with the tried and trusted method to build and program the car
  - Use an off-market car chassis and modify as needed
  - Add 3D printed parts to mount sensors, Micro-Controller Unit (MCU), Single-board Computer (SBC) and Power unit.
  - Use of a MCU connected to distance sensor for obstacle detection, Color sensor for line detection and  Inertial Movement Unit (IMU) for navigation
  - Use  of a Raspberry Pi with a camera for vision in the Obstacle Challenge
  - Python for programming both MCU and Raspberry Pi

Note: AI tools like ChatGPT and Perplexity were used only for researching ideas. Base code was gathered from various sources on the internet and altered to suit our choice of platform and solution.


## Choice of MCU

- One of the early decisions to be made was the choice of MCU. Most teams seem to use Arduino Uno. Some teams use other variants of Arduino such as Nano or Mega. Some others use Lego platforms such as EV3 or Spike. We’ve also seen NVidia Jetson being used. 
- However, we wanted a cost effective and easily learnable platform. One of the forerunners in this decision was the Micro:bit (MB) for several reasons: 
  - We were already familiar with MB since we learned to use it at school - although it was just the basics
  - MB has a smaller form factor
  - MB has several inbuilt sensors, most importantly it has an Inertial Movement Unit (IMU) sensor
  - We did some research and found several articles supporting our decision
    - https://www.codeadvantage.org/coding-for-kids-blog/micro-bit-vs-arduino 
    - https://picobricks.com/blogs/info/microbit-vs-arduino

- So we made the decision to experiment with MB first and if that doesn’t work well, we can always switch to Arduino
- Most important consideration in the experimentation with MB was to find a shield that offers all the connectivity we need
- We found a shield for Micro:bit that offered all the ports we needed and result of experiment are documented below
  - [X] Connect to a DC motor
  - [X] Connect to a Servo motor
  - [X] Connect to 2 distance sensors 
  - [X] Connect to 1 or 2 color sensors 
  - [X] Interface with Raspberry Pi over I2C or UART

## Choice of SBC

- We already decided that we will use Raspberry Pi with a camera for vision tracking since that is the most popular solutions
- Some teams have used other products like PixyCam, HuskyLens etc to enable vision directly on their Arduino.
- But for the same cost, we wanted to learn more by using a Raspberry Pi since there is a lot of resources available and vision tracking is exciting (if we are able to learn it in the available time)
- We did some research and came across OpenCV and YOLO as popular libraries. There are plenty of support resources to load either library onto a Raspberry Pi 4 with a basic camera module.


## Connection from SBC (Raspberry Pi) to transmit navigation decisions to the MCU (Micro:bit)

- The SBC should use the vision data and compute the direction of travel - Turn left, Turn right, Go forward
- SBC will communicate the navigation data to the MCU over serial connection
- MCU will then combine the navigation data from the SBC and the sensor data to make decisions to drive

