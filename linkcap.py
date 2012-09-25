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
    readbuf = []
    
    # check if previous marker is present
    if log.markerfile_present():
        logging.info('previous marker found. replaying')
        (logtime, marker) = log.get_marker()
        (page, seq, secs, replay_cmd) = Decoder.getdfs(marker)
        ser.write(replay_cmd)
        
        # replay loop
        while True:
            try:
                if ser.inWaiting() > 0:
                    data = ser.readline()
                    if data[0] == 'R' or data[0:4] == 'DF R':
                        readbuf.append(data)
                    if data[0:4] == 'DF E': # end of replay
                        break
            except serial.SerialException, e:
                logging.error("Serial bridge %s: %s\n", ser.portstr, e)
                sys.exit(1)
            except IOError, e:
                logging.error("Logger: %s\n", e)
                sys.exit(1)
        logging.info('replay ended. writing to log')
        
        # log replays
        (secs, packet) = Decoder.getreplay(readbuf[0])
        prevsecs = secs
        for line in readbuf:
            if line[0] == 'R': # replay packet
                (secs, packet) = Decoder.getreplay(line)
                if secs < prevsecs:
                    offset = secs
                else:
                    offset = secs - prevsecs
                logtime = logtime + timedelta(seconds=offset)
                log.append(logtime, packet)
                prevsecs = secs
            if line[0:4] == 'DF R': # replay marker
                log.append(line, logtime)
        logging.info('done writing replay data to log')
        
    # Recording loop
    logging.info('recording new packets')
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
    logging.info("linkcap completed")
    logging.shutdown()
    sys.exit(0)

            
if __name__ == "__main__":
    syslog = logging.getLogger()
    syslog.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
                  system_log, maxBytes=1048576, backupCount=5)
    form = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
    handler.setFormatter(form)

    syslog.addHandler(handler)
    logging.info('linkcap started')

    try:
        log = caplogger.CapLogger()
    except IOError, e:
        logging.error("Logger: %s\n", e)
        sys.exit(1)
    logging.info('capture logger created')

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
    logging.info('serial connection opened')

    capture(ser, log)
    