import struct
from config import nodes

class Packet:

    @staticmethod
    def is_ok_packet(packet_string):
        return packet_string.startswith('OK')
        
    @staticmethod
    def is_dfs_packet(packet_string):
        return packet_string.startswith('DF S')
        
    def getdfs(cls, dfsline):
        parts = dfsline.split(' ')
        if len(parts) == 5:
            page = parts[2]
            seq = parts[3]
            time = parts[4]
        replay_cmd = (page + 'r')
        return (page, seq, time, replay_cmd)
        
    def getreplay(cls, repline):
        parts = repline.split(' ')
        secs = parts[2]
        sep = ' '
        ok = 'OK ' + sep.join(parts[3:])
        return (int(secs), ok)
        
    def getreplaymarker(cls, repline):
        parts = repline.split(' ')
        page = parts[2]
        seq = parts[3]
        secs = parts[4]
        return (page, seq, int(secs)) 

    def _byte_encode_ok_packet(cls, packet_string):
        parts = packet_string.split(' ')
        node_id = parts[1]
        packed = ''
    
        for s in parts[2:]:
            packed += struct.pack('B', int(s))
        
        return (node_id, packed)
    
    def _byte_encode_replay_packet(cls, packet_string):
        parts = packet_string.split(' ')
        node_id = parts[3]
        packed = ''
    
        for s in parts[4:]:
            packed += struct.pack('B', int(s))
        
        return (node_id, packed)
    
    def _unpack_packet_bytes(cls, format, packed_string):
        return struct.unpack(format, packed_string)
        
    def decode(self, packet):
        """decode packet bytes to individual readings"""
        (node_id, decode) = self._byte_encode_ok_packet(packet)
        data = None
        try:
            data = self._unpack_packet_bytes(nodes[node_id]['format'], decode)
        except KeyError:
            pass # discard unknown id's
        except struct.error:
            pass # TODO: log bad format in config

        return (node_id, data)