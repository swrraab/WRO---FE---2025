from time import sleep

import serial

# Replace with your microbit port number
s = serial.Serial("/dev/ttyACM0")
s.baudrate = 115200
s.parity   = serial.PARITY_NONE
s.bytesize = serial.EIGHTBITS
s.stopbits = serial.STOPBITS_ONE
s.timeout  = 1
s.reset_input_buffer()

i = 1

while i<100:
    # Send serial uart data to microbit

    s.write(str(i).encode('UTF-8'))
    s.flush()
    i=i+1

    sleep(.1)

s.close()