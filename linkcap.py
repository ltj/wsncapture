import sys
import serial
import caplogger
import time
import logging
import logging.handlers
from decoder import Decoder
from datetime import datetime, timedelta
from config import serial_port, serial_baudrate, serial_timeout, system_log

def capture(ser, log):
    buf = []
    
    # check if previous marker is present
    if log.markerfile_present():
        print 'Previous marker found. Replaying...'
        (logtime, marker) = log.get_marker()
        (page, seq, secs, replay_cmd) = Decoder.getdfs(marker)
        ser.write(replay_cmd)
        time.sleep(1)
        
        # Replay loop
        prevsec = 0
        while True:
            try:
                if ser.inWaiting() > 0:
                    line = ser.readline()
                    if line[0] == 'R': # replay packet
                        repdata = Decoder.getreplay(line)
                        buf.append(repdata)
                    if line[0:4] == 'DF R': # replay marker
                        (page, seq, psec) = Decoder.getreplaymarker(line)
                        if psec < prevsec:
                            prevsec = psec
                            psec = 0
                        else:
                            prevsec = psec
                        for (rpsec, rok) in buf:
                            offset = rpsec - psec
                            logtime = logtime + timedelta(seconds=offset)
                            log.append(rok, logtime)
                            psec = rpsec
                        buf = [] # clear buffer
                        log.append(line, logtime)
                    if line[0:4] == 'DF E': # end of replay
                        break
            except serial.SerialException, e:
                logging.error("Serial bridge %s: %s\n", ser.portstr, e)
                sys.exit(1)
            except IOError, e:
                logging.error("Logger: %s\n", e)
                sys.exit(1)
        
    # Recording loop
    print 'Recording new packets...'
    while True:
        try:
            if ser.inWaiting() > 0:
                line = ser.readline()
                if line[0:2] == 'OK': # ok packet
                    log.append(line)
                elif line[0:4] == 'DF S': # store marker
                    log.append(line)
                    break
        except serial.SerialException, e:
            logging.error("Serial bridge %s: %s\n", ser.portstr, e)
            sys.exit(1)
        except IOError, e:
            logging.error("Logger: %s\n", e)
            sys.exit(1)
        except (KeyboardInterrupt, SystemExit):
            break
        time.sleep(0.01) # bad CPU 'nice' hack
    
    ser.close()
    logging.info("linkcap done :)")
    print("linkcap done :)")
    logging.shutdown()
    sys.exit(0)

            
if __name__ == "__main__":
    print("Starting wsncap...")
    
    print("Initializing system logger...")
    syslog = logging.getLogger()
    syslog.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
                  system_log, maxBytes=1048576, backupCount=5)
    form = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
    handler.setFormatter(form)

    syslog.addHandler(handler)
    logging.info('linkcap started')

    print("Initializing capture logger...")
    try:
        log = caplogger.CapLogger()
    except IOError, e:
        logging.error("Logger: %s\n", e)
        sys.exit(1)

    print("Starting serial...")
    ser = serial.Serial()
    ser.port = serial_port
    ser.baudrate = serial_baudrate
    ser.timeout = serial_timeout
    try:
        ser.open()
        time.sleep(2)
    except serial.SerialException, e:
       logging.error("Could not open serial %s: %s\n", ser.portstr, e)
       sys.exit(1)

    capture(ser, log)
    