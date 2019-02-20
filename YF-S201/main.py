#!/usr/bin/env python
#DEBUG = True
DEBUG = False
import time, sys
import RPi.GPIO as GPIO
from datetime import datetime

#DBConnection
import os
scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
os.chdir(scriptPath)
sys.path.append("../InfluxDB")
import DBconnection

INFLUX_ENABLE = 'yes'

# argument pin is required
import argparse
parser = argparse.ArgumentParser(description='YF-S201 measurement application for Raspberry Pi')
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-p', '--pin', help='Data Raspberry Pin. Look at GPIO PINOUT', required=True)
args = parser.parse_args()
print("Port:",args.pin)

if not args.pin:
    parser.parse_args(['-h'])

try: 
    int(args.pin)
except ValueError:
    print('Error pin must be a integer')
    sys.exit() 

if args.pin != '8' and args.pin != '10':
    print("Error pin must be 8 or 10. If you need another pin change this condition...")
    sys.exit()

# configurations
pin_input = int(args.pin)
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

# data 
db_good_sample = 0
db_hz = 0
db_liter_by_min = 0

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
            db_good_sample = round(good_sample*100,4)
            print("\t", db_good_sample,'(%) good sample')
            average = average * good_sample
        else:
            average = 0
        average_liters = average*m*sample_rate;
        total_liters += average_liters
        db_hz = round(average,4);
        db_liter_by_min= round(average_liters*(60/sample_rate),4)
        print("\t", db_hz,'(hz) average')
        print('\t', db_liter_by_min,'(L/min)') # Display L/min instead of L/sec
        print(round(total_liters,4),'(L) total')
        print(round(secondes/60,4), '(min) total')
        print('-------------------------------------')

        if INFLUX_ENABLE == 'yes':
          # Format JSON for sending to InfluxDB
          current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
          json_body = [{
            "measurement": "temperature",
            "tags": {
                "serial": "WF-"+str(pin_input),
                "type": "WaterFlow"
            },
            "time": current_time,
            "fields": {
                "good_sample": float(db_good_sample),
                "hz": db_hz,
                "liter_by_min": db_liter_by_min
           }
          }]

          # Send data to InfluxDB
          DBconnection.sendJSON(json_body)

    except KeyboardInterrupt:
        print('\n CTRL+C - Exiting')
        GPIO.cleanup()
        sys.exit()
GPIO.cleanup()
print('Done')

