#!/usr/bin/env python

import os
import time
 
write_path = "/tmp/pipe.in"
read_path = "/tmp/pipe.out"
 
wf = os.open(write_path, os.O_SYNC | os.O_CREAT | os.O_RDWR)
rf = None

while True:
    msg = "cmd..."
    b = msg.encode('latin-1')
    len_send = os.write(wf, b)
    # print("sent msg: %s" % msg)
 
    if rf is None:
        rf = os.open(read_path, os.O_RDONLY)
 
    b = os.read(rf, 1024)
    if len(b) == 0:
        break
    s = b.decode('latin-1')
    print('Received:', s)
 
    time.sleep(.01)
 
os.write(wf, 'exit')
 
os.close(rf)
os.close(wf)

