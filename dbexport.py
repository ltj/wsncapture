import sys
import os.path
from decoder import Decoder
from datetime import datetime
from config import nodes, types, tables, database, log_path

def main(infile, outfile, fromline=0):
    fin = open(infile, 'r')
    fout = open(outfile, 'w')
    fseek = open(log_path + '/db_progress', 'w')
    
    fout.write("USE %s;\n" % database)
    
    # read in file
    i = 0 # line counter
    for l in fin:
        if i < fromline: 
            i += 1
            continue # skip lines before fromline
        if 'OK' in l:
            date = l[0:10]
            time = l[11:19]
            timestamp = "'" + date + ' ' + time + "'"
            packet = l[28:].strip()
            (nid, data) = Decoder.decode(packet)
            if data:
                if nodes.has_key(nid):
                    table = nodes[nid]['db']['table']
                    fieldstring = ', '.join(table['fields'])
                    stringdata = [timestamp]
                    for d in data:
                        stringdata.append("'" + str(d) + "'")
                    valstring = ', '.join(stringdata)
                    fout.write("INSERT INTO %s (%s) VALUES (%s);\n" 
                                % (table['name'], fieldstring, valstring))            
        i += 1
    
    fseek.write(str(i)) # write last line to file
        
    fin.close()
    fout.close()
    fseek.close()  
    

if __name__ == "__main__":
    if not (len(sys.argv) == 3 or len(sys.argv) == 4):
        print 'Usage: dbexport.py <infile> <outfile> [from_line]'
        exit(1)
        
    infile = sys.argv[1]
    outfile = sys.argv[2]
    if len(sys.argv) == 4:
        fromline = int(sys.argv[3])
    else:
        fromline = 0
    
    if not os.path.isfile(infile):
        print 'Infile %s not found' % infile
        exit(1)
        
    main(infile, outfile, fromline)