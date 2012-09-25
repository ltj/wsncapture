import os.path
import cPickle
import logging
from datetime import date, datetime
from config import log_zulu, log_path

class CapLogger:
    """Logs to and manages packet log files"""
    
    def __init__(self, suffix='-capture', markerfile='marker_file'):
        if log_path.endswith('/'):
            self.path = log_path
        else:
            self.path = log_path + '/'
        self.suffix = suffix
        self.markerfile = markerfile
        self.buffer = []
        self.date = date.today()
        self.current_file = self.path + self.date.strftime('%Y%m%d') + self.suffix
        if not os.path.exists(self.path):
            raise IOError('Path not found.')
        
    def append(self, entry, time=None):
        """Adds a timestamped logfile entry"""
        if time:
            now = time
        else:
            if log_zulu:
                now = datetime.utcnow()
            else:
                now = datetime.now()
        
        if log_zulu:
            timestamp = now.isoformat() + 'Z'
        else:
            timestamp = now.isoformat()
        
        if entry[0:2] == 'OK':
            self.buffer.append(timestamp + " " + entry)
        elif entry[0:2] == 'DF':
            if entry[3] == 'S':
                self.buffer.pop()
            self.buffer.append(timestamp + " " + entry)
            self._save_marker(now, entry)
            self.flush()
                
    def flush(self):
        """writes buffer immediately"""
        try:
            fh = open(self.current_file, 'a')
            try:
                for line in self.buffer:
                    fh.write(line)
            finally:
                fh.close()
                self.buffer = []
        except IOError:
            pass

    def _save_marker(self, timestamp, marker):
        """saves the df storage marker and timestamp to file"""
        data = (timestamp, marker)
        try:
            out = open(self.path + self.markerfile, 'wb')
            cPickle.dump(data, out)
            out.close()
        except IOError:
            pass
            
    def get_marker(self):
        """retrieves the last saved marker"""
        try:
            inm = open(self.path + self.markerfile, 'r')
            (logtime, marker) = cPickle.load(inm)
            inm.close()
            return (logtime, marker)
        except IOError as e:
            logging.error('Marker file IO error: {0}', e.strerror)
            return None
            
    def markerfile_present(self):
        return os.path.isfile(self.path + self.markerfile)