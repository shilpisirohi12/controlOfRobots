#import Mapping
import csv
from array import *
import cv2 as cv
import time
from ThreadedWebcam import ThreadedWebcam
import random
import math
import RPi.GPIO as GPIO
from servos import servos
from tof import tof
import Mapping


class Cell(servos):
    def __init__(self, west, north, east, south,weight=-1, visited=False):
        # There are 4 walls per cell
        # Wall values can be 'W', 'O', or '?' (wall, open, or unknown)
        self.west = west
        self.north = north
        self.east = east
        self.south = south
        self.weight=weight

        # Store whether or not the cell has been visited before
        self.visited = visited

class pathPlanning():

    def __init__(self):
        super().__init__()
        #self.maze = [
            #Mapping.Cell('W','W','O','O',False), Mapping.Cell('O','W','O','W',False), Mapping.Cell('O','W','O','W',False), Mapping.Cell('O','W','W','O',False),
            #Mapping.Cell('W','O','W','O',False), Mapping.Cell('W','W','O','O',False), Mapping.Cell('O','W','W','O',False), Mapping.Cell('W','O','W','O',False),
            #Mapping.Cell('W','O','W','O',False), Mapping.Cell('W','O','W','O',False), Mapping.Cell('W','O','O','W',False), Mapping.Cell('O','O','W','W',False),
            #Mapping.Cell('W','O','O','W',False), Mapping.Cell('O','O','O','W',False), Mapping.Cell('O','W','O','W',False), Mapping.Cell('O','W','W','W',False)
        #]
        self.maze = [
            Cell('W','W','?','?',False), Cell('?','W','?','?',False), Cell('?','W','?','?',False), Cell('?','W','W','?',False),
            Cell('W','?','?','?',False), Cell('?','?','?','?',False), Cell('?','?','?','?',False), Cell('?','?','W','?',False),
            Cell('W','?','?','?',False), Cell('?','?','?','?',False), Cell('?','?','?','?',False), Cell('?','?','W','?',False),
            Cell('W','?','?','W',False), Cell('?','?','?','W',False), Cell('?','?','?','W',False), Cell('?','?','W','W',False)
        ]

        self.shortestPathCounter=-1
        self.pos=[(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3),(2,0),(2,1),(2,2),(2,3),(3,0),(3,1),(3,2),(3,3)]
        self.paths=[]

    def reader(self):
        #Reading the mapping from the file
        with open('./mazeMap.csv', mode='r') as csvfile:
            csvReader = csv.DictReader(csvfile)
            cnt = 0
            for row in csvReader:
                x = float(row["Cell"])
                self.maze[cnt].west = row["west"]
                self.maze[cnt].north = row["north"]
                self.maze[cnt].east = row["east"]
                self.maze[cnt].south = row["south"]
                self.maze[cnt].visited = row["visit"]
                self.maze[cnt].weight=-1
                cnt += 1
            for i in range(16):
                print("i: ",i,"  ",self.maze[i].east," ",self.maze[i].west,"  ",self.maze[i].north,"  ",self.maze[i].south)
    def StartExecute(self,start,end):
        self.reader()
        print("start: ",self.pos[start-1][0]," ",self.pos[start-1][1])
        print("end: ",self.pos[end-1][0]," ",self.pos[end-1][1])
     # i will be rows and j will be columns. use this formula to get the cell number (i*4+j+1). Value in the list will be at (i*4+j)
        self.maze[end-1].weight=1
        allWgted=False
        while( not allWgted):
            print("inside while")
            for i in range(4):
                for j in range(4):
                    wgt = self.maze[i * 4 + j].weight
                    if self.maze[i*4+j].weight >0:
                        #wgt=self.maze[i*4+j].weight
                        if i>0 and self.maze[(i-1) * 4 + j].weight == -1:
                            self.maze[(i-1) * 4 + j].weight=wgt+1
                        if i<3 and self.maze[(i + 1) * 4 + j].weight == -1:
                            self.maze[(i + 1) * 4 + j].weight = wgt + 1
                        if j>0 and self.maze[i * 4 + (j-1)].weight == -1:
                            self.maze[i * 4 + (j-1)].weight = wgt + 1
                        if j<3 and self.maze[i * 4 + (j + 1)].weight == -1:
                            self.maze[i * 4 + (j + 1)].weight = wgt + 1
                        #print(self.maze[(i-1) * 4 + j].weight,"  ",self.maze[(i + 1) * 4 + j].weight,"  ",self.maze[i * 4 + (j-1)].weight,"  ",self.maze[i * 4 + (j + 1)].weight)
            flag=1
            for cnt in range(16):
                if self.maze[cnt].weight == -1:
                    flag=0
            if flag == 1:
                allWgted= True


        #printing mapping on the screen
        flag=0
        print("FINAL MAZE***************")
        for cnt in range(16):
            print(self.maze[cnt].weight,"  ",end = " ")
            flag=flag+1
            if flag ==4:
                print()
                flag=0

    def shortestPath(self,start,end):
        self.reader()
        print("inside shortest path")
        print("start: ",self.pos[start-1][0]," ",self.pos[start-1][1])
        print("end: ",self.pos[end-1][0]," ",self.pos[end-1][1])
        isShortPath=False
        possiblePaths=0
        openPaths=['C','C','C','C']
        while not isShortPath:
            pos=self.pos[start-1][0]*4+self.pos[start-1][1]
            print("pos: ",pos)
            if self.maze[pos].east=='W' and self.maze[pos].west=='W' and self.maze[pos].north=='W' and self.maze[pos].south=='W':
                print("No path from this cell")
                break
            else:
                if self.maze[pos].east=='O':
                    print("East is open")
                    possiblePaths+=1
                    openPaths[0]='Y'
                    self.path('E',start,end)
                if self.maze[pos].west=='O':
                    print("West is open")
                    possiblePaths+=1
                    openPaths[1]='Y'
                    self.path('W',start,end)
                if self.maze[pos].north=='O':
                    print("North is open")
                    possiblePaths+=1
                    openPaths[2]='Y'
                    self.path('N',start,end)
                if self.maze[pos].south=='O':
                    print("South is open")
                    possiblePaths+=1
                    openPaths[3]='Y'
                    self.path('S',start,end)
                print("openPaths: ",openPaths[0]," ",openPaths[1]," ",openPaths[2]," ",openPaths[3]," ",possiblePaths)


            for i in range(possiblePaths-1):
                if len(self.paths[i])<len(self.paths[i+1]):
                    #print(len(self.paths[i]),"  ",len(self.paths[i+1]))
                    self.shortestPathCounter=i
                else:
                    self.shortestPathCounter=i+1
            print("shortestPath: ",self.shortestPathCounter)
            print("square  numbers: ",self.paths[self.shortestPathCounter])

            if self.shortestPathCounter != -1:
                isShortPath=True
                self.moveTheRobot(start,end)
            #print(self.maze[self.pos[end-1][0]*4+self.pos[end-1][1]].east)


    def moveTheRobot(self,start,end):
        print("*************inside moveTheRobot***********************")
        stepsCnt=len(self.paths[self.shortestPathCounter])
        prevStep=self.paths[self.shortestPathCounter][0]
        for steps in range(stepsCnt):
            print("******************************")
            print(steps,"  ",self.paths[self.shortestPathCounter][steps])
            if self.paths[self.shortestPathCounter][steps]==start:
                print("At the starting point")
                prevStep=start
            else:
                prevStep=self.paths[self.shortestPathCounter][steps-1]
                #print("Start the movement")
                nextStep=self.paths[self.shortestPathCounter][steps]
                diff=prevStep-nextStep
                print("diff: ",diff)
                if diff == 4:
                    print("move up")
                    self.moveForward(self.maze,17,8)
                if diff == -4:
                    print("move right")
                if diff == -1:
                    print("move right")
                if diff == 1:
                    print("move left")

    def moveForward(self,maze, dist, sec_time):
        print("Moving Straight")
        self.resetCounts()
        wheel_diam = 2.5

        avg_speed = float(dist) / float(sec_time)
        rps_speed = round(float(avg_speed) / (2.5 * 3.14), 2)
        cnt = 0
        req = 0

        # value = servos.interpolate(rps_speed, rps_speed, servos.wheel_calibration)
        # print("Value Interpolated: ",value)
        # cal_time=float(dist)/(float(value[2])*(2.61))

        tick_length = (float(wheel_diam) * 3.14) / 32
        num_tick = float(dist) / float(tick_length)
        tick_count = servos.rTick
        print("Ticks needed: ", num_tick)

        while (float(tick_count) <= num_tick):
            lDist = float(tof.leftDistance() / 25.4)
            rDist = float(tof.rightDistance() / 25.4)
            fDist = float(tof.forwardSensor() / 25.4)

            distError = lDist - rDist

            # if no walls nearby, just move straight
            if fDist < 4:
                print("Too close to front wall... Back up")
                Mapping.backUp(maze)
                break
            if lDist > 12 and rDist > 12:
                servos.setSpeedsIPS(3.5, 3.5)
                # else, use Pcontrollerg
            elif distError < 0:
                # print("Left PControl Sensor Distance: ", lDist)
                Mapping.leftpControl(maze, 7.5, 0.4, lDist)
            else:
                # print("Right PControl Sensor Distance: ", rDist)
                Mapping.rightpControl(maze, 7.5, 0.4, rDist)
                # print("Tick count: ", tick_count)
                # increased sleep, should help prevent scneario of sensor picking up edges of walls
            time.sleep(0.2)
            tick_count = servos.rTick

        tick_count = 0
        servos.stopRobot()
        time.sleep(0.5)





    def path(self,dir,start,end):
        print("path values:----------------->>>>>>>>>>")
        sqNum=[]
        curPos=start
        print(curPos)

        if dir=='E':
            cnt=0
            sqNum.append(curPos)
            curPos=curPos+1
            sqNum.append(curPos)
            print(curPos,self.maze[curPos-1].east,self.maze[curPos-1].west,self.maze[curPos-1].north,self.maze[curPos-1].south)
            while(curPos!=end):
                if self.maze[curPos-1].north=='W' and self.maze[curPos-1].south=='W' and self.maze[curPos-1].east=='O':
                    curPos+=1
                    print(curPos)
                    cnt += 1
                    sqNum.append(curPos)
                elif self.maze[curPos-1].north=='O' and self.maze[curPos-1].south=='W':
                    curPos=curPos-4
                    print(curPos)
                    cnt += 1
                    sqNum.append(curPos)
                elif self.maze[curPos-1].east=='W' and self.maze[curPos-1].west=='W' and self.maze[curPos-1].north=='O':
                    curPos=curPos-4
                    print(curPos)
                    cnt += 1
                    sqNum.append(curPos)
                elif self.maze[curPos-1].east=='O' and self.maze[curPos-1].west=='W' and self.maze[curPos-1].south=='O' and self.maze[curPos-1].north=='W':
                    curPos=curPos+1
                    print(curPos)
                    cnt += 1
                    sqNum.append(curPos)
                elif self.maze[curPos-1].east=='W' and self.maze[curPos-1].west=='O' and self.maze[curPos-1].south=='O' and self.maze[curPos-1].north=='W':
                    curPos=curPos-1
                    print(curPos)
                    cnt += 1
                    sqNum.append(curPos)
                elif self.maze[curPos-1].east=='O' and self.maze[curPos-1].west=='O' and self.maze[curPos-1].south=='O' and self.maze[curPos-1].north=='W':
                    curPos=curPos+1
                    print(curPos)
                    cnt += 1
                    sqNum.append(curPos)
                if curPos+4==end and self.maze[curPos-1].south=='O':
                    curPos=curPos+1
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1
                if curPos-4==end and self.maze[curPos-1].north=='O':
                    curPos=curPos-4
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1
                if cnt >16:
                    break
            self.paths.append(sqNum)
        sqNum=[]
        if dir=='N':
            cnt=0
            sqNum.append(curPos)
            curPos=curPos-4
            print(curPos)
            sqNum.append(curPos)
            while(curPos!=end):
                if self.maze[curPos-1].east=='W' and self.maze[curPos-1].west=='W' and self.maze[curPos-1].north=='O':
                    curPos=curPos-4
                    print(curPos)
                    sqNum.append(curPos)
                    cnt+=1
                elif self.maze[curPos-1].east=='O' and self.maze[curPos-1].west=='W' and self.maze[curPos-1].north=='W':
                    curPos=curPos+1
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1
                elif self.maze[curPos-1].east=='O' and self.maze[curPos-1].west=='O' and self.maze[curPos-1].north=='W'  and self.maze[curPos-1].south=='W':
                    curPos=curPos+1
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1
                elif self.maze[curPos-1].east=='W' and self.maze[curPos-1].south=='O' and self.maze[curPos-1].north=='W':
                    curPos=curPos+4
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1
                elif self.maze[curPos-1].east=='W' and self.maze[curPos-1].south=='O' and self.maze[curPos-1].west=='W'  and self.maze[curPos-1].north=='W':
                    curPos=curPos+4
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1
                elif self.maze[curPos-1].east=='W' and self.maze[curPos-1].south=='W' and self.maze[curPos-1].west=='O':
                    curPos=curPos-1
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1
                elif self.maze[curPos-1].east=='O' and self.maze[curPos-1].south=='W' and self.maze[curPos-1].west=='W' and self.maze[curPos-1].north=='O':
                    curPos=curPos+1
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1
                if curPos+4==end and self.maze[curPos-1].south=='O':
                    curPos=curPos+1
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1
                if curPos-4==end and self.maze[curPos-1].north=='O':
                    curPos=curPos-4
                    print(curPos)
                    sqNum.append(curPos)
                    cnt += 1

                if cnt >16:
                    break
            self.paths.append(sqNum)

        #print(self.paths)


obj=pathPlanning()
#obj.StartExecute(13,7)
obj.shortestPath(13,7)
