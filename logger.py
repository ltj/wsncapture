import os.path
import cPickle
from datetime import date, datetime
from config import log_zulu
from packet import Packet

class Logger:
    """Logs to and manages pecket log files"""
    
    def __init__(self, path, suffix='-wsnhub', markerfile='marker_file'):
        if path.endswith('/'):
            self.path = path
        else:
            self.path = path + '/'
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
        
        if Packet.is_ok_packet(entry):
            self.buffer.append(timestamp + " " + entry)
        elif Packet.is_dfs_packet(entry):
            self._update_file()
            try:
                fh = open(self.current_file, 'a')
                try:
                    for line in self.buffer[:-1]: # discard the last entry
                        fh.write(line)
                    self._save_marker(now, entry)
                finally:
                    fh.close()
                    self.buffer = []
            except IOError:
                pass
        
    def _update_file(self):
        """Rolls over logfile if we entered a new day"""
        if date.today() > self.date:
            self.date = date.today()
            self.current_file = self.path + self.date.strftime('%Y%m%d') + self.suffix

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
            print "Marker file IO error: {0}".format(e.strerror)
            return None
            
    def markerfile_present(self):
        return os.path.isfile(self.path + self.markerfile)