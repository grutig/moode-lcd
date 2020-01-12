# moode-lcd
LCD Display 16x2 driver daemon for moodeaudio 3.4

Copyright (c) 2015, 2019 Giorgio L. Rutigliano
(www.iltecnico.info, www.i8zse.eu, www.giorgiorutigliano.it)

This is free software released under MIT License
Requires RPLCD library by Danilo Bargen (https://github.com/dbrgn/RPLCD)

This script is a daemon designed to drive a standard 16x2 LCD display based 
on HD44780 controller and interfaced via I2C bus.
It shows on first line the name of source played (or BT device name).
On the second line there are three numbers: Board load (00..99), WiFi Signal (0..9)
and CPU temperature (degrees celtius).

It can be started from /etc/rc.local
Tested with moodeaudio 3.4 and raspberry pi-zero.

Please notice that standard LCD display modules must be run from 5V power line, 
while Raspberry PI GPIO runs at 3.3V and are not 5V tolerant. It is possible to
connect 5V devices to RPI GPIO as long as there are no pullup resistor on it.
Standard LCD I2C inteface boards are fitted with pullup resistor, that must be
removed to avoid damages to Raspberry. It is better to measure voltage on SDA and
SCL lines before connect them to RPI and check that voltage is ok: it should be near
zero V.
