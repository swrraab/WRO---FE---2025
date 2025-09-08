from microbit import *
import music
import mShield

# Play music to indicate the Microbit is active
music.play(music.tone_playable(Note.C, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)

# Initilize serial connection parameters
serial.redirect_to_usb()
serial.set_baud_rate(BaudRate.BAUD_RATE115200)
serial.set_rx_buffer_size(7)

# Set the Siyeenove Shield S ports to PWM control
mShield.set_s1_to_s4_type(mShield.S1ToS4Type.PWM)

# Initialize default values
deg = 90
speed = 0

# Set servo to align straight
pins.servo_write_pin(AnalogPin.P0, deg)

# Set drive motor speed to zero
mShield.extend_pwm_control(mShield.PwmIndex.S3, 0)
mShield.extend_pwm_control(mShield.PwmIndex.S4, speed)

# When Button A is pressed send the "go" signal to R-Pi
# In the R-Pi this either starts the car or stops the car
# based on the current state of the car
# Feeback from the R-Pi is handled in the while loop below
def on_button_pressed_a():
    basic.pause(100)
    serial.write_string("go")
    
input.on_button_pressed(Button.A, on_button_pressed_a)

# When Button B is pressed, send "quit" signal to the R-Pi
# And show a pattern on the screen indicating the quit signal
def on_button_pressed_b():
    basic.pause(100)
    serial.write_string("quit")
    
input.on_button_pressed(Button.B, on_button_pressed_b)


# def on_forever():
while True:
    try:
        # Read serial uart data from Raspberry Pi
        data_in = serial.read_until(serial.delimiters(Delimiters.NEW_LINE))
        
        # Depending on the feedback from the R-Pi actions, display
        # patterns on the screen to indicate car status
        if (data_in[0] == "s"):
            if data_in == "startt":
                basic.show_leds("""
                    . . . . .
                    . . # . .
                    . # # # .
                    . . # . .
                    . . . . .
                    """)
            elif data_in == "stoppp":
                basic.show_leds("""
                    . . . . .
                    . . . . .
                    . # # # .
                    . . . . .
                    . . . . .
                    """)
            elif data_in == "ssssss":
                basic.show_leds("""
                    . # # # #
                    # . . . .
                    . # # # .
                    . . . . #
                    # # # # .
                    """)
            elif data_in == "squitt":
                basic.show_leds("""
                    # . . . #
                    . # . # .
                    . . # . .
                    . # . # .
                    # . . . #
                    """)       
        else:
            # decode the input data to separate servo turn degrees, and motor speed values
            deg, speed = int(data_in[:3])-100, int(data_in[3:6])-200
    
            # Send turn angle to servo
            pins.servo_write_pin(AnalogPin.P0, deg)

            if speed < 0:
                # Send speed as PWM value to the 9v DC motor                
                mShield.extend_pwm_control(mShield.PwmIndex.S4, 0)
                mShield.extend_pwm_control(mShield.PwmIndex.S3, abs(speed))

            else:
                # Send speed as PWM value to the 9v DC motor               
                mShield.extend_pwm_control(mShield.PwmIndex.S3, 0)
                mShield.extend_pwm_control(mShield.PwmIndex.S4, speed)
        
    except:
        basic.show_leds("""
            # . . . #
            . . . . .
            . . # . .
            . . . . .
            # . . . #
            """)
        pass

# basic.forever(on_forever)
