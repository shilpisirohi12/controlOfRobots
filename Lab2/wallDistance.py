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
        self.flag=-1
        self.isMax=-1

    def pControl(self, r_t, k_p):
        # P controller function
        self.e_t = float(r_t) - float(self.y_t)
        self.u_t = float(k_p) * self.e_t
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)        
        print("self.e_t: ", self.e_t, " self.u_t: ", self.u_t,"  rpsSpd: ",rpsSpd," self.u_rt: ",self.u_rt," k_p: ",k_p," r_t: ",r_t)
        #self.u_rt = self.fSat(self.u_t)
        if abs(round(float(self.e_t),0))== 0 or abs(round(float(self.e_t),0)) == 1 or abs(round(float(self.e_t),0)) == 2:
            print("inside if----------------------------------->",abs(round(float(self.e_t),0)))
            self.stopRobot()
            # might need a small range since sensors aren't 100% accurate..
            # setPWM to 1.5 STOP condition at expected distance
            # stay w/in infinite loop to check if robot is move
        else:
            #print("inside else----------------------------------->")
            if self.isMax==1:
                if self.flag==1:
                    lpwm=1.6
                    rpwm=1.4
                elif self.flag==0:
                    lpwm=1.4
                    rpwm=1.6
            else:        
                speeds = self.lin_interpolate(abs(float(self.u_rt)),abs(float(self.u_rt)),self.wheel_calibration)
                print("Value Interpolated: ",float(speeds[0]), float(speeds[1]))
                #lSpd = self.fSat(speeds[0])
                #print("lSpd:  ",lSpd)
                if (float(speeds[0])>float(speeds[1])):
                     if self.flag==1:
                        lpwm=float(speeds[0])+0.1
                        rpwm=float(speeds[1])-0.1
                     elif self.flag==0:
                        lpwm=float(speeds[1])-0.1
                        rpwm=float(speeds[0])+0.1
                     #print("if----->flag: ",self.flag," lpwm: ",lpwm," rpwm: ",rpwm)

                else:
                    if self.flag==1:
                        lpwm=float(speeds[1])+0.1
                        rpwm=float(speeds[0])-0.1
                    elif self.flag==0:
                        lpwm=float(speeds[0])-0.1
                        rpwm=float(speeds[1])+0.1
                    #print("else----->flag: ",self.flag," lpwm: ",lpwm," rpwm: ",rpwm)
            print("self.isMax: ",self.isMax," flag: ",self.flag," lpwm: ",lpwm," rpwm: ",rpwm)   
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(rpwm)-0.003) / 20 * 4096))                
                
            
            


    def fSat(self, velSig):
        # Saturation function, if the desired speed is too great, set to max speed
        # IPS speeds in .csv file has been changed to have a +/- value
        # min/max function (in servos) will have to be changed to find the largest +/- value
        if abs(float(velSig)) > abs(float(self.maxRight)) or abs(float(velSig)) > abs(float(self.maxLeft)):
            print("inside max ifs ",max(self.maxRight, self.maxLeft))
            self.isMax=1
            return max(self.maxRight, self.maxLeft)
        else:
            self.isMax=0
            return float(velSig)

    def towardsWall(self, desired_dist, p):
        self.csvReader()
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@(float(self.forwardSensor())/25.4-float(desired_dist))@@@",(float(self.forwardSensor())/25.4-float(desired_dist)))
            
        while True:
            if((float(self.forwardSensor())/25.4-float(desired_dist))<0):
                self.flag=0 #move backwards
            else:
                self.flag=1 #move forward
            #print("Walking towards Wall---",self.forwardSensor())
            self.y_t = float(self.forwardSensor())/25.4
            #print("y_t: ",self.forwardSensor(),"  float(self.y_t)/25.4:",float(self.y_t));
            if float(self.y_t) >45:
                print("******WARNING: EXCEEDING THE SENSOR's RANGE********")
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


