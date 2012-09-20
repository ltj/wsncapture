import struct
from config import nodes

class Decoder:
    ''' JeeLink packet and message decoder
     
    Various methods to manage the JeeLink serial ouput.
    
    '''

    @staticmethod
    def is_ok_packet(packet_string):
        return packet_string.startswith('OK')
        
    @staticmethod
    def is_dfs_packet(packet_string):
        return packet_string.startswith('DF S')
        
    @staticmethod
    def is_dfr_packet(packet_string):
        return packet_string.startswith('DF R')
        
    @staticmethod
    def getdfs(dfsline):
        parts = dfsline.split(' ')
        if len(parts) == 5:
            page = parts[2]
            seq = parts[3]
            time = parts[4]
        replay_cmd = (page + 'r')
        return (page, seq, time, replay_cmd)
    
    @staticmethod
    def getreplay(repline):
        parts = repline.split(' ')
        secs = parts[2]
        sep = ' '
        ok = 'OK ' + sep.join(parts[3:])
        return (int(secs), ok)
        
    @staticmethod
    def getreplaymarker(repline):
        parts = repline.split(' ')
        page = parts[2]
        seq = parts[3]
        secs = parts[4]
        return (page, seq, int(secs)) 

    @staticmethod
    def _byte_encode_ok_packet(packet_string):
        parts = packet_string.split(' ')
        node_id = parts[1]
        packed = ''
    
        for s in parts[2:]:
            packed += struct.pack('B', int(s))
        
        return (node_id, packed)
    
    @staticmethod
    def _byte_encode_replay_packet(packet_string):
        parts = packet_string.split(' ')
        node_id = parts[3]
        packed = ''
    
        for s in parts[4:]:
            packed += struct.pack('B', int(s))
        
        return (node_id, packed)
    
    @staticmethod
    def _unpack_packet_bytes(format, packed_string):
        return struct.unpack(format, packed_string)
    
    @staticmethod
    def decode(packet):
        """decode packet bytes to individual readings"""
        (node_id, decode) = Decoder._byte_encode_ok_packet(packet)
        data = None
        try:
            data = Decoder._unpack_packet_bytes(nodes[node_id]['format'], decode)
        except KeyError:
            pass # discard unknown id's TO-DO: log on exports?
        except struct.error:
            pass # TODO: log bad format in config

        return (node_id, data)