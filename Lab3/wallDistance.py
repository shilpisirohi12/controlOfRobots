# wallDistance.py - *move robot to w/in 5inches of the wall using a P controlller*

from tof import tof
from servos import servos
import time
import math


class wallDistance(tof, servos):
    def __init__(self):
        super().__init__()
        self.e_t = self.u_t = self.y_t = self.u_rt = 0
        self.sleep_interval = 0.05
        self.isMax=-1

    def pControl(self, r_t, k_p):
        # P controller function
        self.currTime = time.monotonic()
        self.elapsedT = float(self.currTime) - float(self.startTime)
        self.e_t = float(r_t) - float(self.y_t)
        self.u_t = -(float(k_p) * self.e_t)
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)        
        #print("Distance: ", self.e_t, " elapsed Time: ",self.elapsedT)
        #self.u_rt = self.fSat(self.u_t)
        if abs(float(self.e_t)) < 0.2:
            #print("inside if----------------------------------->",abs(round(float(self.e_t),0)))
            self.stopRobot()

        else:
            #print("inside else----------------------------------->")
            self.setSpeedsRPS(self.u_rt,self.u_rt)
         

    def fSat(self, velSig):
        # Saturation function, if the desired speed is too great, set to max speed
        lowestRPS = min(float(self.maxRight), float(self.maxLeft), abs(float(self.minRight)), abs(float(self.minLeft)))
        if abs(float(velSig)) > float(lowestRPS):
            #print("inside max ifs ",lowestRPS)
            self.isMax=1
            return lowestRPS
        else:
            self.isMax=0
            return float(velSig)

    def towardsWall(self, desired_dist, p):
        self.csvReader()
        self.startTime = time.monotonic()
        #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@(float(self.forwardSensor())/25.4-float(desired_dist))@@@",(float(self.forwardSensor())/25.4-float(desired_dist)))
            

        self.y_t = float(self.forwardSensor())/25.4            
        if float(self.y_t) >45:
            print("******WARNING: EXCEEDING THE SENSOR's RANGE********")

        self.pControl(desired_dist, p)
        time.sleep(self.sleep_interval)  # might need to be half second or faster...

    def executeWallDist(self):
        self.csvReader()
        inputOption = 0
        print("*****MENU****")
        print("Choose Below Options to Execute the Function")
        print("Run Calibrations  ----> 1")
        print("Run Wall Distance Program ----> 2")
        print("Enter your choice: ", end="")
        inputOption = input()

        if int(inputOption) == 1:
            self.calibrateSpeed()
        elif int(inputOption) == 2:
            print("Please provide desired distance(in inches) of the goal: ", end="")
            desired_dist = input()
            print("Please provide proportional gain or correction error gain: ", end="")
            p = input()
            self.towardsWall(desired_dist, p)


#obj = wallDistance()
#obj.executeWallDist()


