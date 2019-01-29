#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BOARD) # Pin Numbering Board
sensor_pin = 13
GPIO.setup(sensor_pin, GPIO.IN)  # pin 13  = input

rate_cnt = 0
tot_cnt = 0
time_zero = 0.0
time_start = 0.0
time_end = 0.0
gpio_cur = 0
gpio_last = 0
pulses = 0
constant = 1.79

print('Water FLow - Approximate\nControl C to exit')

time_zero = time.time()

while True:
    rate_cnt = 0
    pulses = 0
    time_start = time.time()
    while pulses <= 5:
        gpio_cur = GPIO.input(sensor_pin)
        if (gpio_cur != 0) and (gpio_cur != gpio_last):
            pulses += 1
        gpio_last = gpio_cur
        try:
            None
        except KeyboardInterrupt as inter:
            print('\nCTRL C - Exiting nicely')
            GPIO.cleanup()
            print('Done')
            sys.exit()

    rate_cnt += 1
    tot_cnt += 1
    time_end = time.time()

    print('\nLiters/min ',
            round((rate_cnt * constant)/(time_end - time_start), 2),
            'approximate')
    print('Total Liters ', round(tot_cnt * constant, 1))

