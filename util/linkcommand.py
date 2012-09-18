import serial
import sys
import time

ser = serial.Serial()
ser.port = '/dev/tty.usbserial-AH019YW9'
ser.baudrate = 57600
ser.timeout = 1
ser.dsrdtr = False

command = sys.argv[1]
print "Command: {0}".format(command)

ser.open()

time.sleep(2)

ser.write(command + '\r\n')
time.sleep(1)

while True:
    if ser.inWaiting():
        line = ser.readline()
        if line[0:4] == 'DF R' or line[0] == 'R':
            print line ,
        if line[0:4] == 'DF E':
            print line ,
            break

ser.close()