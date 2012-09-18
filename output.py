import cosm
from config import nodes, types, cosm_apikey, cosm_prec

class ToStdout:
    """stdout pretty printer"""
    
    def send(cls, nid, data, timestamp=None):
        """send raw packet to output via a decoding of the data"""
        if nodes.has_key(nid):
            if data:
                for val, typ in zip(data, nodes[nid]['data']):
                    cls._output(nid, val, typ, timestamp)
                    
    
    def _output(cls, nid, value, type, timestamp):
        if timestamp:
            print timestamp + " " ,
        try:
            print(nid + " " + types[type]['name'] + ": " + 
                  str(value) + " " + types[type]['symbol'])
        except KeyError:
            pass # TODO - log errors in config
            

class ToCosm:
    """update Cosm datastreams"""
    
    def __init__(self):
        self.ccomm = cosm.Cosm(cosm_apikey)
        
    def send(self, nid, data):
        try:
            if nodes.has_key(nid):
                if nodes[nid].has_key('cosm'):
                    feed = str(nodes[nid]['cosm']['feed']['id'])
                    for val, typ in zip(data, nodes[nid]['data']):
                        if nodes[nid]['cosm'].has_key(typ):
                            stream = nodes[nid]['cosm'][typ]
                            if isinstance(val, float):
                                self.ccomm.streamupdate(feed, stream, 
                                                        round(val, cosm_prec))
                            else:
                                self.ccomm.streamupdate(feed, stream, val)
        except KeyError:
            pass # TODO - log errors in config