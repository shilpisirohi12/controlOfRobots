# This program demonstrates usage of the servos.
# Keep the robot in a safe location before running this program,
# as it will immediately begin moving.
# See https://learn.adafruit.com/adafruit-16-channel-pwm-servo-hat-for-raspberry-pi/ for more details.

import time
import Adafruit_PCA9685
import RPi.GPIO as GPIO
import signal
import math
import csv
from decimal import Decimal, ROUND_HALF_EVEN

class servos:


    # To do initialization
    def __init__(self):
        print("--->Initialize Encoders")
        # The servo hat uses its own numbering scheme within the Adafruit library.
        # 0 represents the first servo, 1 for the second, and so on.
        self.LSERVO = 1
        self.RSERVO = 0
        
        # Set the standard value of Frequency to a variable
        self.frequency=50
        
        # Pins that the encoders are connected to
        self.LENCODER = 17
        self.RENCODER = 18        
        
        # Setting the start time
        self.t1 = time.monotonic()
        
        #Setting ticks to 0
        self.lTick = 0
        self.rTick = 0
        
        # Initialize the servo hat library.
        self.pwm = Adafruit_PCA9685.PCA9685()

        # Attach the Ctrl+C signal interrupt
        signal.signal(signal.SIGINT, self.ctrlC)

        # 50Hz is used for the frequency of the servos.
        self.pwm.set_pwm_freq(self.frequency)

        # Write an initial value of 1.5, which keeps the servos stopped.
        # Due to how servos work, and the design of the Adafruit library,
        # the value must be divided by 20 and multiplied by 4096.
        self.pwm.set_pwm(self.LSERVO, 0, math.floor(1.5 / 20 * 4096));
        self.pwm.set_pwm(self.RSERVO, 0, math.floor(1.5 / 20 * 4096));
        
        # Set the pin numbering scheme to the numbering shown on the robot itself.
        GPIO.setmode(GPIO.BCM)
        
        # Set encoder pins as input
        # Also enable pull-up resistors on the encoder pins
        # This ensures a clean 0V and 3.3V is always outputted from the encoders.
        GPIO.setup(self.LENCODER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.RENCODER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
       
        #Setting wheel Calibrations
        self.wheel_calibration=[]
        self.maxLeft=0
        self.maxRight=0
        self.minLeft=0
        self.minRight=0
        self.lSpeed=[]
        self.rSpeed=[]
        self.cf=3.14*2.61  # Setting value of diameter
       
   

    # This function is called when Ctrl+C is pressed.
    # It's intended for properly exiting the program.
    def ctrlC(self,signum, frame):
        print("Exiting")

        # Stop the servos
        self.pwm.set_pwm(self.LSERVO, 0, 0);
        self.pwm.set_pwm(self.RSERVO, 0, 0);
        # Stop measurement for all sensors
        self.lSensor.stop_ranging()
        self.fSensor.stop_ranging()
        self.rSensor.stop_ranging()        
        
        # Cleanup GPIO
        GPIO.cleanup()

        exit()

    # To reset the tick count (number of holes counted) to zero
    def resetCounts(self):
        #print("Count has been reset")
        self.t1= time.monotonic()
        self.lTick=0
        self.rTick=0
        #print(self.t1,"  ",self.lTick,"  ",self.rTick)


    # To return the left and right tick counts since the last call of reset or since the start of the program
    def getCounts(self):
        #print('Inside getCounts---->')
        res = (self.lTick,self.rTick)
        #print("Counts: ",res)
        return res
 
 
    
    # To return the instantaneous left and right wheel speeds (measured in revolutions per second)
    def getSpeeds(self):
        lWheel=rWheel=0
        t2= time.monotonic()
        eTime=t2-self.t1
        lRev=self.lTick/32
        rRev=self.rTick/32
        lWheel=lRev/eTime
        rWheel=rRev/eTime
        
        res=(lWheel, rWheel)
        #print("Speeds: ",res)
        return res
    
    # This function is called when the right encoder detects a rising edge signal.   
    def onLeftEncode(self,pin):
        #print("Left encoder ticked!")
        self.lTick=self.lTick+1

    # This function is called when the right encoder detects a rising edge signal.
    def onRightEncode(self,pin):
        #print("Right encoder ticked!")
        self.rTick=self.rTick+1


    def calibrateSpeed(self):
        leftWheel = 1.29
        
        print("****Wheel Calibration started****")
        arrLeft=[]
        #arrRight=[]
        arrSpeedL=[]
        arrSpeedR=[]        
        lSpeed=[]
        rSpeed=[]
        for i in range(41):
            leftWheel = leftWheel + 0.01
            rightWheel = float(leftWheel)
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(leftWheel / 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor(rightWheel / 20 * 4096))
            time.sleep(1)
            self.resetCounts()
            time.sleep(5)
            spd = self.getSpeeds()
            if leftWheel < 1.5:
                lspd = -spd[0]
            else:
                lspd = spd[0]
            if rightWheel > 1.5:
                rspd = -spd[1]
            else:
                rspd = spd[1]
                
            arrLeft.append(round(leftWheel,2))
            arrSpeedL.append(round(lspd,2))
            arrSpeedR.append(round(rspd,2))
            self.lSpeed.append(round(lspd,2))
            self.rSpeed.append(round(rspd,2))

        length= len(arrLeft)
        cnt=0
        for l in range(length):
            sublist=[]
            sublist.append(arrLeft[cnt])
            #sublist.append(arrRight[cnt])
            sublist.append(arrSpeedL[cnt])
            sublist.append(arrSpeedR[cnt])            
            cnt=cnt+1
            self.wheel_calibration.append(sublist)

        #print("wheel_calibration---->final size: ",len(self.wheel_calibration),"\n Calibrations")
        self.pwm.set_pwm(self.LSERVO, 0, math.floor(1.5 / 20 * 4096))
        self.pwm.set_pwm(self.RSERVO, 0, math.floor(1.5 / 20 * 4096))
        self.min_max()
        self.csvGenerator()        
        print("****Wheel Calibration completed****")
        
        
        
    def min_max(self):
        cnt=0
        for x in self.lSpeed:
            #Initializing the values
            if cnt ==0:
                self.maxLeft = self.minLeft =x
            if float(self.maxLeft)< float(x):
                self.maxLeft = x
            if float(self.minLeft) > float(x):
                self.minLeft = x
            cnt=cnt+1
        cnt=0
        for x in self.rSpeed:
            #Initializing the values
            if cnt ==0:
                self.maxRight=x
            if float(self.maxRight)< float(x):
                self.maxRight = x
            if float(self.minRight) > float(x):
                self.minRight = x
            cnt=cnt+1
        
    def setSpeedsRPS(self, rpsLeft, rpsRight):
        value = self.lin_interpolate(rpsLeft,rpsRight,self.wheel_calibration)
        self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(value[0]) / 20 * 4096))
        self.pwm.set_pwm(self.RSERVO, 0, math.floor(float(value[1]) / 20 * 4096))
                   
    def setSpeedsIPS(self,ipsLeft, ipsRight,isMax,flag):
        print("inside setSpeedsIPS",ipsLeft," ",ipsRight)
        rpsSpd=round((float(self.u_t))/(float(self.cf)),2)
        self.u_rt = self.fSat(rpsSpd)
        if isMax==1:
            if flag==1:
                lpwm=1.6
                rpwm=1.4
            elif flag==0:
                lpwm=1.4
                rpwm=1.6
        else:        
            speeds = self.lin_interpolate(abs(float(self.u_rt)),abs(float(self.u_rt)),self.wheel_calibration)
            print("Value Interpolated: ",float(speeds[0]), float(speeds[1]))
            if (float(speeds[0])>float(speeds[1])):
                if self.flag==1:
                    lpwm=float(speeds[0])+0.1
                    rpwm=float(speeds[1])-0.1
                elif self.flag==0:
                    lpwm=float(speeds[1])-0.1
                    rpwm=float(speeds[0])+0.1

            else:
                if self.flag==1:
                    lpwm=float(speeds[1])+0.1
                    rpwm=float(speeds[0])-0.1
                elif self.flag==0:
                    lpwm=float(speeds[0])-0.1
                    rpwm=float(speeds[1])+0.1
            print("self.isMax: ",isMax," flag: ",flag," lpwm: ",lpwm," rpwm: ",rpwm)   
        self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(lpwm)/ 20 * 4096))
        self.pwm.set_pwm(self.RSERVO, 0, math.floor((float(rpwm)-0.003) / 20 * 4096))        
        


    def fSat(self, velSig):
        # Saturation function, if the desired speed is too great, set to max speed
        # IPS speeds in .csv file has been changed to have a +/- value
        # min/max function (in servos) will have to be changed to find the largest +/- value
        if abs(float(velSig)) > abs(float(self.maxRight)) or abs(float(velSig)) > abs(float(self.maxLeft)):
            self.isMax=1
            return max(self.maxRight, self.maxLeft)
        else:
            self.isMax=0
            return float(velSig)
            
    def setSpeedsvw(self, v, w):
        R = abs(float(v)/float(w))
        d_mid = 3.95/2
        
        if(float(w) > 0):
            ips_L = float(w) * (R - d_mid)
            ips_R = float(w) * (R + d_mid)
        elif( float(w) < 0):
            ips_L = abs(float(w)) * (R + d_mid)
            ips_R = abs(float(w)) * (R - d_mid)
        
        v = self.setSpeedsIPS(ips_L, ips_R)
        return v
    
    def getSpeedsIPS(self,ipsLeft, ipsRight):
        #print("inside setSpeedsIPS",ipsLeft," ",ipsRight)
        rpsLeft=round((float(ipsLeft))/(float(self.cf)),2)
        rpsRight=round((float(ipsRight))/(float(self.cf)),2)
        value = self.interpolate(rpsLeft,rpsRight,self.wheel_calibration)
            
        print("Value Interpolated: ",float(value[0]), float(value[1]))
        return value

    def getSpeedsvw(self, v, w):
        R = abs(float(v)/float(w))
        d_mid = 3.95/2
        
        if(float(w) > 0):
            ips_L = float(w) * (R - d_mid)
            ips_R = float(w) * (R + d_mid)
        elif( float(w) < 0):
            ips_L = abs(float(w)) * (R + d_mid)
            ips_R = abs(float(w)) * (R - d_mid)
        
        v = self.getSpeedsIPS(ips_L, ips_R)
        return v
    
    def interpolate(self, rpsL, rpsR, data_lst):
        given_speedLeft = abs(float(rpsL))
        given_speedRight = abs(float(rpsR))
        count = 0
        nearest_value = 0
        left_spd=0
        right_spd=0
        for x, y, z in data_lst:
            if count == 0:
                distanceL = abs(float(given_speedLeft) - float(y))
                nearest_valueL = float(y)
                left_spd=float(x)
            if count > 0 and distanceL > abs(float(given_speedLeft) - float(y)):
                distanceL = abs(float(given_speedLeft) - float(y))
                nearest_valueL = float(y)
                left_spd=float(x)
            count = count + 1
            
        pwmDistL = abs(1.5 - left_spd)   
        if rpsL < 0:
            left_spd = 1.5 - pwmDistL
                    
        else:
            left_spd = 1.5 + pwmDistL
        
        count = 0
        for x, y, z in data_lst:
                if count==0:
                    #print("inside count==0")
                    distanceR = abs(float(given_speedRight) - float(z))
                    nearest_valueR = float(z)
                    right_spd=float(x)
                else:
                    if distanceR > abs(float(given_speedRight) - float(z)):
                        distanceR = abs(float(given_speedRight) - float(z))
                        nearest_valueR = float(z)
                        right_spd=float(x)
                count=count+1
        pwmDistR = abs(1.5 - right_spd)
        if rpsR > 0:
            right_spd = 1.5 - pwmDistR
        else:
            right_spd = 1.5 + pwmDistR
            
        for x, y, z in data_lst:
                if left_spd == float(x):
                    nearest_valueL = float(y)
                if right_spd == float(x):
                    nearest_valueR = float(z)
                    
        return (left_spd,right_spd,nearest_valueL,nearest_valueR,rpsL,rpsR)
    
    def lin_interpolate(self, rpsL, rpsR, data_lst):
        
        spdL = float(rpsL)
        spdR = float(rpsR)
        pwmL = pwmR = maxL = minL = maxR = minR = 0
        pwm_maxL = pwm_minL = pwm_maxR = pwm_minR = 0
        count = 0

        for x, y, z in data_lst:
            if count == 0:
                if float(y) == spdL:
                    pwmL = float(x)
                else:
                    minL = maxL = float(y)
            elif float(y) > spdL:
                if abs(spdL - float(y)) < abs(spdL - maxL):
                    maxL = float(y)
                    pwm_maxL = float(x)
            elif float(y) < spdL:
                if abs(spdL - float(y)) < abs(spdL - minL):
                    minL = float(y)
                    pwm_minL = float(x)
            elif float(y) == spdL:
                pwmL = float(x)
            count = count + 1
                
        if pwmL == 0 and (maxL - minL)!=0:
            #print("interpolate Left:", pwm_minL, pwm_maxL, minL, maxL, spdL)
            pwmL = (((pwm_minL*(maxL - spdL)) + (pwm_maxL*(spdL - minL))) / (maxL - minL))
            
        count = 0   
        for x, y, z in data_lst:
            if count == 0:
                if float(z) == spdR:
                    pwmR = float(x)
                else:
                    minR = maxR = float(z)
            elif float(z) > spdR:
                if abs(spdR - float(z)) < abs(spdR - maxR):
                    maxR = float(z)
                    pwm_maxR = float(x)
            elif float(z) < spdR:
                if abs(spdR - float(z)) < abs(spdR - minR):
                    minR = float(z)
                    pwm_minR = float(x)
            elif float(z) == spdR:
                pwmR = float(x)
            count = count + 1
                
        if pwmR == 0 and (maxL - minL)!=0:
            #print("Interpolate Right: ", pwm_minR, pwm_maxR, minR, maxR, spdR)
            pwmR = (pwm_minR*(maxR - spdR) + pwm_maxR*(spdR - minR)) / (maxR - minR)
                    
        return (pwmL,pwmR)
    
    def csvGenerator(self):
        with open('/home/pi/assignments/git/controlOfRobots/Lab2/calibrations.csv', 'w', newline='') as csvfile:
            fieldnames = ['PWM', 'RPS_Left', 'RPS_Right']
            csvWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csvWriter.writeheader()
            for x, y, z in self.wheel_calibration:
                csvWriter.writerow({'PWM':x,'RPS_Left':y,'RPS_Right':z})

    def csvReader(self):
        #print("inside csvReader")
        arrLeft=[]
        arrSpeedLeft=[]
        arrSpeedRight=[]
        with open('/home/pi/assignments/git/controlOfRobots/Lab2/calibrations.csv', mode='r') as csvfile:
            csvReader=csv.DictReader(csvfile)
            for row in csvReader:
                arrLeft.append(row["PWM"])
                arrSpeedLeft.append(row["RPS_Left"])
                arrSpeedRight.append(row["RPS_Right"])                
                self.lSpeed.append(row["RPS_Left"])
                self.rSpeed.append(row["RPS_Right"])

            cnt = 0
            self.wheel_calibration=[]
            for l in range(len(arrLeft)):
                sublist = []
                sublist.append(arrLeft[cnt])
                sublist.append(arrSpeedLeft[cnt])
                sublist.append(arrSpeedRight[cnt])                
                cnt = cnt + 1
                self.wheel_calibration.append(sublist)

            self.min_max()        
            print("mins n maxs: ",self.minLeft," ",self.maxLeft," ",self.minRight,"  ",self.maxRight)
            
    

    def stopRobot(self):
            self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(1.5) / 20 * 4096))
            self.pwm.set_pwm(self.RSERVO, 0, math.floor(float(1.5) / 20 * 4096))
            
                
p1=servos()
#p1.main_execute()