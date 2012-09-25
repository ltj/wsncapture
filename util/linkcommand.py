import serial
import sys
import time
import Queue

ser = serial.Serial()
ser.port = '/dev/tty.usbserial-AH019YW9'
ser.baudrate = 57600
ser.timeout = 1
ser.dsrdtr = False

q = Queue.Queue()

command = sys.argv[1]
print "Command: {0}".format(command)

ser.open()

time.sleep(2)

ser.write(command + '\r\n')
#time.sleep(2)

#buf = []

while True:
    if ser.inWaiting():
        data = ser.readline()
        q.put_nowait(data)
        if data[0:4] == ('DF E'):
            break
        

            
ser.close()

while not q.empty():
    print q.get_nowait() ,
#for l in buf:
#    print l ,