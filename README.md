# **2025 WRO Future Engineers Competition** 
# Team **Pink Boba Pearls** 🌸🧋🫧
This repository is for the 2025 WRO Future Engineeers competition. We are a team of 2 high-school girls from Ontario, Canada 🇨🇦 We are passionate about all things engineering - specifically computer science 💻 and space 🚀 

This repository has the below folders
1. `docs` - Contains the Engineering Documentation
2. `models` - Contains STL files we used for our 3D prints 
2. `other` - Contains miscellanous files used for README.md
3. `schemes` - Contains our connection schematic and power distribution schematic
4. `src` - Contains our source code 
5. `t-photos` - Contains team photos
6. `v-photos` - Contains vehicle photos
7. `videos` - Contains links to vehicle demo youtube videos`

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









