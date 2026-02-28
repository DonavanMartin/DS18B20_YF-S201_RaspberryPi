#!/usr/bin/env python
# ════════════════════════════════════════════════════════════════════════════════
# YF-S201 Water Flow Meter - Production/Debug Mode Configuration
# ════════════════════════════════════════════════════════════════════════════════
# --debug → Print all measurements and debug info to console
# (no --debug) → Silent operation, only print on startup and errors

import time, sys
import RPi.GPIO as GPIO
from datetime import datetime
from datetime import timezone
import os
import argparse

# Database Connection
scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
os.chdir(scriptPath)
sys.path.append("../InfluxDB")
import DBconnection

# Enable line buffering for immediate console output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)

# Command-line argument parsing
parser = argparse.ArgumentParser(description='YF-S201 measurement application for Raspberry Pi')
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-p', '--pin', help='Data Raspberry Pin. Look at GPIO PINOUT', required=True)
parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode with verbose logging')
args = parser.parse_args()
DEBUG = args.debug

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


print(f"[START] YF-S201 Water Flow Meter starting on pin {args.pin}")
if DEBUG:
    print("[MODE] Debug mode - Verbose logging enabled")
else:
    print("[MODE] Production mode - Silent operation (errors only)")

# Configuration
pin_input = int(args.pin)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_input, GPIO.IN)

# Variables
total_liters = 0
secondes = 0

# Sampling
sample_rate = 1  # Sample each 1 second
time_start = 0
time_end = 0
period = 0
hz = []       # Frequency (important!)
m = 0.0021    # See linear.pdf

# Data
db_good_sample = 0
db_hz = 0
db_liter_by_min = 0

print(f"[FLOW] [READY] YF-S201 ready - sampling every {sample_rate} seconds")

# Add diagnostic mode for first 3 seconds
print("[FLOW] [DEBUG] Reading raw GPIO values for 3 seconds...")
time_end_diag = time.time() + 3
gpio_samples = []
while time.time() < time_end_diag:
    val = GPIO.input(pin_input)
    gpio_samples.append(val)
    time.sleep(0.01)

if DEBUG or len(set(gpio_samples)) == 1:
    print(f"[FLOW] [WARN] GPIO always reads: {gpio_samples[0]}")
    if len(set(gpio_samples)) == 1:
        print("[FLOW] [ERROR] GPIO is stuck! Check wiring or sensor power")
        print("[FLOW] Continuing anyway...")
else:
    print(f"[FLOW] [OK] GPIO is changing: {len(set(gpio_samples))} states detected")

while True:
    # Start / End
    time_start = time.time()
    init_time_start = time_start  # undetect last edge
    time_end = time_start + sample_rate
    hz = []
    sample_total_time = 0

    # Edge
    current = GPIO.input(pin_input)
    edge = current # Rising edge / Falling edge
    
    if DEBUG:
        print(f"[FLOW] [SAMPLE] Starting 1s sample - Initial state: {current}")

    try:
        while time.time() <= time_end:
            t = time.time()
            v = GPIO.input(pin_input)
            if current != v and current == edge:
                period = t - time_start  # Impulse period
                new_hz = 1/period
                hz.append(new_hz)  # Period = 1/period
                sample_total_time += t - time_start
                time_start = t

                if DEBUG:
                    print(f"[FLOW] [EDGE] {round(new_hz, 4)} Hz")
            current = v
            time.sleep(0.0001)  # Sleep 100µs to reduce CPU usage
        
        if DEBUG and len(hz) == 0:
            print("[FLOW] [WARN] No edges detected in this sample")

        # Sums
        if DEBUG:  # Only print stats in debug mode
            print('[FLOW] -------------------------------------')
            print(f'[FLOW] Current Time: {time.asctime(time.localtime())}')

        secondes += sample_rate
        nb_samples = len(hz)
        if nb_samples > 0:
            average = sum(hz) / float(len(hz))
            # Calculate % of good samples in time range
            good_sample = sample_total_time/sample_rate
            if DEBUG:
                print("[FLOW]\t", round(sample_total_time, 4), '(sec) good sample')
            db_good_sample = round(good_sample*100, 4)
            if DEBUG:
                print("[FLOW]\t", db_good_sample, '(%) good sample')
            average = average * good_sample
        else:
            average = 0
            db_good_sample = 0
        average_liters = average*m*sample_rate
        total_liters += average_liters
        db_hz = round(average, 4)
        db_liter_by_min = round(average_liters*(60/sample_rate), 4)
        if DEBUG:
            print("[FLOW]\t", db_hz, '(Hz) average')
            print('[FLOW]\t', db_liter_by_min, '(L/min)')  # Display L/min instead of L/sec
            print('[FLOW]\t', round(total_liters, 4), '(L) total')
            print('[FLOW]\t', round(secondes/60, 4), '(min) total')
            print('[FLOW] -------------------------------------')

        # Format JSON for sending to InfluxDB
        current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        json_body = [{
          "measurement": "water_flow",
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
        DBconnection.sendJSON(json_body, sensor_type="FLOW", debug=DEBUG)

    except KeyboardInterrupt:
        print('\n CTRL+C - Exiting')
        GPIO.cleanup()
        sys.exit()
GPIO.cleanup()
print('Done')