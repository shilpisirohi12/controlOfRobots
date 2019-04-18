#import cv2 as cv
import time
import random
import math
import RPi.GPIO as GPIO
from servos import servos
from tof import tof
#from printmaze import printmaze

class Navigation(tof, servos):
#random navigation program
    def __init__(self):
        super().__init__()
        self.fDist = float(self.forwardSensor()/25.4)
        self.rDist = float(self.rightDistance()/25.4)
        self.lDist = float(self.leftDistance()/25.4)
        
        self.lastMove = 4
        self.frontWall = 0
        self.rightWall = 0
        self.leftWall = 0
        
        GPIO.add_event_detect(self.LENCODER, GPIO.RISING, self.onLeftEncode)
        GPIO.add_event_detect(self.RENCODER, GPIO.RISING, self.onRightEncode)
        
    def navStart(self):
        self.csvReader()
        #orientation value based on last movement set to 4 to start
        self.lastMove = 4 
        #initialze wall flags (0-No Wall, 1-Wall) set to 0 to start
        self.frontWall = 0
        self.rightWall = 0
        self.leftWall = 0
        #pick a random value for next movement
    
        
        while True:
            self.fDist = float(self.forwardSensor()/25.4)
            print("******Front Sensor: ", self.fDist)
            self.nextMove = random.randint(1,4)
            self.visitCell()
            self.printCell()
            if self.fDist < 3:
                print("Too close to front wall... Back up")
                self.backUp()
            if self.frontWall == 1 and self.rightWall == 1 and self.leftWall == 1:
                self.turnAround()
                self.moveStraight(17, 9)
            else:
                if self.nextMove == 1:
                    if self.frontWall == 0:
                        print("Moving Forward")
                        self.moveStraight(17, 9)
                        self.lastMove = 0
                    else:
                        print("cant move forward, generate a new random number")
                        self.nextMove = random.randint(1,4)
                if self.nextMove == 2:
                    if self.rightWall == 0:
                        print("Moving Right")
                        self.rotateRight()
                        self.moveStraight(17, 9)
                    else:
                        print("cant move right, generate a new random number")
                        self.nextMove = random.randint(1,4)
                if self.nextMove == 3:
                    if self.leftWall == 0:
                        print("Moving left")
                        self.rotateLeft()
                        self.moveStraight(17, 9)
                    else:
                        print("cant move left, generate a new random number")
                        self.nextMove = random.randint(1,4)
            #remote print needed here
    def backUp(self):
        self.resetCounts()
        wheel_diam = 2.5
        
        avg_speed= 3/ 2
        rps_speed= round(float(avg_speed)/(2.5*3.14),2)
        cnt = 0
        req = 0
        
        value = self.interpolate(rps_speed, rps_speed, self.wheel_calibration)
        print("Value Interpolated: ",value)
        #cal_time=float(dist)/(float(value[2])*(2.61))
    
        tick_length = (float(wheel_diam) * 3.14)/32
        num_tick = 3 / float(tick_length)
        tick_count = self.rTick
        print("Ticks needed: ", num_tick)
        
        while(float(tick_count) <= num_tick):
            self.setSpeedsIPS(-2.0, -2.0)
            time.sleep(0.2)
            tick_count = self.rTick
            
        
    def visitCell(self):
        print("Visiting Cell...")
        self.fDist = float(self.forwardSensor()/25.4)
        self.rDist = float(self.rightDistance()/25.4)
        self.lDist = float(self.leftDistance()/25.4)
        
        if self.fDist < 14:
            #wall in front
            self.frontWall = 1
        else:
            self.frontWall = 0
        if self.rDist < 14:
            #wall to right
            self.rightWall = 1
        else:
            self.rightWall = 0
        if self.lDist < 14:
            #wall to left
            self.leftWall = 1
        else:
            self.leftWall = 0
            
        #print("&&&&Visit Results&&& Front: ", self.fDist, "Left: ", self.lDist, "Right: ", self.rDist)
        
    def printCell(self):
        #Print cell walls
        # _____
        #|     |
        #|     |
        #|     |
        #|.....|
        if self.frontWall == 1:
            frontChar = "_____"
        else:
            frontChar = "....."
        if self.rightWall == 1:
            rightChar = "|"
        else:
            rightChar = "."
        if self.leftWall == 1:
            leftChar = "|"
        else:
            leftChar = "."
            
        print(" ", frontChar, sep = "")
        for i in range(3):
            print(leftChar, "     ", rightChar, sep = "")
        print(leftChar,".....",rightChar, sep = "")
        
            
    def turnAround(self):
        print("Turning Around")
        self.resetCounts()

        wheel_diam = 2.5
        dist = 3.14 * 2
        cnt = 0
        tick_length = (float(wheel_diam)*3.14)/32
        num_tick = float(dist) / float(tick_length)
        tick_count = self.rTick
        
        while(float(tick_count) <= num_tick):
            self.setSpeedRPS(1.45, 1.45)
            time.sleep(0.1)
            tick_count = self.rTick
        self.setSpeedRPS(1.5,1.5)
        
    def rotateRight(self):
        self.resetCounts()
        print("Rotating Right")
        wheel_diam = 2.5
        dist = 3.14
        cnt = 0
        tick_length = (float(wheel_diam)*3.14)/32
        num_tick = float(dist) / float(tick_length)
        tick_count = self.rTick
        
        while(float(tick_count) <= num_tick):
            self.setSpeedRPS(1.55, 1.55)
            time.sleep(0.1)
            tick_count = self.rTick
        self.setSpeedRPS(1.5,1.5)

    def rotateLeft(self):
        
        self.resetCounts()
        print("Rotating Left")
        wheel_diam = 2.5
        dist = 3.14
        cnt = 0
        tick_length = (float(wheel_diam)*3.14)/32
        num_tick = float(dist) / float(tick_length)
        tick_count = self.rTick
        
        while(float(tick_count) <= num_tick):
            self.setSpeedRPS(1.45, 1.45)
            time.sleep(0.1)
            tick_count = self.rTick
        self.setSpeedRPS(1.5,1.5)
        
    def moveStraight(self,dist,sec_time):
        print("Moving Straight")
        self.resetCounts()
        wheel_diam = 2.5
        
        avg_speed=float(dist)/float(sec_time)
        rps_speed= round(float(avg_speed)/(2.5*3.14),2)
        cnt = 0
        req=0
        
        value = self.interpolate(rps_speed, rps_speed, self.wheel_calibration)
        print("Value Interpolated: ",value)
        #cal_time=float(dist)/(float(value[2])*(2.61))
    
        tick_length = (float(wheel_diam) * 3.14)/32
        num_tick = float(dist) / float(tick_length)
        tick_count = self.rTick
        print("Ticks needed: ", num_tick)
        
        while(float(tick_count) <= num_tick):
            self.lDist = float(self.leftDistance()/25.4)
            self.rDist = float(self.rightDistance()/25.4)
            self.fDist = float(self.forwardSensor()/25.4)
            
            distError = self.lDist - self.rDist
            
            #if no walls nearby, just move straight
            if self.fDist < 3:
                print("Too close to front wall... Back up")
                self.backUp()
                break
            if self.lDist > 12 and self.rDist > 12: 
                self.setSpeedsIPS(4.0,4.0)
            #else, use Pcontroller
            elif distError < 0:
                print("Left PControl Sensor Distance: ", self.lDist)
                self.leftpControl(7,0.6,self.lDist)
            else:
                print("Right PControl Sensor Distance: ", self.rDist)
                self.rightpControl(7,0.6,self.rDist)
            #print("Tick count: ", tick_count)
            #increased sleep, should help prevent scneario of sensor picking up edges of walls
            time.sleep(0.2)
            tick_count = self.rTick
        
        tick_count = 0
        self.stopRobot()
        time.sleep(0.5)
                        
    def leftpControl(self,r_t,k_p,y_t):
        # sidepControl controller function
        #self.followFlag = 0
        maxSpeed = 0.55 #RPS 0.6 worked for lab3.. testing different values
        self.e_t = float(r_t) - float(y_t)
        self.u_t = float(k_p) * self.e_t
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)
        self.n_rt = float(self.u_rt) + float(maxSpeed)
        self.runSpeed = self.fSat(self.n_rt)
        print("sidePControl Distance away: " ,(float(y_t)), "self.e_t: ",self.e_t, "self.runSpeed: ", self.runSpeed)
        if -0.5 <= abs(round(float(self.e_t),0)) <= 0.5:
            print("inside if----------------------------------->Moving Forward-- self.fSensorDist:",self.fDist,"\nr_t: ",r_t," k_p:",k_p)
            self.setSpeedsRPS(self.runSpeed, self.runSpeed)
        else:
            print("&&&&&Interpolate speeds PControl u_rt:",self.u_rt)
            
            #increasing k_p has fixed that. further testing required...
            #if self.followFlag == 0: **LEFT CONTROLS WORK.. write seperate right side**
            if float(self.e_t) > 0:
                if float(self.runSpeed) > maxSpeed:
                    self.setSpeedsRPS(self.runSpeed, maxSpeed)
                else:
                    self.setSpeedsRPS(maxSpeed, self.runSpeed)
            if float(self.e_t) < 0:
                #if abs(float(self.u_rt)) > maxSpeed: **old version.. should use runSpeed instead of u_rt..test incase**
                if float(self.runSpeed) > maxSpeed:
                    self.setSpeedsRPS(maxSpeed, self.runSpeed)
                else:
                    self.setSpeedsRPS(self.runSpeed, maxSpeed)
                    
    def rightpControl(self,r_t,k_p,y_t):
        # sidepControl controller function
        #self.followFlag = flag
        maxSpeed = 0.5 #RPS 0.6 worked for lab3.. testing different values
        minSpeed = 0.4 #RPS 0.25 ~ 2IPS
        self.e_t = float(r_t) - float(y_t)
        self.u_t = float(k_p) * self.e_t
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)
        #self.n_rt = float(self.u_rt) + float(maxSpeed)
        self.n_rt = float(minSpeed) - float(self.u_rt)
        self.runSpeed = self.fSat(self.n_rt)
        print("sidePControl Distance away: " ,(float(y_t)), "self.e_t: ",self.e_t, "self.runSpeed: ", self.runSpeed)
        if -0.5 <= abs(round(float(self.e_t),0)) <= 0.5:
            print("inside if----------------------------------->Moving Forward-- self.fSensorDist:",self.fDist,"\nr_t: ",r_t," k_p:",k_p)
            self.setSpeedsRPS(self.runSpeed, self.runSpeed)
        else:
            print("&&&&&Interpolate speeds PControl u_rt:",self.u_rt)                
            #if self.followFlag == 1:
            if float(self.e_t) < 0:
                if float(self.runSpeed) < minSpeed:
                    self.setSpeedsRPS(minSpeed, self.runSpeed)
                else:
                    self.setSpeedsRPS(self.runSpeed, minSpeed)
            if float(self.e_t) > 0:
                if abs(float(self.u_rt)) < minSpeed:
                    self.setSpeedsRPS(self.runSpeed, minSpeed)
                else:
                    self.setSpeedsRPS(minSpeed, self.runSpeed)
    
p1 = Navigation()
p1.navStart()