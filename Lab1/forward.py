from servos import servos
import RPi.GPIO as GPIO
import time
import math

class forward(servos):
    #ser=servos()
    def __init__(self):
        super().__init__()
        
        GPIO.add_event_detect(self.LENCODER, GPIO.RISING, self.onLeftEncode)
        GPIO.add_event_detect(self.RENCODER, GPIO.RISING, self.onRightEncode)
        
        self.forward_calibration=[]
     
     
    
    def moveStraight(self,dist,sec_time):
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
        
        if rps_speed>0:
            print("*************************")
            print("Requested Speed: ",rps_speed)
            print("Maximum robot can go with the speed of ",value[2])
            print("If it is fine. Then press 'Y' to make robot move. Else press 'N' to cancel:",end="")
            response=input()
            if response=='y' or response=='Y':
                self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(value[0])/ 20 * 4096))
                self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(value[1])-0.003)/ 20 * 4096))

                #print("cal_time: ",cal_time)
                #time.sleep(round(cal_time,0))
                while(float(tick_count) <= num_tick):
                    tick_count = self.rTick
                    #print("Tick count: ", tick_count)
        
                tick_count = 0
                self.stopRobot()
                                    
                    
        else:
                self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(value[0])/ 20 * 4096))
                self.pwm.set_pwm(self.RSERVO, 0, math.floor(float(value[1])/ 20 * 4096))
                
                self.stopRobot()
                
            
    def forward_execute(self):
        inputOption=0
        print("*****MENU****")
        print("Choose Below Options to Execute the Function")
        print("Load Calibrations  ----> 1")
        print("Move Straight      ----> 2")
        print("Stop Robot         ----> 11")          
        print("Exit               ----> 99")

        while int(inputOption) != 99:
            print("Enter your  choice:", end ="")
            inputOption=input()
            print("Choosen Option:" , inputOption)
            if int(inputOption) == 1:
                self.csvReader()
            elif int(inputOption) == 2:
                print("Enter distance in inches: ", end="")
                dist=input()
                print("Enter time in seconds: ",end="")
                ts=input()
                self.moveStraight(dist,ts)
            elif int(inputOption) ==11:
                self.stopRobot()                
            elif int(inputOption) != 99:
                print("Wrong Choice. Please choose from the mentioned options")
                            
    
f=forward()
#f.csvReader()
#f.moveStraight(1,1)
f.forward_execute()