from servos import servos
import RPi.GPIO as GPIO
import time
import math


class main_menu(servos):

    def __init__(self):
        super().__init__()

        GPIO.add_event_detect(self.LENCODER, GPIO.RISING, self.onLeftEncode)
        GPIO.add_event_detect(self.RENCODER, GPIO.RISING, self.onRightEncode)

    def main_execute(self):
        inputOption = 0
        print("*****MENU****")
        print("Choose Below Options to Execute the Function")
        print("resetCounts()      ----> 1")
        print("getCounts()        ----> 2")
        print("getSpeeds()        ----> 3")
        print("calibrateSpeeds()  ----> 4")
        print("setSpeedsRPS()     ----> 5")
        print("setSpeedsIPS()     ----> 6")
        print("setSpeedsvw()      ----> 7")
        print("Load Calibrations  ----> 8")
        print("Task1              ----> 9")
        print("Stop Robot         ----> 11")
        print("Exit               ----> 99")

        while int(inputOption) != 99:
            print("Enter your  choice:", end="")
            inputOption = input()
            print("Choosen Option:", inputOption)
            if int(inputOption) == 1:
                self.resetCounts()
            elif int(inputOption) == 2:
                self.getCounts()
            elif int(inputOption) == 3:
                self.getSpeeds()
            elif int(inputOption) == 4:
                self.calibrateSpeed()
            elif int(inputOption) == 5:
                print("Please provide  value between", self.minLeft, "and +/-", self.maxLeft, " for the parameter rpsLeft: ",
                      end="")
                ls = input()
                print("Please provide  value between", self.minRight, "and +/-", self.maxRight,
                      " for the parameter rpsLeft: ", end="")
                rs = input()
                self.setSpeedsRPS(float(ls), float(rs))
            elif int(inputOption) == 6:
                iminLeft = round(float(self.minLeft) * float(self.cf), 2)
                imaxLeft = round(float(self.maxLeft) * float(self.cf), 2)
                iminRight = round(float(self.minRight) * float(self.cf), 2)
                imaxRight = round(float(self.maxRight) * float(self.cf), 2)

                print("Please provide  value between", iminLeft, "and +/-", imaxLeft, " for the parameter IPSLeft: ", end="")
                ls = input()
                print("Please provide  value between", iminRight, "and +/-", imaxRight, " for the parameter IPSRight: ",
                      end="")
                rs = input()

                self.setSpeedsIPS(float(ls), float(rs))
            elif int(inputOption) == 7:
                print("Please provide a value for velocity v: ", end="")
                v = input()
                print("Please provide a value for angular velocity w: ", end="")
                w = input()

                self.setSpeedsvw(v, w)

            elif int(inputOption) == 8:
                self.csvReader()
            elif int(inputOption) == 11:
                self.stopRobot()
            elif inputOption != '99':
                print("Wrong Choice. Please choose from the mentioned options")
        print("***********EXITING***********")


p1 = main_menu()
p1.main_execute()
