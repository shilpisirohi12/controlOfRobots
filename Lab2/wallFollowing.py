#wallFollowing.py
#TA suggestion: create multiple states as functions (wallFollowing, rightTurn, leftTurn, etc)
#include servos.py
#include tof.py
from tof import tof
from servos import servos
import time
import math

class wallFollow(tof, servos):
    def __init__(self):
        super().__init__()
        self.e_t = self.u_t = self.y_t = self.u_rt = 0
        self.sleep_interval = 0.05
        self.dist_from_wall=5
        self.lSensorDist=0
        self.rSensorDist=0
        self.fSensorDist=0
        self.followFlag=-1
    
    def moveForward(self):
        println("move Forward")
        
    def rightTurn(self):
        println("turn Right")
        
    def leftTurn(self):
        println("turn Left")
    
    def startWallFollow(self):
        self.lSensorDist=self.leftDistance()
        self.rSensorDist=self.rightDistance()
        self.fSensorDist=self.forwardSensor()
        
        if self.lSensorDist<self.rSensorDist:
            print("following wall wrt to leftSensor")
            self.followFlag=0
        else:
            print("following wall wrt to rightSensor")
            self.followFlag=1
        self.moveForward();    
	#safeDist = some value where the sensor is not reading a wall
	#while fDistance > safeDist
	
	
