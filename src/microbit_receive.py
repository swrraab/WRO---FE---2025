from microbit import *
import music

# play music on start for confirm microbit initialization
music.play(music.tone_playable(Note.C, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)

# set parameters to read serial data from the usb port
serial.redirect_to_usb()
serial.set_baud_rate(BaudRate.BAUD_RATE115200)
serial.set_rx_buffer_size(1)

# TCS34725 color sensor is set t0 collect light input for 100 milli secs
envirobit.set_colour_integration_time(100)

# microbit mshield will set ports S1 to S4 to control servo motors
mShield.set_s1_to_s4_type(mShield.S1ToS4Type.SERVO)

# initializing port S1 to control a continuous servo 
# Need to change this to a 90 degree servo or a regular DC motor if needed
mShield.continuous_servo_control(mShield.ServoIndex.S1, 10)

# initialize the servo motor to be at 90 degree position (in a 180 degree setup)
# this will allow the car to 
# turn right if the servo is moved to position 0 and
# turn left if the servo is moved to position 180
mShield.extend_servo_control(mShield.ServoIndex.S1, mShield.ServoType.SERVO180, 90)

# variable to store the bit received from the Raspberry Pi's vision based direction control
# 0 - Go straight. 1 - Turn Right. 9 - Turn Left.
data_in = ''

# Variable to store car direction
# 0 is clockwise. 1 is counter-clockwise
direction = 0

# this will count the number of times the car sensed the orange line
# 4 milestones will be one lap. 12 milestones will be 3 laps
milestone = 0

# this is a temporary setup to test the servo response
def on_button_pressed_b():
    mShield.extend_servo_control(mShield.ServoIndex.S1, mShield.ServoType.SERVO180, 0)
    basic.pause(500)
    mShield.extend_servo_control(mShield.ServoIndex.S1, mShield.ServoType.SERVO180, 90)
input.on_button_pressed(Button.B, on_button_pressed_b)

# this will perform a lap
def go_lap():
    basic.pause(1000)

    # If orange is the first line to be read
    if milestone == 0:
        direction = 0 if envirobit.get_red() > 100 else 1


    # Read serial uart data from Raspberry Pi and control the servo rotation
    try:

        serial.write_numbers([envirobit.get_red(),
            envirobit.get_green(),
            envirobit.get_blue()])

        data_in = serial.read_string()
        # basic.show_string(data_in)
        if int(data_in) == 1:
            mShield.extend_servo_control(mShield.ServoIndex.S1, mShield.ServoType.SERVO180, 0)
            basic.show_arrow(ArrowNames.NORTH_EAST)            
        elif int(data_in) == 9:
            mShield.extend_servo_control(mShield.ServoIndex.S1, mShield.ServoType.SERVO180, 180)
            basic.show_arrow(ArrowNames.NORTH_WEST)            
        else:
            mShield.extend_servo_control(mShield.ServoIndex.S1, mShield.ServoType.SERVO180, 90)
            basic.show_arrow(ArrowNames.NORTH)
        
        
    except:
        pass

def do_12_laps():
    while (milestone <= 12):
        go_lap()

# input.on_button_pressed(Button.A, do_12_laps)

basic.forever(go_lap)

###################

def on_button_pressed_a():
    mShield.extend_pwm_control(mShield.PwmIndex.S1, 0)
    mShield.extend_pwm_control(mShield.PwmIndex.S2, 80)
    basic.pause(200)
    mShield.extend_pwm_control(mShield.PwmIndex.S2, 0)
    basic.pause(100)
    mShield.extend_pwm_control(mShield.PwmIndex.S1, 80)
    basic.pause(200)
    mShield.extend_pwm_control(mShield.PwmIndex.S1, 0)
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_button_pressed_b():
    mShield.extend_pwm_control(mShield.PwmIndex.S3, 0)
    mShield.extend_pwm_control(mShield.PwmIndex.S4, 80)
    basic.pause(1000)
    mShield.extend_pwm_control(mShield.PwmIndex.S4, 0)
    basic.pause(200)
    mShield.extend_pwm_control(mShield.PwmIndex.S3, 80)
    basic.pause(1000)
    mShield.extend_pwm_control(mShield.PwmIndex.S3, 0)
input.on_button_pressed(Button.B, on_button_pressed_b)

envirobit.set_colour_integration_time(0)
direction = 0
milestone = 0
mShield.set_s1_to_s4_type(mShield.S1ToS4Type.PWM)
music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)),
    music.PlaybackMode.UNTIL_DONE)
while milestone == 0:
    if envirobit.get_red() > 100:
        direction = 0
        milestone = 1
    elif envirobit.get_blue() > 100:
        direction = 1
while milestone <= 12:
    pass

def on_forever():
    basic.show_number(sonar.ping(DigitalPin.P1, DigitalPin.P0, PingUnit.CENTIMETERS))
basic.forever(on_forever)

