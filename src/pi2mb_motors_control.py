from microbit import *
import music
import mShield

# Play music to indicate the Microbit is active
music.play(music.tone_playable(Note.C, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)

# Initilize serial connection parameters
serial.redirect_to_usb()
serial.set_baud_rate(BaudRate.BAUD_RATE115200)
serial.set_rx_buffer_size(4)

# Initialize default values
deg = 90

# Set servo to align straight
pins.servo_write_pin(AnalogPin.P0, deg)

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
            if data_in == "str":
                basic.show_leds("""
                    . . . . .
                    . . # . .
                    . # # # .
                    . . # . .
                    . . . . .
                    """)
            elif data_in == "stp":
                basic.show_leds("""
                    . . . . .
                    . . . . .
                    . # # # .
                    . . . . .
                    . . . . .
                    """)
            elif data_in == "sss":
                basic.show_leds("""
                    . # # # #
                    # . . . .
                    . # # # .
                    . . . . #
                    # # # # .
                    """)
            elif data_in == "sqt":
                basic.show_leds("""
                    # . . . #
                    . # . # .
                    . . # . .
                    . # . # .
                    # . . . #
                    """)       
        else:
            # decode the input data to extract servo turn degrees, and motor speed values
            deg  = int(data_in[:3])-100

            # Send turn angle to servo
            pins.servo_write_pin(AnalogPin.P0, deg)
        
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
