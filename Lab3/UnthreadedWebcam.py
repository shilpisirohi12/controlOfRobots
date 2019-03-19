# This is a modified version of the ThreadedWebcam class which removes threading.

import cv2 as cv

class UnthreadedWebcam:
	def __init__(self, src=0, name="ThreadedWebcam"):
		self.stream = cv.VideoCapture(src)
		self.stream.set(cv.CAP_PROP_FRAME_WIDTH, 640)
		self.stream.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
		#self.stream.set(cv.CAP_PROP_BUFFERSIZE, 1)
		
		if not self.stream.isOpened():
			print("Failed to open camera!")
			exit()
		else:
			print("Unthreaded webcam started.")
			
	def start(self):
		# The pass statement is a "do nothing" statement.
		pass
		
	def read(self):
		(self.grabbed, self.frame) = self.stream.read()
		return self.frame
	
	def stop(self):
		pass

