#!/usr/bin/env python2
# coding=utf8

from time import time, sleep
from random import randint
from liblo import *
import colorsys
target = Address("169.254.1.1", 9000)

l = 9
e = [0] * (9 * 3)

while True:
    for i in range(l):
    	c =  colorsys.hsv_to_rgb(randint(0,100)/100.0,1,1)
        e[i * 3] = int(c[0]*128)
        e[i * 3 + 1] = int(c[1]*200)
        e[i * 3 + 2] = int(c[2]*255)

    send(target, "/outputs/rgb/16", e)
    sleep(0.05)


    