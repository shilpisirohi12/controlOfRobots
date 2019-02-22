#wallDistance.py - *move robot to w/in 5inches of the wall using a P controlller*
from servos import servos
from tof import tof
include time
from servos import servos
from tof import tof

class wallDistance:
	def __init__(self):
		super().__init__()
		e_t = u_t = y_t = u_rt = 0
		k_p = 0.6 #change based on test variable

	def pControl(self,y_t,k_p,r_t):
		#P controller function
		e_t = r_t - y_t
		u_t = k_p * e_t
		u_rt = self.fSat(u_t)
		if e_t == 0:
			self.stopRobot()
			#might need a small range since sensors aren't 100% accurate..
			#setPWM to 1.5 STOP condition at expected distance
			#stay w/in infinite loop to check if robot is move
		else:
			self.setSpeedIPS(u_rt, u_rt)# setting the speed on the Servos
			time.sleep(1) #might need to be half second or faster...

	def fSat(self,velSig):
		#Saturation function, if the desired speed is too great, set to max speed
		#IPS speeds in .csv file has been changed to have a +/- value
		#min/max function (in servos) will have to be changed to find the largest +/- value
		if velSig > self.maxSpeed:
			return self.maxSpeed
		elif velSig < self.minSpeed:
			return self.minSpeed
		else:
			return velSig

	def towardsWall(self,desired_dist,p):
		while True:
			print("Walking towards Wall")
			self.pControl(desired_dist,p,self.fSensor.getDistance())



	def executeWallDist(self):
		print("Please provide 𝑑𝑒𝑠𝑖𝑟𝑒𝑑 𝑑𝑖𝑠𝑡𝑎𝑛𝑐𝑒 𝑡𝑜 𝑡ℎ𝑒 𝑔𝑜𝑎𝑙: ", end="")
		desired_dist = input()
		print("Please provide 𝑝𝑟𝑜𝑝𝑜𝑟𝑡𝑖𝑜𝑛𝑎𝑙 𝑔𝑎𝑖𝑛 𝑜𝑟 𝑐𝑜𝑟𝑟𝑒𝑐𝑡𝑖𝑜𝑛 𝑒𝑟𝑟𝑜𝑟 𝑔𝑎𝑖𝑛: ", end="")
		p = input()
		self.towardsWall(desired_dist,p)




