#!/usr/bin/env python
import time, sys
import RPi.GPIO as GPIO

#DEBUG = True
DEBUG = False
# configurations
pin_input = 15
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_input, GPIO.IN)

# variables
total_liters = 0
secondes = 0

# Sampling
sample_rate = 10  # Sampling each 10 secondes
time_start = 0
time_end = 0
period = 0;
hz = []       # Frequency !important!
m = 0.0021    # See linear.pdf

print("Water Flow - YF-S201 measurment")

while True:
    # start / end 
    time_start = time.time();
    init_time_start = time_start # undetect last edge 
    time_end = time_start + sample_rate
    hz = []
    sample_total_time = 0

    # Edge
    current = GPIO.input(pin_input)
    edge = current # Rising edge / Falling edge

    try:
        while time.time() <= time_end:
            t = time.time();
            v = GPIO.input(pin_input)
            if current != v and current == edge:
                period = t - time_start # Impulsion period
                new_hz = 1/period
                hz.append(new_hz)               # Period = 1/period
                sample_total_time += t - time_start
                time_start = t;
               
                if DEBUG:
                    print(round(new_hz, 4))     # Print hz
                    sys.stdout.flush()
            current = v;

        # Sums
        print('-------------------------------------')
        print('Current Time:',time.asctime(time.localtime()))

        secondes += sample_rate
        nb_samples = len(hz);
        if nb_samples >0:
            average = sum(hz) / float(len(hz));
            # Calcul % of good sample in time range
            good_sample = sample_total_time/sample_rate
            print("\t", round(sample_total_time,4),'(sec) good sample')
            print("\t", round(good_sample*100,4),'(%) good sample')
            average = average * good_sample
        else:
            average = 0
        average_liters = average*m*sample_rate;
        total_liters += average_liters
        print("\t", round(average,4),'(hz) average')
        print('\t', round(average_liters*(60/sample_rate),4),'(L/min)') # Display L/min instead of L/sec
        print(round(total_liters,4),'(L) total')
        print(round(secondes/60,4), '(min) total')
        print('-------------------------------------')
    except KeyboardInterrupt:
        print('\n CTRL+C - Exiting')
        GPIO.cleanup()
        sys.exit()
GPIO.cleanup()
print('Done')
