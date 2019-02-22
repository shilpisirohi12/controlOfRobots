# wallDistance.py - *move robot to w/in 5inches of the wall using a P controlller*

from tof import tof
from servos import servos
import time
import math


class wallDistance(tof, servos):
    def __init__(self):
        super().__init__()
        self.e_t = self.u_t = self.y_t = self.u_rt = 0
        self.sleep_interval = 1

    def pControl(self, k_p, r_t):
        # P controller function
        self.e_t = float(r_t) - (float(self.y_t) / 25.4)
        self.u_t = float(k_p) * self.e_t
        rpsLeft=round((float(self.u_t))/(float(self.cf)),2)
        print("self.e_t: ", self.e_t, " self.u_t: ", self.u_t," rpsLeft: ",rpsLeft," k_p: ",k_p," r_t: ",r_t)
        #self.u_rt = self.fSat(self.u_t)
        if self.e_t == 0:
            self.stopRobot()
            # might need a small range since sensors aren't 100% accurate..
            # setPWM to 1.5 STOP condition at expected distance
            # stay w/in infinite loop to check if robot is move
        else:
            speeds = self.lin_interpolate(rpsLeft,rpsLeft,self.wheel_calibration)
            lSpd = self.fSat(speeds[0])
            print("lSpd:  ",lSpd)


    def fSat(self, velSig):
        # Saturation function, if the desired speed is too great, set to max speed
        # IPS speeds in .csv file has been changed to have a +/- value
        # min/max function (in servos) will have to be changed to find the largest +/- value
        if abs(float(velSig)) > abs(float(self.maxRight)) or abs(float(velSig)) > abs(float(self.maxLeft)):
            print("inside max ifs ",max(self.maxRight, self.maxLeft))
            return max(self.maxRight, self.maxLeft)
        elif abs(float(velSig)) < abs(float(self.minLeft)) or abs(float(velSig)) < abs(float(self.minRight)):
            print("inside min ifs ",min(self.minLeft, self.minRight))
            return min(self.minLeft, self.minRight)
        else:
            return("float(velSig): ",float(velSig))
            return float(velSig)

    def towardsWall(self, desired_dist, p):
        self.csvReader()
        while True:
            print("Walking towards Wall---",self.forwardSensor())
            self.y_t = self.forwardSensor()
            print("y_t: ",self.y_t,"  float(self.y_t)/25.4:",float(self.y_t)/25.4);
            if float(self.y_t)/25.4 >45:
                print("******WARNING: EXCEEDING THE SENSOR's RANGE********")

            if round(float(self.y_t),0) == round(float(desired_dist),0):
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>inside if of towardsWall>>>>>>>>>>>>>>")
                self.stopRobot()
            else:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>inside else of towardsWall>>>>>>>>>>>>>>")
                self.pControl(desired_dist, p)
            time.sleep(self.sleep_interval)  # might need to be half second or faster...

    def executeWallDist(self):
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


obj = wallDistance()
obj.executeWallDist()


