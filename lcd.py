#!/usr/bin/env python
""" 
Moodeaudio LCD 16x2 I2C update daemon

Requires RPLCD library by Danilo Bargen (https://github.com/dbrgn/RPLCD)

Copyright (c) 2015, 2019 Giorgio L. Rutigliano
(www.iltecnico.info, www.i8zse.eu, www.giorgiorutigliano.it)

This is free software released under MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__ = "Giorgio Leo Rutigliano"
__copyright__ = "Copyright 2019"
__date__ = "2019/11/03"
__license__ = "GPLv3"
__version__ = "1.2"

from RPLCD.i2c import CharLCD
import os
import subprocess
import socket
from time import sleep

LCD_W = 16


def docmd(cs):
    # execute commands via subprocess
    process = subprocess.Popen(cs, stdout=subprocess.PIPE, shell=True)
    os.waitpid(process.pid, 0)[1]
    return process.stdout.read().strip()


def updcpu():
    # display CPU load 1-min avg
    l1, l2, l3 = os.getloadavg()
    cpu = int(l1 * 50.0 + .5)
    if cpu > 99:
        dcpu = "99"
    else:
        dcpu = "%02d" % (cpu)
    lcd.cursor_pos = (1, 4)
    lcd.write_string(dcpu)


def updwifi():
    # display wifi level (0..9)
    try:
        ss = docmd("iwconfig wlan0 | grep Signal | awk '{print $4}' | cut -d= -f2")
        dbm = int(ss)
        if (dbm <= -100):
            dbm = -100;
        if (dbm >= -50):
            dbm = -50;
        q = int((100.0 + dbm) * 9.0 / 50.0 + 0.5)
        wfl = str(q)
    except:
        wfl = "-"
    lcd.cursor_pos = (1, 10)
    lcd.write_string(wfl)


def updtemp():
    # display CPU temperaure
    ss = docmd("/opt/vc/bin/vcgencmd measure_temp | cut -c6-9")
    cpt = int(float(ss) + 0.5)
    if cpt > 99:
        dcpt = "**"
    else:
        dcpt = "%02d" % (cpt)
    lcd.cursor_pos = (1, 14)
    lcd.write_string(dcpt)


def btcon():
    # return name of bt connected device, empty string if no device
    bt = subprocess.Popen(["bluetoothctl"], shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    out, err = bt.communicate("exit")
    # strip escape sequences
    out = out.replace("\x1b[", "")
    # extract connected device
    cn = out[out.find("[") + 1:out.find("]")]
    if cn == 'bluetooth':
        return ''
    return "BT:"+cn[0:13]


# ini LCD
lcd = CharLCD('PCF8574', 0x27)
lcd.compat_mode = True
# show splash
lcd.cursor_pos = (0, 0)
lcd.write_string('   Moodeaudio   ')
lcd.cursor_pos = (1, 0)
lcd.write_string('    by I8ZSE    ')
sleep(5)
# get main ip address and show it on LCD
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
lanip = s.getsockname()[0]
# show IP address of device
lcd.clear()
lcd.cursor_pos = (1, int((LCD_W - len(lanip)) / 2))
lcd.write_string(lanip)
sleep(3)
# clear LCD
lcd.cursor_pos = (1, 0)
lcd.write_string('CPU:   WS:  T:  ')
# main loop
while True:
    # get current playing status via mpc
    buf = docmd("mpc")
    rows = buf.split("\n")
    updcpu()
    updwifi()
    updtemp()
    if len(rows) != 3:
        # Nothing playing via mpd, check BT status
        msg = btcon()
        if msg == '':
            # no BT connection
            msg = "** In  Attesa **"
        lcd.cursor_pos = (0, 0)
        lcd.write_string(msg)
        for i in range(0, 4):
            updcpu()
            sleep(.4)
        continue
        # something is playing via mpd
    song = (" " * LCD_W) + rows[0]
    if len(song) <= LCD_W:
        lcd.cursor_pos = (0, 0)
        lcd.write_string(song)
    else:
        for i in range(0, len(song) + 1):
            lcd.cursor_pos = (0, 0)
            text = (song + ' ' * LCD_W)[i:i + LCD_W]
            lcd.write_string(text)
            updcpu()
            sleep(.4)

