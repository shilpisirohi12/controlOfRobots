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
        self.e_t = self.u_t = self.y_t = self.u_rt =self.lpwm=self.rpwm= 0 #self.y_t take care of only forward sensor distance
        self.sleep_interval = 0.05
        self.dist_from_wall=5
        self.lSensorDist=0
        self.rSensorDist=0
        self.fSensorDist=0
        self.followFlag=-1
        self.threshold=0.1
    
    def moveForward(self, r_t, k_p,y_t):
        print("move Forward")
        self.pControl(r_t, k_p,y_t)
        
    def rightTurn(self,r_t, k_p):
        print("turn Right")
        while(float(self.forwardSensor())<float(305) or float(self.forwardSensor())<float(r_t)):
            self.lpwm=1.6
            self.rpwm=1.6
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)-0.003) / 20 * 4096))
            time.sleep(self.sleep_interval)
        self.fSensorDist=self.forwardSensor()
        
    def leftTurn(self,r_t, k_p):
        print("turn Left")
        while(float(self.forwardSensor())<float(305) or float(self.forwardSensor())<float(r_t)):        
            self.lpwm=1.4
            self.rpwm=1.4
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)-0.003) / 20 * 4096))
            time.sleep(self.sleep_interval)
        self.fSensorDist=self.forwardSensor()        
    
    def sidepControl(self,r_t,k_p,y_t):
        # sidepControl controller function
        self.e_t = float(r_t) - float(y_t)/25.4
        self.u_t = float(k_p) * self.e_t
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)
        print("self.e_t: ",self.e_t,"self.u_t:",self.u_t,"self.u_rt: ",self.u_rt)
        if abs(round(float(self.e_t),0))== 0 or abs(round(float(self.e_t),0)) == 1 or abs(round(float(self.e_t),0)) == 2:
            print("inside if----------------------------------->",abs(round(float(self.e_t),0))," self.fSensorDist:",self.fSensorDist,"\nr_t: ",r_t," k_p:",k_p)
            self.moveForward(r_t, k_p,self.fSensorDist)
        else:
            print("inside else----------------------------------->",self.followFlag)
            if self.isMax==1:
                if  self.followFlag==0:
                    self.lpwm=1.35
                    self.rpwm=1.4
                if  self.followFlag==1:
                    self.lpwm=1.45
                    self.rpwm=1.3                    
            else:        
                speeds = self.lin_interpolate(abs(float(self.u_rt)),abs(float(self.u_rt)),self.wheel_calibration)
                print("Value Interpolated: ",float(speeds[0]), float(speeds[1]))
                if (float(speeds[0])>float(speeds[1])):
                    if  self.followFlag==0:
                        self.lpwm=float(speeds[0])+self.threshold
                        self.rpwm=float(speeds[1])
                    elif self.followFlag==1:
                        self.lpwm=float(speeds[0])
                        self.rpwm=float(speeds[1])+self.threshold                       

                else:
                    if  self.followFlag==0:
                        self.lpwm=float(speeds[0])-self.threshold
                        self.rpwm=float(speeds[1])+self.threshold
                    elif self.followFlag==1:
                        self.lpwm=float(speeds[0])+self.threshold
                        self.rpwm=float(speeds[1])-self.threshold 

                    #print("else----->flag: ",self.flag," lpwm: ",lpwm," rpwm: ",rpwm)
            print("self.isMax: ",self.isMax," self.lpwm: ",self.lpwm," rself.pwm: ",self.rpwm)   
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)-0.003) / 20 * 4096))        
        
     
        
    def pControl(self, r_t, k_p,y_t):
        # P controller function
        self.e_t = float(r_t) - float(y_t)/25.4
        self.u_t = float(k_p) * self.e_t
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)        
        print("self.e_t: ", self.e_t, " self.u_t: ", self.u_t,"  rpsSpd: ",rpsSpd," self.u_rt: ",self.u_rt," k_p: ",k_p," r_t: ",r_t)
        #self.u_rt = self.fSat(self.u_t)
        if abs(round(float(self.e_t),0))== 0 or abs(round(float(self.e_t),0)) == 1 or abs(round(float(self.e_t),0)) == 2:
            print("inside if----------------------------------->",abs(round(float(self.e_t),0)))
            if float(self.followFlag) ==1:
                time.sleep(0.02)
                if float(self.rSensorDist) < ((float(r_t) / 25.4) + 1) and float(self.rSensorDist) > ((float(r_t) / 25.4) - 1):
                    self.leftTurn(r_t, k_p)
                else:
                    self.rightTurn(r_t,k_p)
            if float(self.followFlag) ==0:
                time.sleep(0.02)
                if float(self.lSensorDist)<((float(r_t)/25.4)+1) and float(self.lSensorDist)>((float(r_t)/25.4)-1):
                    self.rightTurn(r_t, k_p)
                else:
                    self.leftTurn(r_t,k_p)
        else:
            #print("inside else----------------------------------->")
            if self.isMax==1:
                self.lpwm=1.6
                self.rpwm=1.4
            else:        
                speeds = self.lin_interpolate(abs(float(self.u_rt)),abs(float(self.u_rt)),self.wheel_calibration)
                print("Value Interpolated: ",float(speeds[0]), float(speeds[1]))
                if (float(speeds[0])>float(speeds[1])):
                    self.lpwm=float(speeds[0])+0.1
                    self.rpwm=float(speeds[1])-0.1
                else:
                    self.lpwm=float(speeds[1])+0.1
                    self.rpwm=float(speeds[0])-0.1
                    #print("else----->flag: ",self.flag," lpwm: ",lpwm," rpwm: ",rpwm)
            print("self.isMax: ",self.isMax," self.lpwm: ",self.lpwm," rself.pwm: ",self.rpwm)   
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)-0.003) / 20 * 4096))
            
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

    def startWallFollow(self,r_t,k_p):        
        while True:
            self.lSensorDist=self.leftDistance()
            self.rSensorDist=self.rightDistance()
            self.fSensorDist=self.forwardSensor()
            time.sleep(0.01)
            if self.lSensorDist<self.rSensorDist:
                print("following wall wrt to leftSensor")
                self.followFlag=0
                if float(self.lSensorDist)<((float(r_t)/25.4)+1) and float(self.lSensorDist)>((float(r_t)/25.4)-1):
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@IFS@@@@@@@@@@@@@@@@@@@@@@")
                    self.moveForward(r_t, k_p,self.fSensorDist);
                else:
                    print("**********************Left Sensor do corrections***************")
                    self.sidepControl(r_t,k_p,self.lSensorDist)
            else:
                print("following wall wrt to rightSensor")
                self.followFlag=1
                if float(self.rSensorDist)<((float(r_t)/25.4)+1) and float(self.rSensorDist)>((float(r_t)/25.4)-1):
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@IFS@@@@@@@@@@@@@@@@@@@@@@")
                    self.moveForward(r_t, k_p,self.fSensorDist);
                else:
                    print("**********************Right Sensor do corrections***************")
                    self.sidepControl(r_t,k_p,self.rSensorDist)

    def executeWallFollow(self):
        inputOption = 0
        print("*****MENU****")
        print("Choose Below Options to Execute the Function")
        print("Run Calibrations  ----> 1")
        print("Run Wall Follow Program ----> 2")
        print("Enter your choice: ", end="")
        inputOption = input()

        if int(inputOption) == 1:
            self.calibrateSpeed()
        elif int(inputOption) == 2:
            print("Please provide desired distance(in inches) from th wall: ", end="")
            desired_dist = input()
            print("Please provide proportional gain or correction error gain: ", end="")
            p = input()
            self.startWallFollow(desired_dist, p)


obj = wallFollow()
obj.executeWallFollow()            

