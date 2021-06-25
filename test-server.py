#!/usr/bin/env python

import os, time
 
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
    s = b.decode('latin-1')
    if len(s) == 0:
        time.sleep(.01)
        continue

    print('Received:', s)

    if "exit" in s:
        break

    lst = [10.1010, 20.2020, 30.3030, 1]
    s = ' '.join(map(str, lst))
    b = s.encode('latin-1')
    os.write(wf, b)
 
os.close(rf)
os.close(wf)

