from tof import tof
from servos import servos
import time
import math

class wallFollow(tof, servos):
    def __init__(self):
        super().__init__()
        self.e_t = self.u_t = self.y_t = self.u_rt =self.lpwm=self.rpwm= 0 #self.y_t take care of only forward sensor distance

        self.dist_from_wall=5
        self.lSensorDist=0
        self.rSensorDist=0
        self.fSensorDist=0
        self.followFlag=-1
        self.threshold=0.1
        self.thresholdDist=5        
        self.r_t=0
        self.k_p=0
        self.isFirstL=False
        self.cntL=0
        self.prev_etL=-100
        self.isFirstR=False
        self.cntR=0
        self.prev_etR=-100

    
    def moveForward(self, r_t, k_p,y_t):
        print("move Forward")
        #time.sleep(0.02)
        self.pControl(r_t, k_p,y_t)
        
    def rightTurn(self,r_t, k_p):
        print("turn Right")        
        self.lpwm=1.55
        self.rpwm=1.55
        self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
        self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)-0.003) / 20 * 4096))
        time.sleep(0.02)
        self.fSensorDist=self.forwardSensor()
        
    def leftTurn(self,r_t, k_p):
        print("turn Left")     
        self.lpwm=1.45
        self.rpwm=1.45
        self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
        self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)-0.003) / 20 * 4096))
        time.sleep(0.02)
        self.fSensorDist=self.forwardSensor()        
    
    def sidepLeftControl(self,r_t,k_p,y_t):
        # sidepControl controller function
        self.e_t = float(r_t) - float(y_t)/25.4        
        self.u_t = float(k_p) * self.e_t
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)
        
        if self.isFirstL == False:
            self.prev_etL=self.e_t
            self.isFirstL= True
        else:
            if self.prev_etL<self.e_t:
                self.cntL=self.cntL+1
                
                
        print("self.e_t: ",self.e_t,"self.u_t:",self.u_t,"self.u_rt: ",self.u_rt)
        if 0 <= abs(round(float(self.e_t),0)) <= 2:
            print("inside if of sidepLeftControl------------------------>",abs(round(float(self.e_t),0))," self.fSensorDist:",self.fSensorDist,"\nr_t: ",r_t," k_p:",k_p)
            self.moveForward(r_t, k_p,self.fSensorDist)
            time.sleep(0.5)
        else:
            print("inside else of sidepLeftControl--------------------------->",self.followFlag)
            if self.isMax==1:
                if  self.followFlag==0:
                    self.lpwm=1.35
                    self.rpwm=1.4
            else:        
                speeds = self.lin_interpolate(abs(float(self.u_rt)),abs(float(self.u_rt)),self.wheel_calibration)
                print("Value Interpolated for sidepLeftControl: ",float(speeds[0]), float(speeds[1]))
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

            print("self.isMax: ",self.isMax," self.lpwm: ",self.lpwm," rself.pwm: ",self.rpwm)   
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm)/ 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm)-0.003) / 20 * 4096))

    def sidepRightControl(self, r_t, k_p, y_t):
        # sidepControl controller function
        self.e_t = float(r_t) - float(y_t) / 25.4
        self.u_t = float(k_p) * self.e_t
        rpsSpd = round((float(self.u_t)) / (float(self.cf)), 2)
        self.u_rt = self.fSat(rpsSpd)

        if self.isFirstR == False:
            self.prev_etR = self.e_t
            self.isFirstR = True
        else:
            if self.prev_etR < self.e_t:
                self.cntR = self.cntR + 1

        print("self.e_t: ", self.e_t, "self.u_t:", self.u_t, "self.u_rt: ", self.u_rt)
        if 0 <= abs(round(float(self.e_t), 0)) <= 2:
            print("inside if of sidepRightControl--------------------------->", abs(round(float(self.e_t), 0)), " self.fSensorDist:",self.fSensorDist, "\nr_t: ", r_t, " k_p:", k_p)
            self.moveForward(r_t, k_p, self.fSensorDist)
            time.sleep(0.5)
        else:
            print("inside else of sidepRightControl--------------------------->", self.followFlag)

            if self.isMax == 1:
                if self.followFlag == 1:
                    self.lpwm = 1.6
                    self.rpwm = 1.55
            else:
                speeds = self.lin_interpolate(abs(float(self.u_rt)), abs(float(self.u_rt)), self.wheel_calibration)
                print("Value Interpolated for sidepControl: ", float(speeds[0]), float(speeds[1]))
                if (float(speeds[0]) > float(speeds[1])):
                    if self.followFlag == 1:
                        self.lpwm = float(speeds[0])
                        self.rpwm = float(speeds[1]) + self.threshold

                else:
                    if self.followFlag == 1:
                        self.lpwm = float(speeds[0]) + self.threshold
                        self.rpwm = float(speeds[1]) - self.threshold

            print("self.isMax of sidepRightControl: ", self.isMax, " self.lpwm: ", self.lpwm, " rself.pwm: ", self.rpwm)
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(self.lpwm) / 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(self.rpwm) - 0.003) / 20 * 4096))


    def pControl(self, r_t, k_p,y_t):
        # P controller function
        self.e_t = float(r_t) - float(y_t)/25.4
        self.u_t = float(k_p) * self.e_t
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)        
        print("self.e_t: ", self.e_t, " self.u_t: ", self.u_t,"  rpsSpd: ",rpsSpd," self.u_rt: ",self.u_rt," k_p: ",k_p," r_t: ",r_t)
        #self.u_rt = self.fSat(self.u_t)
        if abs(round(float(self.e_t),0))== 0 or abs(round(float(self.e_t),0)) == 1 or abs(round(float(self.e_t),0)) == 2:
            print("inside if of pControl-------------------------------->",abs(round(float(self.e_t),0)))
            if float(self.followFlag) ==1:
                print("<----Moving Left for right wall follow in pControl---->")
                time.sleep(0.02)
                self.leftTurn(r_t, k_p)
            if float(self.followFlag) ==0:
                print("<----Moving right for left wall follow in pControl---->")
                time.sleep(0.02)
                self.rightTurn(r_t, k_p)
        else:
            #print("inside else----------------------------------->")
            if self.isMax==1:
                self.lpwm=1.6
                self.rpwm=1.4
            else:        
                speeds = self.lin_interpolate(abs(float(self.u_rt)),abs(float(self.u_rt)),self.wheel_calibration)
                print("Value Interpolated: ",float(speeds[0]), float(speeds[1]))
                if (float(speeds[0])>float(speeds[1])):
                    self.lpwm=float(speeds[0])+0.05
                    self.rpwm=float(speeds[1])-0.05
                else:
                    self.lpwm=float(speeds[1])+0.05
                    self.rpwm=float(speeds[0])-0.05
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

    def moveBack(self):

        self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(1.4)/ 20 * 4096))
        self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(1.6)-0.003) / 20 * 4096))
        time.sleep(0.1)
        if self.followFlag == 0:
            print("inside moveBack---> turning right")
            self.rightTurn(self.r_t,self.k_p)
        if self.followFlag == 1:
            print("inside moveBack---> turning left")
            self.leftTurn(self.r_t,self.k_p)
        time.sleep(0.1)
            
    
    def startWallFollow(self,r_t,k_p):
        currTime=time.monotonic()
        self.r_t=r_t
        self.k_p=k_p
        while True:
            self.lSensorDist = self.leftDistance()
            self.rSensorDist = self.rightDistance()
            self.fSensorDist = self.forwardSensor()
            time.sleep(0.01)
            print("**********************************************")
            print("if and else: ",self.ifcnt,"  ",self.elsecnt,"\n Left, right and forward: ",self.lSensorDist," ",self.rSensorDist,"  ",self.fSensorDist)
            print("**********************************************")
            if self.cntL>3 or self.cntR>3:
                print("!!!!!!!!!!!!!MOVE BACK BACK BACK!!!!!!!!!!!!!!!!!!!!!!!!!!")
                self.moveBack()
                #time.sleep(0.05)
                self.cnt=0
            
            if self.lSensorDist < self.rSensorDist:
                print("following wall wrt to leftSensor")
                self.followFlag = 0
                if (((float(r_t)) + 1) > (float(self.lSensorDist) / 25.4) > (float(r_t) - 0.5)):
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@IFS@@@@@@@@@@@@@@@@@@@@@@", ((float(r_t)) + 1) ,">", (float(self.lSensorDist) / 25.4) ,">", (float(r_t) - 1))
                    self.moveForward(r_t, k_p,self.fSensorDist);
                else:
                    print("**********************Left Sensor do corrections***************")
                    self.lturn = True;
                    self.sidepLeftControl(r_t,k_p,self.lSensorDist)
                    
            if self.lSensorDist > self.rSensorDist:
                print("following wall wrt to rightSensor")
                self.followFlag = 1
                if (((float(r_t)) + 1) > (float(self.rSensorDist) / 25.4) > (float(r_t) - 0.5)):
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@IFS@@@@@@@@@@@@@@@@@@@@@@")
                    self.moveForward(r_t, k_p,self.fSensorDist)
                else:
                    print("**********************Right Sensor do corrections***************")
                    self.rturn  =True
                    self.sidepRightControl(r_t,k_p,self.rSensorDist)

            if self.followFlag==0 and ((float(self.fSensorDist) / 25.4)<float(self.thresholdDist)):
                print("*****************************inside followFlag==0")
                self.rightTurn(r_t,k_p)
                time.sleep(0.1)

            if self.followFlag==1 and ((float(self.lSensorDist) / 25.4)<float(self.thresholdDist)):
                print("*****************************inside followFlag==1")
                self.leftTurn(r_t,k_p)
                time.sleep(0.1)

                
            if(float(self.fSensorDist)/25.4 > float(r_t)) and (float(self.rSensorDist)/25.4 >float(r_t)) and (self.followFlag < 0):
               print("inside if --------->1")
               self.moveForward(r_t,k_p,self.forwardSensor())
               time.sleep(0.1)                 
               self.moveForward(r_t,k_p,self.forwardSensor())
               
            if(float(self.fSensorDist)/25.4 > float(r_t)) and (float(self.leftDistance())/25.4 >(float(r_t)+3)) and (self.followFlag == 0):
               print("inside if --------->2  ",float(self.leftDistance())/25.4,"  ",(float(r_t)+3))
               self.moveForward(r_t,k_p,self.forwardSensor())
               time.sleep(0.1) 
               self.leftTurn(r_t,k_p)
               
            if(float(self.fSensorDist)/25.4 > float(r_t)) and (self.rSensorDist/25.4 >(float(r_t)+3)) and (self.followFlag == 1):
               print("inside if --------->3")
               self.moveForward(r_t,k_p,self.forwardSensor())
               time.sleep(0.1)                
               self.rightTurn(r_t,k_p)               

            if (float(time.monotonic())-float(currTime))>500:
                time.sleep(0.02)
                if (self.followFlag == 0) and (float(self.leftDistance())/25.4)>(float(r_t)):
                    print("no reading available for leftsensor--> turn robot left")
                    self.moveForward(r_t,k_p,self.forwardSensor())
                    time.sleep(0.1)                
                    self.leftTurn(r_t,k_p)
                if (self.followFlag == 1) and (float(self.rightDistance())/25.4)>(float(r_t)+5):
                    print("no reading available for rightsensor--> turn robot right")
                    self.moveForward(r_t,k_p,self.forwardSensor())                    
                    time.sleep(0.1)
                    self.rightTurn(r_t,k_p)




    def executeWallFollow(self):
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
            p = 0.6#input()
            self.startWallFollow(desired_dist, p)


obj = wallFollow()
obj.executeWallFollow()            

