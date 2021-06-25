#!/usr/bin/env python2

import os, time
import linuxcnc
 
read_path = "/tmp/pipe.in"
write_path = "/tmp/pipe.out"

for fn in [read_path, write_path]: 
    if os.path.exists(fn):
        os.remove(fn)
    os.mkfifo(fn)
 
rf = os.open(read_path, os.O_RDONLY)
wf = os.open(write_path, os.O_SYNC | os.O_CREAT | os.O_RDWR)

vel_ = [10, 20, 100]
vel_ind_ = 0

while True:
    b = os.read(rf, 1024)
    if len(b) == 0:
        continue

    s = b.decode('latin-1')
    # print('Received:', s)
    if s != '0':
        lst = s.split('\n')
        # print([x.split(':') for x in lst])
        d = {k:v=='1' for k,v in [x.split(':') for x in lst]}

        c = linuxcnc.command()
        for k,v in d.items():
            if k == 'brake':
                 if v:
                     c.brake(linuxcnc.BRAKE_ENGAGE)
                 else:
                     c.brake(linuxcnc.BRAKE_RELEASE)
            elif k == 'jog_speed':
                 if v:
                     vel_ind_ = (vel_ind_ + 1) % len(vel_)
            elif k.startswith('jog_'):
                 axis = {'x':0, 'y':1, 'z':2}[k[4]]
                 d = {'+':1, '-':-1}[k[6]]
                 vel = d * vel_[vel_ind_] / 60.
                 if v:
                     c.jog(linuxcnc.JOG_CONTINUOUS, False, axis, vel)
                 else:
                     c.jog(linuxcnc.JOG_STOP, False, axis)
               
    # Process command...

    #     if "exit" in s:
    #         break

    try:
        s = linuxcnc.stat() # create a connection to the status channel
        s.poll() # get current values
    except linuxcnc.error, detail:
        print("error", detail)
        sys.exit(1)
    # for x in dir(s):
    #     if not x.startswith('_'):
    #         print x, getattr(s,x)
    pos = s.actual_position

    lst = ['{:6.04f}'.format(pos[0]), '{:6.04f}'.format(pos[1]), '{:6.04f}'.format(pos[2]), str(s.spindle[0]['brake']), str(vel_[vel_ind_])]
    s = ' '.join(lst)
    b = s.encode('latin-1')
    os.write(wf, b)
 
os.close(rf)
os.close(wf)

