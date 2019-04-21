# Lab 4 mapping plans

#TO DO:
#	Determine best data structure to ensure mapping reaches all cells (queue or list might be best)
#	Determine best method to reach un mapped cells (if found necessary during testing **I think it will**)
#	

# ________________
#|   |   |   |   |
#| 1 | 2 | 3 | 4 |
#|___|___|___|___|
#|   |   |   |   |
#| 5 | 6 | 7 | 8 |
#|___|___|___|___|
#|   |   |   |   |
#| 9 | 10| 11| 12|
#|___|___|___|___|
#|   |   |   |   |
#| 13| 14| 15| 16|
#|___|___|___|___|
import csv
import cv2 as cv
import time
from ThreadedWebcam import ThreadedWebcam
import random
import math
import RPi.GPIO as GPIO
from servos import servos
from tof import tof


class Cell:
    def __init__(self, west, north, east, south, visited = False):
        # There are 4 walls per cell
	# Wall values can be 'W', 'O', or '?' (wall, open, or unknown)
        self.west = west
        self.north = north
        self.east = east
        self.south = south
		
	# Store whether or not the cell has been visited before
        self.visited = visited

		
# Helper function that verifies all the walls of the maze
def detectMazeInconsistencies(maze):
	# Check horizontal walls
	for i in range(3):
		for j in range(4):
			pos1 = i * 4 + j
			pos2 = i * 4 + j + 4
			hWall1 = maze[pos1].south
			hWall2 = maze[pos2].north		
			assert hWall1 == hWall2, " Cell " + str(pos1) + "'s south wall doesn't equal cell " + str(pos2) + "'s north wall! ('" + str(hWall1) + "' != '" + str(hWall2) + "')"
	
	# Check vertical walls
	for i in range(4):
		for j in range(3):
			pos1 = i * 4 + j
			pos2 = i * 4 + j + 1
			vWall1 = maze[pos1].east
			vWall2 = maze[pos2].west
			assert vWall1 == vWall2, " Cell " + str(pos1) + "'s east wall doesn't equal cell " + str(pos2) + "'s west wall! ('" + str(vWall1) + "' != '" + str(vWall2) + "')"

			
# You don't have to understand how this function works
def printMaze(maze, hRes = 4, vRes = 2):
	assert hRes > 0, "Invalid horizontal resolution"
	assert vRes > 0, "Invalid vertical resolution"

	# Get the dimensions of the maze drawing
	hChars = 4 * (hRes + 1) + 2
	vChars = 4 * (vRes + 1) + 1
	
	# Store drawing into a list
	output = [" "] * (hChars * vChars - 1)
	
	# Draw top border
	for i in range(1, hChars - 2):
		output[i] = "_"
	
	# Draw bottom border
	for i in range(hChars * (vChars - 1) + 1, hChars * (vChars - 1) + hChars - 2):
		output[i] = "¯"
	
	# Draw left border
	for i in range(hChars, hChars * (vChars - 1), hChars):
		output[i] = "|"
		
	# Draw right border
	for i in range(2 * hChars - 2, hChars * (vChars - 1), hChars):
		output[i] = "|"

	# Draw newline characters
	for i in range(hChars - 1, hChars * vChars - 1, hChars):
		output[i] = "\n"
	
	# Draw dots inside maze
	for i in range((vRes + 1) * hChars, hChars * (vChars - 1), (vRes + 1) * hChars):
		for j in range(hRes + 1, hChars - 2, hRes + 1):
			output[i + j] = "·"
	
	# Draw question marks if cell is unvisited
	for i in range(4):
		for j in range(4):
			cellNum = i * 4 + j
			if maze[cellNum].visited:
				continue
			origin = (i * hChars * (vRes + 1) + hChars + 1) + (j * (hRes + 1))
			for k in range(vRes):
				for l in range(hRes):
					output[origin + k * hChars + l] = "?"
	
	# Draw horizontal walls
	for i in range(3):
		for j in range(4):
			cellNum = i * 4 + j
			origin = ((i + 1) * hChars * (vRes + 1) + 1) + (j * (hRes + 1))
			hWall = maze[cellNum].south
			for k in range(hRes):
				output[origin + k] = "-" if hWall == 'W' else " " if hWall == 'O' else "?"
	
	# Draw vertical walls
	for i in range(4):
		for j in range(3):
			cellNum = i * 4 + j
			origin = hChars + (hRes + 1) * (j + 1) + i * hChars * (vRes + 1)
			vWall = maze[cellNum].east
			for k in range(vRes):
				output[origin + k * hChars] = "|" if vWall == 'W' else " " if vWall == 'O' else "?"

	# Print drawing
	print(''.join(output))

FPS_SMOOTHING = 0.9

# Window names
WINDOW1 = "Adjustable Mask - Press Esc to quit"
WINDOW2 = "Detected Blobs - Press Esc to quit"

# Default HSV ranges
# Note: the range for hue is 0-180, not 0-255
minH =  140; minS = 155; minV =  60;
maxH = 180; maxS = 255; maxV = 255;


# These functions are called when the user moves a trackbar
def onMinHTrackbar(val):
    # Calculate a valid minimum red value and re-set the trackbar.
    global minH
    global maxH
    minH = min(val, maxH - 1)
    cv.setTrackbarPos("Min Hue", WINDOW1, minH)


def onMinSTrackbar(val):
    global minS
    global maxS
    minS = min(val, maxS - 1)
    cv.setTrackbarPos("Min Sat", WINDOW1, minS)


def onMinVTrackbar(val):
    global minV
    global maxV
    minV = min(val, maxV - 1)
    cv.setTrackbarPos("Min Val", WINDOW1, minV)


def onMaxHTrackbar(val):
    global minH
    global maxH
    maxH = max(val, minH + 1)
    cv.setTrackbarPos("Max Hue", WINDOW1, maxH)


def onMaxSTrackbar(val):
    global minS
    global maxS
    maxS = max(val, minS + 1)
    cv.setTrackbarPos("Max Sat", WINDOW1, maxS)


def onMaxVTrackbar(val):
    global minV
    global maxV
    maxV = max(val, minV + 1)
    cv.setTrackbarPos("Max Val", WINDOW1, maxV)



def mapping(maze):
    global lastMove
    global orient
    global currentLoc
    #take object of current cell
    #take orientation of Robot
    #0-West, 1-North, 2-East, 3-South (use these for past movement, current orientation, etc.)
    #save last movement
    fDist = float(tof.forwardSensor()/25.4)
    if fDist < 14 and fDist > 0:
        while fDist < 8.5 or fDist > 9.5:
            fDist = float(tof.forwardSensor()/25.4)
            frontpController(maze,9,0.5,fDist)
            time.sleep(0.1)
    print("New Cell entered... lastMove:", lastMove, "orientation:", orient, "Current cell:", (currentLoc+1))
    cur = maze[currentLoc]
    visitCell(maze)
    print("Cell layout-- west:",cur.west,"North:", cur.north,"East:", cur.east,"South:", cur.south)
    #print("Surrounding Cells--- west
    if currentLoc < 15 and cur.east == 'O':
        if maze[currentLoc+1].visited != True:
            print("Moving Right...")
            moveRight(maze)
            return
    if currentLoc > 3 and cur.north == 'O':
        if maze[currentLoc-4].visited != True:
            print("Moving up...")
            moveUp(maze)
            return
    if currentLoc < 11 and cur.south == 'O':
        if maze[currentLoc+4].visited != True:
            print("Moving down...")
            moveDown(maze)
            return
    if currentLoc > 0 and cur.west == 'O':
        if maze[currentLoc-1].visited != True:
            print("Moving left...")
            moveLeft(maze)
            return
                
    print("no unvisited cells nearby...")
    if cur.east == 'O' and lastMove != 0:
        print("Moving Right...")
        moveRight(maze)
    elif cur.north == 'O' and lastMove != 3:
        print("Moving up...")
        moveUp(maze)
    elif cur.south == 'O' and lastMove != 1:
        print("Moving down...")
        moveDown(maze)
    elif cur.west == 'O' and lastMove != 2:
        print("Moving left...")
        moveLeft(maze)
    else:
    #no movement available... backtrack
        print("No movement available.. backtracking")
        if lastMove == 0:
            moveRight(maze)
        elif lastMove == 3:
            moveUp(maze)
        elif lastMove == 2:
            moveLeft(maze)
        elif lastMove == 1:
            moveDown(maze)
            
def backUp(maze):
    servos.resetCounts()
    wheel_diam = 2.5
        
    #avg_speed= 3/ 2
    #rps_speed= round(float(avg_speed)/(2.5*3.14),2)
    #cnt = 0
    #req = 0
    
    tick_length = (float(wheel_diam) * 3.14)/32
    num_tick = 4 / float(tick_length)
    tick_count = servos.rTick
    print("Ticks needed: ", num_tick)
        
    while(float(tick_count) <= num_tick):
        servos.setSpeedsIPS(-2.0, -2.0)
        time.sleep(0.2)
        tick_count = servos.rTick
			
def moveRight(maze):
    global currentLoc
    currentLoc += 1
    global lastMove
    lastMove = 2;
    while orient != 2:
	#Need to rotate to proper orientation....
        rotate(maze)
    moveForward(maze,17,8)
	#Orientation should be correct when while loop ends, begin movement
    
def moveLeft(maze):
    global currentLoc
    currentLoc -= 1
    global lastMove
    lastMove = 0;
    while orient != 0:
	#Need to rotate to proper orientation....
        rotate(maze)
    moveForward(maze,17,8)
	#Orientation should be correct when while loop ends, begin movement
    
def moveUp(maze):
    global currentLoc
    currentLoc -= 4
    global lastMove
    lastMove = 1;
    while orient != 1:
	#Need to rotate to proper orientation....
        rotate(maze)
    #moving up goes too far... distance is reduced to 16
    moveForward(maze,17,8)
	#Orientation should be correct when while loop ends, begin movement
    
def moveDown(maze):
    global currentLoc
    currentLoc += 4
    global lastMove
    lastMove = 3;
    while orient != 3:
	#Need to rotate to proper orientation....
        rotate(maze)
    moveForward(maze,17,8)
	#Orientation should be correct when while loop ends, begin movement
    
def moveForward(maze,dist,sec_time):
    print("Moving Straight")
    servos.resetCounts()
    wheel_diam = 2.5
        
    avg_speed=float(dist)/float(sec_time)
    rps_speed= round(float(avg_speed)/(2.5*3.14),2)
    cnt = 0
    req=0
        
    #value = servos.interpolate(rps_speed, rps_speed, servos.wheel_calibration)
    #print("Value Interpolated: ",value)
        #cal_time=float(dist)/(float(value[2])*(2.61))
    
    tick_length = (float(wheel_diam) * 3.14)/32
    num_tick = float(dist) / float(tick_length)
    tick_count = servos.rTick
    print("Ticks needed: ", num_tick)
        
    while(float(tick_count) <= num_tick):
        lDist = float(tof.leftDistance()/25.4)
        rDist = float(tof.rightDistance()/25.4)
        fDist = float(tof.forwardSensor()/25.4)
            
        distError = lDist - rDist
            
            #if no walls nearby, just move straight
        if fDist < 4:
            print("Too close to front wall... Back up")
            backUp(maze)
            break
        if lDist > 12 and rDist > 12: 
            servos.setSpeedsIPS(3.5,3.5)
            #else, use Pcontroller
        elif distError < 0:
            #print("Left PControl Sensor Distance: ", lDist)
            leftpControl(maze,7.5,0.4,lDist)
        else:
            #print("Right PControl Sensor Distance: ", rDist)
            rightpControl(maze,7.5,0.4,rDist)
            #print("Tick count: ", tick_count)
            #increased sleep, should help prevent scneario of sensor picking up edges of walls
        time.sleep(0.2)
        tick_count = servos.rTick
        
    tick_count = 0
    servos.stopRobot()
    time.sleep(0.5)

def frontpController(maze, r_t, k_p, y_t):
    # P controller function
    #currTime = time.monotonic()
    #elapsedT = float(self.currTime) - float(self.startTime)
    cf=3.14*2.61
    e_t = float(r_t) - float(y_t)
    u_t = -(float(k_p) * e_t)
    rpsSpd=round((float(u_t))/(float(cf)),2)
    u_rt = servos.fSat(rpsSpd)        
    #print("Distance: ", self.e_t, " elapsed Time: ",self.elapsedT)
    #self.u_rt = self.fSat(self.u_t)
    if abs(float(e_t)) < 0.2:
        #print("inside if----------------------------------->",abs(round(float(self.e_t),0)))
        servos.stopRobot()

    else:
        #print("inside else----------------------------------->")
        servos.setSpeedsRPS(u_rt,u_rt)

def leftpControl(maze,r_t,k_p,y_t):
        # sidepControl controller function
        #self.followFlag = 0
    cf=3.14*2.61
    maxSpeed = 0.5 #RPS 0.6 worked for lab3.. testing different values
    e_t = float(r_t) - float(y_t)
    u_t = float(k_p) * e_t
    rpsSpd=round((float(u_t))/(float(cf)),2)
    u_rt = servos.fSat(rpsSpd)
    n_rt = float(u_rt) + float(maxSpeed)
    runSpeed = servos.fSat(n_rt)
    #print("sidePControl Distance away: " ,(float(y_t)), "e_t: ",e_t, "runSpeed: ", runSpeed)
    if -0.5 <= abs(round(float(e_t),0)) <= 0.5:
        #print("inside if----------------------------------->Moving Forward-- fSensorDist:",fDist,"\nr_t: ",r_t," k_p:",k_p)
        servos.setSpeedsRPS(runSpeed, runSpeed)
    else:
        #print("&&&&&Interpolate speeds PControl u_rt:",u_rt)
            
            #increasing k_p has fixed that. further testing required...
            #if followFlag == 0: **LEFT CONTROLS WORK.. write seperate right side**
        if float(e_t) > 0:
            if float(runSpeed) > maxSpeed:
                servos.setSpeedsRPS(runSpeed, maxSpeed)
            else:
                servos.setSpeedsRPS(maxSpeed, runSpeed)
        if float(e_t) < 0:
                #if abs(float(self.u_rt)) > maxSpeed: **old version.. should use runSpeed instead of u_rt..test incase**
            if float(runSpeed) > maxSpeed:
                servos.setSpeedsRPS(maxSpeed, runSpeed)
            else:
                servos.setSpeedsRPS(runSpeed, maxSpeed)
                    
def rightpControl(maze,r_t,k_p,y_t):
        # sidepControl controller function
        #self.followFlag = flag
    cf=3.14*2.61
    maxSpeed = 0.5 #RPS 0.6 worked for lab3.. testing different values
    minSpeed = 0.4 #RPS 0.25 ~ 2IPS
    e_t = float(r_t) - float(y_t)
    u_t = float(k_p) * e_t
    rpsSpd=round((float(u_t))/(float(cf)),2)
    u_rt = servos.fSat(rpsSpd)
        #self.n_rt = float(self.u_rt) + float(maxSpeed)
    n_rt = float(minSpeed) - float(u_rt)
    runSpeed = servos.fSat(n_rt)
    #print("sidePControl Distance away: " ,(float(y_t)), "e_t: ",e_t, "runSpeed: ", runSpeed)
    if -0.5 <= abs(round(float(e_t),0)) <= 0.5:
        #print("inside if----------------------------------->Moving Forward-- fSensorDist:",fDist,"\nr_t: ",r_t," k_p:",k_p)
        servos.setSpeedsRPS(float(runSpeed), float(runSpeed))
    else:
        #print("&&&&&Interpolate speeds PControl u_rt:",u_rt)                
            #if followFlag == 1:
        if float(e_t) < 0:
            if float(runSpeed) < float(minSpeed):
                servos.setSpeedsRPS(minSpeed, float(runSpeed))
            else:
                servos.setSpeedsRPS(float(runSpeed), minSpeed)
        if float(e_t) > 0:
            if abs(float(u_rt)) < float(minSpeed):
                servos.setSpeedsRPS(float(runSpeed), minSpeed)
            else:
                servos.setSpeedsRPS(minSpeed, float(runSpeed))

def mapGenerator(maze):
    with open('/home/pi/Desktop/Lab_4/mazeMap.csv', 'w', newline='') as csvfile:
        fieldnames = ['Cell', 'west', 'north', 'east', 'south','visit','color']
        csvWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvWriter.writeheader()
        cnt = 0
        for x in maze:
            west = maze[cnt].west
            north = maze[cnt].north
            east = maze[cnt].east
            south = maze[cnt].south
            visit = maze[cnt].visited
            csvWriter.writerow({'Cell':cnt, 'west':west, 'north':north, 'east':east, 'south':south,'visit':visit,'color':0})
            cnt += 1

def mapReader(maze):
    #print("inside csvReader")
    with open('/home/pi/Desktop/Lab_4/mazeMap.csv', mode='r') as csvfile:
        csvReader=csv.DictReader(csvfile)
        cnt = 0
        for row in csvReader:
            x = float(row["Cell"])
            maze[cnt].west = row["west"]
            maze[cnt].north = row["north"]
            maze[cnt].east = row["east"]
            maze[cnt].south = row["south"]
            maze[cnt].visited = row["visit"]
            cnt += 1
            

def visitCell(maze):
    global lastMove
    global orient
    global currentLoc
    cur = maze[currentLoc]
    
    #while orient != 2:
	#facing right... use TOF sensors to check North, East, and SouthWalls
        #rotate(maze) #rotate and check West wall...
    fDist = float(tof.forwardSensor()/25.4)
    rDist = float(tof.rightDistance()/25.4)
    lDist = float(tof.leftDistance()/25.4)
    print("Visiting Cell.. fDist:", fDist, "rDist:", rDist, "lDist:", lDist)
    #starting map... first cell the wall behind should be checked.. based on the assumption we are facing north
    if cur.visited == False:
        if lastMove == 4:
            if lDist < 14:
                cur.west = 'W'
                if currentLoc > 0:
                    maze[currentLoc-1].east = 'W'
            else:
                cur.west = 'O'
                if currentLoc > 0:
                    maze[currentLoc-1].east = 'O'
            if fDist < 14:
                cur.north = 'W'
                if currentLoc > 3:
                    maze[currentLoc - 4].south = 'W'
            else:
                cur.north = 'O'
                if currentLoc > 3:
                    maze[currentLoc - 4].south = 'O'
            if rDist < 14:
                cur.east = 'W'
                if currentLoc < 15:
                    maze[currentLoc + 1].west = 'W'
            else:
                cur.east = 'O'
                if currentLoc < 15:
                    maze[currentLoc + 1].west = 'O'
            rotate(maze)
            #rotate once clockwise, now facing east
            rDist = float(tof.rightDistance()/25.4)
            if rDist < 14:
                cur.south = 'W'
                if currentLoc < 11:
                    maze[currentLoc + 4].north = 'W'
            else:
                cur.south = 'O'
                if currentLoc < 11:
                    maze[currentLoc + 4].north = 'O'
        #check surrounding walls, wall behind has been mapped in last movement, ignore it
        if lastMove == 0: #last move = west/left
            if fDist < 14:
                cur.west = 'W'
                if currentLoc > 0:
                    maze[currentLoc-1].east = 'W'
            else:
                cur.west = 'O'
                if currentLoc > 0:
                    maze[currentLoc-1].east = 'O'
            if rDist < 14:
                cur.north = 'W'
                if currentLoc > 3:
                    maze[currentLoc - 4].south = 'W'
            else:
                cur.north = 'O'
                if currentLoc > 3:
                    maze[currentLoc - 4].south = 'O'
            if lDist < 14:
                cur.south = 'W'
                if currentLoc < 11:
                    maze[currentLoc + 4].north = 'W'
            else:
                cur.south = 'O'
                if currentLoc < 11:
                    maze[currentLoc + 4].north = 'O'
        if lastMove == 1: #last move = north/up
            if lDist < 14:
                cur.west = 'W'
                if currentLoc > 0:
                    maze[currentLoc-1].east = 'W'
            else:
                cur.west = 'O'
                if currentLoc > 0:
                    maze[currentLoc-1].east = 'O'
            if fDist < 14:
                cur.north = 'W'
                if currentLoc > 3:
                    maze[currentLoc - 4].south = 'W'
            else:
                cur.north = 'O'
                if currentLoc > 3:
                    maze[currentLoc - 4].south = 'O'
            if rDist < 14:
                cur.east = 'W'
                if currentLoc < 15:
                    maze[currentLoc + 1].west = 'W'
            else:
                cur.east = 'O'
                if currentLoc < 15:
                    maze[currentLoc + 1].west = 'O'
        if lastMove == 2: #last move = east/right
            if fDist < 14:
                cur.east = 'W'
                if currentLoc < 15:
                    maze[currentLoc+1].west = 'W'
            else:
                cur.east = 'O'
                if currentLoc < 15:
                    maze[currentLoc+1].west = 'O'
            if lDist < 14:
                cur.north = 'W'
                if currentLoc > 3:
                    maze[currentLoc - 4].south = 'W'
            else:
                cur.north = 'O'
                if currentLoc > 3:
                    maze[currentLoc - 4].south = 'O'
            if rDist < 14:
                cur.south = 'W'
                if currentLoc < 11:
                    maze[currentLoc + 4].north = 'W'
            else:
                cur.south = 'O'
                if currentLoc < 11:
                    maze[currentLoc + 4].north = 'O'
        if lastMove == 3: #last move = south/down
            if rDist < 14:
                cur.west = 'W'
                if currentLoc > 0:
                    maze[currentLoc-1].east = 'W'
            else:
                cur.west = 'O'
                if currentLoc > 0:
                    maze[currentLoc-1].east = 'O'
            if lDist < 14:
                cur.east = 'W'
                if currentLoc < 15:
                    maze[currentLoc + 1].west = 'W'
            else:
                cur.east = 'O'
                if currentLoc < 15:
                    maze[currentLoc + 1].west = 'O'
            if fDist < 14:
                cur.south = 'W'
                if currentLoc < 11:
                    maze[currentLoc + 4].north = 'W'
            else:
                cur.south = 'O'
                if currentLoc < 11:
                    maze[currentLoc + 4].north = 'O'
        cur.visited = True
    print("Cell mapped... check for color if applicable")
    #once we check for the presence of walls... we need to check for colored walls (if outside wall)
    #there are 4 cells inside and 12 outside.. check if not inside
    
    #if currentLoc != 5 and currentLoc != 6 and currentLoc != 9 and currentLoc != 10:
    if currentLoc > 15: #set to an impossible condition to ignore for now, proper if is above
        print("Color checking started..")
        if currentLoc == 0:
	    #check North & west wall for color
            while orient != 0:
                rotate(maze)
            checkColor(maze)
            while orient != 1:
                rotate(maze)
            checkColor(maze)
			
        if currentLoc == 1 or currentLoc == 2:
	    #check North wall
            while orient != 1:
                rotate(maze)
            checkColor(maze)
			
            if currentLoc == 3:
		#check north & east wall
                while orient != 1:
                    rotate(maze)
                checkColor(maze)
                while orient != 2:
                    rotate(maze)
                checkColor(maze)
			
            if currentLoc == 4 or currentLoc == 8:
		    #check west wall
                while orient != 0:
                    rotate(maze)
                checkColor(maze)
			
            if currentLoc == 7 or currentLoc == 11:
			#check East wall
                while orient != 2:
                    rotate(maze)
                checkColor(maze)
			
            if currentLoc == 12:
			#check West & south wall
                while orient != 3:
                    rotate(maze)
                checkColor(maze)
                while orient != 0:
                    rotate(maze)
                checkColor(maze)
			
            if currentLoc == 15:
			#check south & East wall
                while orient != 2:
                    rotate(maze)
                checkColor(maze)
                while orient != 3:
                    rotate(maze)
                checkColor(maze)
            if currentLoc == 13 or currentLoc == 14:
                #check south wall
                while orient != 3:
                    rotate(maze)
                checkColor(maze)
    #center(maze)
    printMaze(maze)
    localization(maze)
    
    
def localization(maze):
    global orient
    global currentLoc
    if orient == 0:
        orientation = "West"
    elif orient == 1:
        orientation = "North"
    elif orient == 2:
        orientation = "East"
    elif orient == 3:
        orientation = "South"
    
    if currentLoc < 15:
        if maze[currentLoc+1].visited == True:
            east = True
        else:
            east = False
    else:
        east = "Border"
    if currentLoc > 3:
        if maze[currentLoc-4].visited == True:
            north = True
        else:
            north = False
    else:
        north = "Border"

    if currentLoc < 11:
        if maze[currentLoc+4].visited == True:
            south = True
        else:
            south = False
    else:
        south = "Border"

    if currentLoc > 0:
        if maze[currentLoc-1].visited == True:
            west = True
        else:
            west = False
    else:
        west = "Border"
    
    print("Current Cell: ", (currentLoc+1), "\tOrientation: ", orientation)
    print("Surrounding Cells Visited? West: ", west, "North: ", north, "East: ", east, "South: ", south)
    print("*********************************CELLS VISITED*********************************")
    print ("'X' - visited \t '-' = unvisited")
    loc = 0
    for i in range(4):
        for j in range(4):
            if maze[loc].visited == True:
                print("X", end = "")
            else:
                print("-", end = "")
            loc += 1
        print(" ")
            
def turnAround(maze):
    print("Turning Around")
    servos.resetCounts()
    
    global orient
    orient += 2
    orient = orient % 4

    wheel_diam = 2.5
    dist = 3.14 * 2
    cnt = 0
    tick_length = (float(wheel_diam)*3.14)/32
    num_tick = float(dist) / float(tick_length)
    tick_count = servos.rTick
        
    while(float(tick_count) <= num_tick):
        servos.setSpeedRPS(1.45, 1.45)
        time.sleep(0.1)
        tick_count = servos.rTick
    servos.setSpeedRPS(1.5,1.5)
    
def rotate(maze):
    global orient
    servos.resetCounts()
    print("Rotating Right, current orientation:" , orient)
    orient += 1;
    orient = orient %4;
    wheel_diam = 2.5
    dist = 3.14
    cnt = 0
    tick_length = (float(wheel_diam)*3.14)/32
    num_tick = float(dist) / float(tick_length)
    tick_count = servos.rTick
        
    while(float(tick_count) <= num_tick):
        servos.setSpeedsRPS(0.4, -0.4)
        time.sleep(0.1)
        tick_count = servos.rTick
        #print("TIck count:", tick_count)
    time.sleep(0.1)
    servos.setSpeedRPS(1.5,1.5)
    
def center(maze):
    #center the robot, if a wall is present on a side, turn to face it and use the front p controller to position ~9in
    print("Begin centering..")
    global orient
    global currentLoc
    cur = maze[currentLoc]
    fDist = float(tof.forwardSensor()/25.4)
    if cur.west == 'W':
        print("Center west wall")
        while orient != 0:
            rotate(maze)
        while fDist < 8.5 or fDist > 9.5:
            fDist = float(tof.forwardSensor()/25.4)
            frontpController(maze,9,0.5,fDist)
            time.sleep(0.1)
        servos.stopRobot
        #use front p control to position ~9in from wall
    if cur.north == 'W':
        print("center north wall")
        while orient != 1:
            rotate(maze)
        while fDist < 8.5 or fDist > 9.5:
            fDist = float(tof.forwardSensor()/25.4)
            frontpController(maze,9,0.5,fDist)
            time.sleep(0.1)
        servos.stopRobot
        #front p control
    if cur.east == 'W':
        print("center east wall")
        while orient != 2:
            rotate(maze)
        while fDist < 8.5 or fDist > 9.5:
            fDist = float(tof.forwardSensor()/25.4)
            frontpController(maze,9,0.5,fDist)
            time.sleep(0.1)
        servos.stopRobot
        #front p control
    if cur.south == 'W':
        print("center south wall")
        while orient != 3:
            rotate(maze)
        while fDist < 8.5 or fDist > 9.5:
            fDist = float(tof.forwardSensor()/25.4)
            frontpController(maze,9,0.5,fDist)
            time.sleep(0.1)
        servos.stopRobot
        #front p control

	
def checkColor(maze):
	#check the wall being faced for color... set mask, check for blobs, save & return if found, try other masks if not
	#0 - Blue, 1 - Green, 2 - Yellow, 3 - Red (can be changed as needed)
	print("WORK IN PROGRESS")
	#mask = blue;
	#check for blobs.. camera should already be on... use if statement below?
	#if size(keypoints) > 0:
		#save color value
		#cur.color = 0;
		
def allVisit(maze):
    for i in range(16):
        if maze[i].visited == False:
            return False
    return True
	
#creating object of wall Distance class
#wallDist=wallDistance()
servos=servos()
tof=tof()
GPIO.add_event_detect(servos.LENCODER, GPIO.RISING, servos.onLeftEncode)
GPIO.add_event_detect(servos.RENCODER, GPIO.RISING, servos.onRightEncode)
servos.csvReader()


# Initialize the threaded camera
# You can run the unthreaded camera instead by changing the line below.
# Look for any differences in frame rate and latency.
camera = ThreadedWebcam()  # UnthreadedWebcam()
camera.start()

# Initialize the SimpleBlobDetector
params = cv.SimpleBlobDetector_Params()
detector = cv.SimpleBlobDetector_create(params)

# Attempt to open a SimpleBlobDetector parameters file if it exists,
# Otherwise, one will be generated.
# These values WILL need to be adjusted for accurate and fast blob detection.
fs = cv.FileStorage("params.yaml", cv.FILE_STORAGE_READ);  # yaml, xml, or json
if fs.isOpened():
    detector.read(fs.root())
else:
    print("WARNING: params file not found! Creating default file.")

    fs2 = cv.FileStorage("params.yaml", cv.FILE_STORAGE_WRITE)
    detector.write(fs2)
    fs2.release()

fs.release()

# Create windows
cv.namedWindow(WINDOW1)
cv.namedWindow(WINDOW2)

# Create trackbars
cv.createTrackbar("Min Hue", WINDOW1, minH, 180, onMinHTrackbar)
cv.createTrackbar("Max Hue", WINDOW1, maxH, 180, onMaxHTrackbar)
cv.createTrackbar("Min Sat", WINDOW1, minS, 255, onMinSTrackbar)
cv.createTrackbar("Max Sat", WINDOW1, maxS, 255, onMaxSTrackbar)
cv.createTrackbar("Min Val", WINDOW1, minV, 255, onMinVTrackbar)
cv.createTrackbar("Max Val", WINDOW1, maxV, 255, onMaxVTrackbar)

fps, prev = 0.0, 0.0

lastMove = 4
orient = 1
currentLoc = 0
cellCount = 0

now = time.time()
fps = (fps * FPS_SMOOTHING + (1 / (now - prev)) * (1.0 - FPS_SMOOTHING))
prev = now

# Get a frame
frame = camera.read()

# Blob detection works better in the HSV color space
# (than the RGB color space) so the frame is converted to HSV.
#frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

# Create a mask using the given HSV range
#mask = cv.inRange(frame_hsv, (minH, minS, minV), (maxH, maxS, maxV))

# Run the SimpleBlobDetector on the mask.
# The results are stored in a vector of 'KeyPoint' objects,
# which describe the location and size of the blobs.
#keypoints = detector.detect(mask)

# For each detected blob, draw a circle on the frame
#frame_with_keypoints = cv.drawKeypoints(frame, keypoints, None, color=(0, 255, 0),flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# Write text onto the frame
#cv.putText(frame_with_keypoints, "FPS: {:.1f}".format(fps), (5, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
#cv.putText(frame_with_keypoints, "{} blobs".format(len(keypoints)), (5, 35), cv.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0))

    # Display the frame
    #cv.imshow(WINDOW1, mask)
    #cv.imshow(WINDOW2, frame_with_keypoints)

    #if len(keypoints)>0:
        #print(keypoints[0].pt[0],"   ",keypoints[0].pt[1],"   ",keypoints[0].size);
        #print("keypoints: ",len(keypoints))
        #dist=float(wallDist.forwardSensor())/25.4
        #if dist<4 or dist>6:
            #if float(keypoints[0].pt[0]) > 380:
                #wallDist.setSpeedRPS(1.55, 1.5)
            #elif float(keypoints[0].pt[0]) < 260:
                #wallDist.setSpeedRPS(1.5, 1.45)
            #wallDist.towardsWall(5,0.6)
        #else:
            #wallDist.setSpeedRPS(1.5, 1.5)  
            #time.sleep(1)
        #time.sleep(0.02)
    #else:
       # print("keypoints are less than or equal to zero: ", len(keypoints))
        #wallDist.setSpeedRPS(1.53, 1.5)
        #time.sleep(0.5)



    # Check for user input
    
def mappingStart(maze):
    global orient
    global currentLoc
    global lastMove
    global cellCount
    print("Do you want to load the saved Map? 'Y' or 'N'")
    choice = input()
    if choice == 'y' or choice == 'Y':
        mapReader(maze)
        printMaze(maze)
    elif(allVisit(maze) != True):
        print("Please place me in any cell, facing North.")
        while int(currentLoc) > 16 or int(currentLoc) < 1:
            print("Which cell am I located in?")
            currentLoc = input()
            if int(currentLoc) > 16 or int(currentLoc) < 1:
                print("Invalid Location, cells are nubered 1 - 16. Please try again")
        currentLoc = int(currentLoc) - 1

        printMaze(maze)
        while allVisit(maze) != True:
            global cellCount
            print("All cells visited? ", allVisit(maze))
            mapping(maze)
        
            if cellCount == 3:
                lastOrient = orient
                center(maze)
                cellCount = 0
                while orient != lastOrient:
                    rotate(maze)
            else:
                cellCount += 1
            c = cv.waitKey(1)
            if c == 27 or c == ord('q') or c == ord('Q'):  # Esc or Q
                camera.stop()
                break
            
        print("Mapping Complete!!")
    printMaze(maze)
    mapGenerator(maze)
    camera.stop()
