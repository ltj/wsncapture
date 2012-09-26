from datetime import datetime
import cPickle
import sys
import os.path

mfile = sys.argv[1]

if os.path.isfile(mfile):
    fh = open(mfile, 'r')
    (logtime, marker) = cPickle.load(fh)
    fh.close()
    print "Time: " + logtime.isoformat()
    print "Marker: " + marker
