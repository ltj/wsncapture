import sys
import serial
import packet
import logger
import output
import time
from datetime import datetime, timedelta
from config import (serial_port, serial_baudrate, serial_timeout, log_path,
                   use_log, use_stdout, use_cosm)

def capture(ser, log):
    
    decoder = packet.Packet()
    
    if use_stdout:
        out_stdout = output.ToStdout()
    if use_cosm:
        out_cosm = output.ToCosm()
    
    # check if previous marker is present
    if log.markerfile_present():
        print 'Previous marker found. Replaying...'
        (logtime, marker) = log.get_marker()
        (page, seq, secs, replay_cmd) = decoder.getdfs(marker)
        ser.write(replay_cmd)
        time.sleep(1)
        
        # Replay loop
        prevsec = secs
        while True:
            if ser.inWaiting() > 0:
                line = ser.readline()
                if line[0] == 'R':
                    (sec, ok) = decoder.getreplay(line)
                    offset = sec - prevsec
                    logtime = logtime + timedelta(seconds=offset)
                    log.append(ok, logtime)
                    prevsec = sec   
                    if use_stdout:
                        print ok ,
                if line[0:4] == 'DF E':
                    break
        
    # Recording loop
    print 'Recording new packets...'
    while True:
        try:
            if ser.inWaiting() > 0:
                line = ser.readline()
                if decoder.is_ok_packet(line):
                    (node_id, data) = decoder.decode(line)
                    if use_log:
                        log.append(line)
                    if use_stdout:
                        out_stdout.send(node_id, data)
                    if use_cosm:
                        out_cosm.send(node_id, data)
                elif decoder.is_dfs_packet(line):
                    log.append(line)
                    break
        except serial.SerialException, e:
            sys.stderr.write("Serial bridge %s: %s\n" % (ser.portstr, e))
            sys.exit(1)
        except IOError, e:
            sys.stderr.write("Logger: %s\n" % e)
            sys.exit(1)
        except (KeyboardInterrupt, SystemExit):
            break
        
        time.sleep(0.01)
    
    ser.close()
    print("wsncap done.")

            
if __name__ == "__main__":
    print("Starting wsncap...")

    print("Initializing logger.")
    try:
        log = logger.Logger(log_path)
    except IOError, e:
        sys.stderr.write("Logger: %s\n" % e)
        sys.exit(1)

    print("Starting serial bridge.")
    ser = serial.Serial()
    ser.port = serial_port
    ser.baudrate = serial_baudrate
    ser.timeout = serial_timeout
    try:
        ser.open()
        time.sleep(2)
    except serial.SerialException, e:
       sys.stderr.write("Could not open serial %s: %s\n" % (ser.portstr, e))
       sys.exit(1)

    capture(ser, log)
    