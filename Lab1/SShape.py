from servos import servos
import time
import math
import RPi.GPIO as GPIO

class SShape(servos):
    
    def __init__(self):
        super().__init__()
        GPIO.add_event_detect(self.LENCODER, GPIO.RISING, self.onLeftEncode)
        GPIO.add_event_detect(self.RENCODER, GPIO.RISING, self.onRightEncode)

    
    def calculation(self,radius,Stime,orientation):
        d_mid = 4.25/2
        velocity=(3.14*float(radius))/(float(Stime))  
        w = abs(velocity / float(radius) )
        if int(orientation) == 1:
            w = -w

        v = self.getSpeedsvw(velocity, w)                
        return v
        
        

    def makeSCurve(self,radius, Stime, orientation):    
        self.resetCounts()
        wheel_diam = 2.61
        d_mid = 4.25/2
        if float(Stime) == 0:
            print("Time cannot be zero, please try again!")
            return
        else:
            v = self.calculation(radius, Stime, orientation)
            
        
        if v[0] != 0:
            print("RPS Speeds desired: " ,v[4], " , " ,v[5])
            print("RPS Speeds obtained: " ,v[2], " , ", v[3])
            adjustment=(v[0] - v[1])/3
            
            if abs(v[4] - v[2]) > 0.02 or abs(v[5] - v[3]) > 0.02:
                print("Difference in desired and obtained speeds detected! Unexpected results may occur!",
                      "Press 'Y' to continue or any input to cancel:" ,end = "")
                choice = input()
                if choice == 'y' or choice == "Y":
                    self.pwm.set_pwm(self.LSERVO, 0, math.floor((float(v[0])) / 20 * 4096))
                    self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(v[1])) / 20 * 4096))
                else:
                    return
            
            else:
                if int(orientation) == 1:
                    self.pwm.set_pwm(self.LSERVO, 0, math.floor((float(v[0]) + 0.07) / 20 * 4096))
                    self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(v[1]) ) / 20 * 4096))
                    
                else:
                    self.pwm.set_pwm(self.LSERVO, 0, math.floor((float(v[0])) / 20 * 4096))
                    self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(v[1]) + adjustment) / 20 * 4096))
                    
            if float(orientation) == 1:
                #if moving CW, right wheel is on the inside, set d_mid to negative
                d_mid = -d_mid
                
            half_circumR = (float(radius) + float(d_mid)) * 3.14
            tick_length = (float(wheel_diam) * 3.14)/32
            num_tick = float(half_circumR) / float(tick_length)
            tick_count = self.rTick
            #print("Ticks needed: ", num_tick)
            while(float(tick_count) <= num_tick):
                tick_count = self.rTick
                time.sleep(1)
                #print("Tick count: ", tick_count)
        
        tick_count = 0
        self.stopRobot()
        
    def shape_execute(self):
        inputOption=0
        print("*****MENU****")
        print("Choose Below Options to Execute the Function")
        print("Load Calibrations  ----> 1")
        print("Make S Curve       ----> 2")
        print("Stop Robot         ----> 11")          
        print("Exit               ----> 99")

        while int(inputOption) != 99:
            print("Enter your  choice:", end ="")
            inputOption=input()
            print("Choosen Option:" , inputOption)
            if int(inputOption) == 1:
                self.csvReader()
            elif int(inputOption) == 2:
                print("Enter radius in inches: ", end="")
                rad=input()
                print("Enter time in seconds: ",end="")
                ts=input()
                print("Indicate orientation (1 - CW, 0 - CCW): ", end="")
                orient=input()
                self.makeSCurve(rad,ts,orient)
            elif int(inputOption) ==11:
                self.stopRobot()                
            elif inputOption != '99':
                print("Wrong Choice. Please choose from the mentioned options")        
        print("***********EXITING***********")
        
s=SShape()
s.shape_execute()