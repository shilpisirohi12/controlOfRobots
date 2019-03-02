#wallFollowing.py
#TA suggestion: create multiple states as functions (wallFollowing, rightTurn90, leftTurn, etc)
#include servos.py
#include tof.py
from tof import tof
from servos import servos
import time
import math

class wallFollow(tof, servos):
    def __init__(self):
        super().__init__()
        self.e_t = self.u_t = self.u_rt =self.lpwm=self.rpwm= 0 
        self.sleep_interval = 0.05
        self.dist_from_wall=5
        self.lSensorDist=0
        self.rSensorDist=0
        self.fSensorDist=0
        self.followFlag=-1
        self.threshold=0.1
    
    def moveForward(self, r_t, k_p,y_t):
        print("move Forward")
        #time.sleep(0.02)
        self.pControl(r_t, k_p,y_t)
        
    def rightTurn90(self,r_t, k_p):
        print("turn Right")
        while float(self.forwardSensor())<float(305):
            self.lpwm=1.55
            self.rpwm=1.55
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)) / 20 * 4096))
            time.sleep(0.2)
        self.fSensorDist=self.forwardSensor()
        
    def leftTurn90(self,r_t, k_p):
        print("turn Left")
        while float(self.forwardSensor())<float(305):        
            self.lpwm=1.45
            self.rpwm=1.45
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)) / 20 * 4096))
            time.sleep(0.2)
        self.fSensorDist=self.forwardSensor()
        
    def rightTurnEdge(self, r_t, k_p):
        while float(self.rightDistance()/25.4) > float(r_t + 0.5):
            self.lpwm=1.68 #full power left
            self.rpwm=1.45 #right forward but slow
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)) / 20 * 4096))
            
            if float(self.forwardSensor()/25.4) < float(r_t):
                self.leftTurn90(r_t, k_p)
                
    def leftTurnEdge(self, r_t, k_p):
        while float(self.leftDistance()/25.4) > float(r_t):
            self.lpwm=1.53
            self.rpwm=1.3 #full power right
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)) / 20 * 4096))
            
            if float(self.forwardSensor()/25.4) < float(r_t):
                self.rightTurn90(r_t, k_p)
    
    def sidepControl(self,r_t,k_p,y_t):
        # sidepControl controller function
        maxSpeed = 0.60 #RPS
        self.e_t = float(r_t) - float(y_t)/25.4
        self.u_t = float(k_p) * self.e_t
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)
        self.n_rt = float(self.u_rt) + float(maxSpeed)
        self.runSpeed = self.fSat(self.n_rt)
        print("sidePControl Distance away: " ,(float(y_t)/25.4), "self.e_t: ",self.e_t, "self.runSpeed: ", self.runSpeed)
        if -0.5 <= abs(round(float(self.e_t),0)) <= 0.5:
            print("inside if----------------------------------->Moving Forward-- self.fSensorDist:",self.fSensorDist,"\nr_t: ",r_t," k_p:",k_p)
            self.moveForward(r_t, k_p,self.fSensorDist)
        else:
            print("&&&&&Interpolate speeds PControl u_rt:",self.u_rt)
            #current setup has some error if u_rt is too far from maxSpeed
            #increasing k_p has fixed that. further testing required...
            if self.followFlag == 0:
                if float(self.e_t) > 0:
                    if self.runSpeed > maxSpeed:
                        self.setSpeedsRPS(self.runSpeed, maxSpeed)
                    else:
                        self.setSpeedsRPS(maxSpeed, self.runSpeed)
                if float(self.e_t) < 0:
                    if abs(float(self.u_rt)) > maxSpeed:
                        self.setSpeedsRPS(maxSpeed, self.runSpeed)
                    else:
                        self.setSpeedsRPS(self.runSpeed, maxSpeed)
                
            if self.followFlag == 1:
                if float(self.e_t) > 0:
                    if abs(float(self.u_rt)) > maxSpeed:
                        self.setSpeedsRPS(maxSpeed, abs(float(self.u_rt)))
                    else:
                        self.setSpeedsRPS(abs(float(self.u_rt)), maxSpeed)
                if float(self.e_t) < 0:
                    if abs(float(self.u_rt)) > maxSpeed:
                        self.setSpeedsRPS(abs(float(self.u_rt)), maxSpeed)
                    else:
                        self.setSpeedsRPS(maxSpeed, abs(float(self.u_rt)))             
     
        
    def pControl(self, r_t, k_p,y_t):
        # P controller function
        self.e_t = float(r_t) - float(y_t)/25.4
        self.u_t = -(float(k_p) * self.e_t)
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)
        if abs(float(self.e_t)) < 0.5:
            print("&&&&&&TURNING&&&&&&&",abs(round(float(self.e_t),0)))
            if float(self.followFlag) ==1:
                time.sleep(0.02)
                self.leftTurn90(r_t, k_p)
            if float(self.followFlag) ==0:
                time.sleep(0.02)
                self.rightTurn90(r_t, k_p)
        else:
            speeds = self.lin_interpolate(abs(float(self.u_rt)),abs(float(self.u_rt)),self.wheel_calibration)
            self.lpwm=float(speeds[0])
            self.rpwm=float(speeds[1])
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)) / 20 * 4096))
            
    def fSat(self, velSig):
        # Saturation function, if the desired speed is too great, set to max speed
        lowestRPS = min(float(self.maxRight), float(self.maxLeft), abs(float(self.minRight)), abs(float(self.minLeft)))
        if abs(float(velSig)) > float(lowestRPS):
            print("inside max ifs ",lowestRPS)
            self.isMax=1
            return lowestRPS
        else:
            self.isMax=0
            return float(velSig)            

    def startWallFollow(self,r_t,k_p):
        currTime=time.monotonic()
        switchCnt = 0
        while True:
            self.lSensorDist = self.leftDistance()
            self.rSensorDist = self.rightDistance()
            self.fSensorDist = self.forwardSensor()
            time.sleep(0.01)
            if self.lSensorDist < self.rSensorDist and float(self.lSensorDist) < float(305):
                print("following wall wrt to leftSensor")
                self.followFlag = 0
                if (((float(r_t)) + 0.5) > (float(self.lSensorDist) / 25.4) > (float(r_t) - 0.5)):
                    self.moveForward(r_t, k_p,self.fSensorDist);
                else:
                    print("**********************Left Sensor do corrections***************")
                    self.sidepControl(r_t,k_p,self.lSensorDist)
            if self.lSensorDist > self.rSensorDist and float(self.rSensorDist) < float(305):
                print("following wall wrt to rightSensor")
                self.followFlag = 1
                if (((float(r_t)) + 0.5) > (float(self.rSensorDist) / 25.4) > (float(r_t) - 0.5)):
                    self.moveForward(r_t, k_p,self.fSensorDist);
                else:
                    print("**********************Right Sensor do corrections***************")
                    self.sidepControl(r_t,k_p,self.rSensorDist)

            if abs(float(self.fSensorDist/25.4)) < abs(float(r_t)+0.5) and self.followFlag == 0:
                self.rightTurn90(r_t,k_p)
                
            if abs(float(self.fSensorDist/25.4)) < abs(float(r_t)+0.5) and self.followFlag == 1:
                self.leftTurn90(r_t,k_p)

            if float(self.fSensorDist) > float(305) and float(self.lSensorDist) > float(305) and float(self.rSensorDist) > float(305):
                print("*******No Sensor Reading! UTURN!*****")
                if (self.followFlag == 0):
                    print("%%%%%%left Uturn%%%%%%")
                    time.sleep(0.1)
                    self.leftTurnEdge(r_t,k_p)
                if (self.followFlag == 1):
                    print("%%%%%%right Uturn%%%%%%")
                    time.sleep(0.1)
                    self.rightTurnEdge(r_t,k_p)
            time.sleep(0.1)     


    def executeWallFollow(self):
        self.csvReader()
        inputOption = 0
        print("*****MENU****")
        print("Choose Below Options to Execute the Function")
        print("Run Calibrations  ----> 1")
        print("Run Wall Follow Program ----> 2")
        print("Enter your choice: ", end="")
        inputOption = 2#input()

        if int(inputOption) == 1:
            self.calibrateSpeed()
        elif int(inputOption) == 2:
            print("Please provide desired distance(in inches) from the wall: ", end="")
            desired_dist = 5#input()
            print("Please provide proportional gain or correction error gain: ", end="")
            p = 1.2#input()
            self.startWallFollow(desired_dist, p)


obj = wallFollow()
obj.executeWallFollow()            

