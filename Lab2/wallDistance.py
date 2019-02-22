# wallDistance.py - *move robot to w/in 5inches of the wall using a P controlller*

from tof import tof
from servos import servos
import time


class wallDistance(tof, servos):
    def __init__(self):
        super().__init__()
        self.e_t = self.u_t = self.y_t = self.u_rt = 0
        self.sleep_interval = 1

    def pControl(self, k_p, r_t):
        # P controller function
        self.e_t = float(r_t) - (float(self.y_t) / 25.4)
        self.u_t = float(k_p) * self.e_t
        self.u_rt = self.fSat(self.u_t)
        if self.e_t == 0:
            self.stopRobot()
            # might need a small range since sensors aren't 100% accurate..
            # setPWM to 1.5 STOP condition at expected distance
            # stay w/in infinite loop to check if robot is move
        else:
            speeds = self.getSpeedsIPS(self.u_rt, self.u_rt)
            lSpd = self.fSat(speeds[0])
            rSpd = self.fSat(speeds[1])
            self.y_t = ((lSpd + rSpd) * self.sleep_interval) / 2
            # setting the speed on the Servos
            self.setSpeedsIPS(lSpd, rSpd);

        print("pControl--->\n self.e_t: ", self.e_t, " self.u_t:", self.u_t, " self.u_rt:", self.u_rt)

    def fSat(self, velSig):
        # Saturation function, if the desired speed is too great, set to max speed
        # IPS speeds in .csv file has been changed to have a +/- value
        # min/max function (in servos) will have to be changed to find the largest +/- value
        if float(velSig) > abs(float(self.maxRight)) or float(velSig) > abs(float(self.maxLeft)):
            return max(self.maxRight, self.maxLeft)
        elif float(velSig) < abs(float(self.minLeft)) or float(velSig) < abs(float(self.minRight)):
            return min(self.minLeft, self.minRight)
        else:
            return float(velSig)

    def towardsWall(self, desired_dist, p):
        self.csvReader()
        self.y_t = self.forwardSensor()
        while True:
            print("Walking towards Wall")
            if self.y_t == desired_dist:
                self.stopRobot()
            else:
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


