#!/usr/bin/dev python3

import time
from Reader import Thermometer

while True:
    therm = Thermometer()
    print(therm.read())
    time.sleep(1)

