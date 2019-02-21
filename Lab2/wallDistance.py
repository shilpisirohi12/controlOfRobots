#wallDistance.py - *move robot to w/in 5inches of the wall using a P controlller*
from servos import servos
from tof import tof
include time
include servos
#inlcude tof

def pControl:
	#P controller function
	e_t = u_t = y_t = u_rt = 0
	r_t = 5
	k_p = 0.6 #change based on test variable
	
	#this loop should run infinitely.. should move back to 5in from wall without having
	#to restart if the robot is moved
	while true:
		y_t = fSensor.getDistance()
		#convert to inches (given in mm) or convert r_t to mm
		e_t = r_t - y_t
		
		if e_t == 0: #might need a small range since sensors aren't 100% accurate..
			#setPWM to 1.5 STOP condition at expected distance
			#stay w/in infinite loop to check if robot is moved
		u_t = k_p * e_t
		u_rt = fSat(u_t)
		
		getSpeedIPS(u_rt, u_rt)
		
		#setPWM using return vals from getSpeed
	
		time.sleep(1) #might need to be half second or faster...
		
def fSat(velSig):
	#Saturation function, if the desired speed is too great, set to max speed

	#IPS speeds in .csv file has been changed to have a +/- value
	#min/max function (in servos) will have to be changed to find the largest +/- value
	if velSig > maxSpeed:
		return velSig = maxSpeed
	elif velSig < minSpeed:
		return velSig = minSpeed
	else:
		return velSig