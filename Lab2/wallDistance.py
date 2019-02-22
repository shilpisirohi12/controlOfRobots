#wallDistance.py - *move robot to w/in 5inches of the wall using a P controlller*

from tof import tof
from servos import servos
import time

class wallDistance(tof,servos):
    def __init__(self):
        super().__init__()
        self.e_t = self.u_t =self. y_t = self.u_rt = 0


    def pControl(self,y_t,k_p,r_t):
        #P controller function
        self.e_t = float(r_t) - float(y_t)
        self.u_t = float(k_p) * self.e_t
        self.u_rt = self.fSat(self.u_t)
        if self.e_t == 0:
            self.stopRobot()
            #might need a small range since sensors aren't 100% accurate..
            #setPWM to 1.5 STOP condition at expected distance
            #stay w/in infinite loop to check if robot is move
        else:
            speeds=self.getSpeedsIPS(self.u_rt, self.u_rt)
            lSpd=self.fSat(speeds[0])
            rSpd=self.fSat(speeds[1])

            # setting the speed on the Servos
            self.setSpeedsIPS(lSpd,rSpd);



    def fSat(self,velSig):
        #Saturation function, if the desired speed is too great, set to max speed
        #IPS speeds in .csv file has been changed to have a +/- value
        #min/max function (in servos) will have to be changed to find the largest +/- value
        if velSig > abs(self.maxRight) or velSig >abs(self.maxLeft):
            return max(self.maxRight,self.maxLeft)
        elif velSig < abs(self.minLeft) or velSig < abs(self.minRight):
            return min(self.minLeft,self.minRight)
        else:
            return velSig

    def towardsWall(self,desired_dist,p):
        while True:
            print("Walking towards Wall")
            self.pControl(desired_dist,p,self.forwardSensor())
            time.sleep(1) #might need to be half second or faster...



    def executeWallDist(self):
        inputOption = 0
        print("*****MENU****")
        print("Choose Below Options to Execute the Function")
        print("Run Calibrations  ----> 1")
        print("Load Calibrations  ----> 2")
        print("Run Wall Distance Program ----> 3")
        print("Enter your choice: ",end="")
        inputOption=input()

        if int(inputOption) == 1:
            self.calibrateSpeed()
        elif int(inputOption) == 2:
            self.csvReader()
        elif int(inputOption) == 3:
            print("Please provide desired distance of the goal: ", end="")
            desired_dist = input()
            print("Please provide proportional gain or correction error gain: ", end="")
            p = input()
            self.towardsWall(desired_dist,p)

obj=wallDistance()
obj.executeWallDist()


