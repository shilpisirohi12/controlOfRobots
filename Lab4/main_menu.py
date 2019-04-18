import Mapping
from servos import servos
import RPi.GPIO as GPIO
import time
import math


class main_menu(servos):

    def __init__(self):
        super().__init__()
        #self.maze = [
            #Mapping.Cell('W','W','O','O',False), Mapping.Cell('O','W','O','W',False), Mapping.Cell('O','W','O','W',False), Mapping.Cell('O','W','W','O',False),
            #Mapping.Cell('W','O','W','O',False), Mapping.Cell('W','W','O','O',False), Mapping.Cell('O','W','W','O',False), Mapping.Cell('W','O','W','O',False),
            #Mapping.Cell('W','O','W','O',False), Mapping.Cell('W','O','W','O',False), Mapping.Cell('W','O','O','W',False), Mapping.Cell('O','O','W','W',False),
            #Mapping.Cell('W','O','O','W',False), Mapping.Cell('O','O','O','W',False), Mapping.Cell('O','W','O','W',False), Mapping.Cell('O','W','W','W',False)
        #]
        self.maze = [
            Mapping.Cell('W','W','?','?',False), Mapping.Cell('?','W','?','?',False), Mapping.Cell('?','W','?','?',False), Mapping.Cell('?','W','W','?',False),
            Mapping.Cell('W','?','?','?',False), Mapping.Cell('?','?','?','?',False), Mapping.Cell('?','?','?','?',False), Mapping.Cell('?','?','W','?',False),
            Mapping.Cell('W','?','?','?',False), Mapping.Cell('?','?','?','?',False), Mapping.Cell('?','?','?','?',False), Mapping.Cell('?','?','W','?',False),
            Mapping.Cell('W','?','?','W',False), Mapping.Cell('?','?','?','W',False), Mapping.Cell('?','?','?','W',False), Mapping.Cell('?','?','W','W',False)
        ]

        #GPIO.add_event_detect(self.LENCODER, GPIO.RISING, self.onLeftEncode)
        #GPIO.add_event_detect(self.RENCODER, GPIO.RISING, self.onRightEncode)

    def main_execute(self):
        inputOption = 0
        print("*****MENU****")
        print("Choose Below Options to Execute the Function")
        print("Calibrate           ----> 1")
        print("Load Calibrations   ----> 2")
        print("Localization        ----> 3")
        print("Mapping             ----> 4")
        print("Path Planning       ----> 5")
        print("Stop Robot         ----> 11")
        print("Exit               ----> 99")

        while int(inputOption) != 99:
            print("Enter your  choice:", end="")
            inputOption = input()
            print("Choosen Option:", inputOption)
            if int(inputOption) == 1:
                self.calibrateSpeed()
            elif int(inputOption) == 2:
                self.csvReader()
            elif int(inputOption) == 3:
                Mapping.localization(self.maze)
            elif int(inputOption) == 4:
                Mapping.mappingStart(self.maze)
                #Mapping Menu
            elif int(inputOption) == 5:
                #pathPlanning Menu
                print("WORK IN PROGRESS")
            elif int(inputOption) == 11:
                self.stopRobot()
            elif inputOption != '99':
                print("Wrong Choice. Please choose from the mentioned options")
        print("***********EXITING***********")
                
p1 = main_menu()
p1.main_execute()