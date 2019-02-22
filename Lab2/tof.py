# This program demonstrates the usage of the time of flight sensors.
# After running the program, move your hand in front of each sensor to verify that it's working.
# See https://learn.adafruit.com/adafruit-vl53l0x-micro-lidar-distance-sensor-breakout/overview for more details.

import time
import sys
from servos import servos
sys.path.append('/home/pi/VL53L0X_rasp_python/python')
import VL53L0X
import RPi.GPIO as GPIO


class tof(servos):
    def __init__(self):
        super().__init__()
        print("inside init")
        print("Pins that the sensors are connected to")
        LSHDN = 27
        FSHDN = 22
        RSHDN = 23

        DEFAULTADDR = 0x29  # All sensors use this address by default, don't change this
        LADDR = 0x2a
        RADDR = 0x2b

        print("Set the pin numbering scheme to the numbering shown on the robot itself.")
        GPIO.setmode(GPIO.BCM)

        print("Setup pins")
        GPIO.setup(LSHDN, GPIO.OUT)
        GPIO.setup(FSHDN, GPIO.OUT)
        GPIO.setup(RSHDN, GPIO.OUT)

        print("Shutdown all sensors")
        GPIO.output(LSHDN, GPIO.LOW)
        GPIO.output(FSHDN, GPIO.LOW)
        GPIO.output(RSHDN, GPIO.LOW)

        time.sleep(0.01)

        print("Initialize all sensors")
        self.lSensor = VL53L0X.VL53L0X(address=LADDR)
        self.fSensor = VL53L0X.VL53L0X(address=DEFAULTADDR)
        self.rSensor = VL53L0X.VL53L0X(address=RADDR)
        #print("lSensor:" ,self.lSensor )
        
        #to increase the timing budget to a more accurate but slower 200ms value
        self.lSensor.measurement_timing_budget=200000
        self.fSensor.measurement_timing_budget=200000
        self.rSensor.measurement_timing_budget=200000
        print("Connect the left sensor and start measurement")
        GPIO.output(LSHDN, GPIO.HIGH)
        time.sleep(0.01)
        self.lSensor.start_ranging(VL53L0X.VL53L0X_GOOD_ACCURACY_MODE)
        
        # Connect the right sensor and start measurement
        GPIO.output(RSHDN, GPIO.HIGH)
        time.sleep(0.01)
        self.rSensor.start_ranging(VL53L0X.VL53L0X_GOOD_ACCURACY_MODE)

        # Connect the front sensor and start measurement
        GPIO.output(FSHDN, GPIO.HIGH)
        time.sleep(0.01)
        self.fSensor.start_ranging(VL53L0X.VL53L0X_GOOD_ACCURACY_MODE)
        
        
    def leftDistance(self):
        return self.lSensor.get_distance()
    
    def rightDistance(self):
        return self.rSensor.get_distance()
    
    def forwardSensor(self):
        return self.fSensor.get_distance()

    def start(self):
        for count in range(1, 100):
            print("Get a measurement from each sensor:  ")
            lDistance = self.lSensor.get_distance()
            fDistance = self.fSensor.get_distance()
            rDistance = self.rSensor.get_distance()            

            # Print each measurement
            print("Left: {}\tFront: {}\tRight: {}".format(lDistance, fDistance, rDistance))

        # Stop measurement for all sensors
        self.lSensor.stop_ranging()
        self.fSensor.stop_ranging()
        self.rSensor.stop_ranging()

p1 = tof()
#p1.start()
