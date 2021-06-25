#!/usr/bin/env python2

import os, time
import linuxcnc
 
read_path = "/tmp/pipe.in"
write_path = "/tmp/pipe.out"
 
if os.path.exists(read_path):
    os.remove(read_path)
if os.path.exists(write_path):
    os.remove(write_path)
 
os.mkfifo(write_path)
os.mkfifo(read_path)
 
rf = os.open(read_path, os.O_RDONLY)
wf = os.open(write_path, os.O_SYNC | os.O_CREAT | os.O_RDWR)
 
while True:
    b = os.read(rf, 1024)
    if len(b) == 0:
        s = b.decode('latin-1')
        print('Received:', s)
        # Process command...

    #     if "exit" in s:
    #         break

    try:
        s = linuxcnc.stat() # create a connection to the status channel
        s.poll() # get current values
    except linuxcnc.error, detail:
        print "error", detail
        sys.exit(1)
    for x in dir(s):
        if not x.startswith('_'):
            print x, getattr(s,x)
    pos = s.actual_position

    lst = ['{:6.04f}'.format(pos[0]), '{:6.04f}'.format(pos[1]), '{:6.04f}'.format(pos[2]), str(s.spindle[0]['brake'])]
    s = ' '.join(lst)
    b = s.encode('latin-1')
    os.write(wf, b)

    time.sleep(0.01)
 
os.close(rf)
os.close(wf)

