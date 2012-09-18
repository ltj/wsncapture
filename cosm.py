import json
import httplib

class Cosm:
    
    COSM_HOST = 'api.cosm.com'
    BASE_URL = '/v2/feeds/'
    
    def __init__(self, apikey, use_https=True):
        self.apikey = apikey
        self.use_https = True
        

    def streamupdate(self, feed, stream, value, min=None, max=None):
        if min and max:
            data = {'current_value': value, 'max_value': max,
                    'min_value': min, 'id': stream}
        else:
            data = {'current_value': value, 'id': stream}
            
        url = self.BASE_URL + feed + '/datastreams/' + stream
        
        self._senddata('PUT', url, json.dumps(data))
        
        
    def datapointcreate(self, feed, stream, datapoints):
        data = {'datapoints': []}
        for (time,val) in datapoints:
            data['datapoints'].append({'at': time, 'value': val})
        
        url = self.BASE_URL + feed + '/datastreams/' + stream + '/datapoints'
        
        self._senddata('POST', url, json.dumps(data))
            

    def _senddata(self, method, url, data):
        if self.use_https:
            conn = httplib.HTTPSConnection(self.COSM_HOST, timeout=10)
        else:
            conn = httplib.HTTPConnection(self.COSM_HOST, timeout=10)
        
        conn.request(method, url, data, {'X-ApiKey': self.apikey})
        conn.sock.settimeout(5.0)
        resp = conn.getresponse()
        if resp.status != 200:
            msg = resp.reason
            raise Exception(msg)
        resp.read()
        conn.close()