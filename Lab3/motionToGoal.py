# This program demonstrates advanced usage of the OpenCV library by
# using the SimpleBlobDetector feature along with camera threading.
# The program displays two windows: one for adjusting the mask,
# and one that displays the detected blobs in the (masked) image.
# Adjust the HSV values until blobs are detected from the camera feed.
# There's also a params file in the same folder that can be adjusted.

# Helpful links:
# https://www.learnopencv.com/blob-detection-using-opencv-python-c/
# https://docs.opencv.org/3.4.1/da/d97/tutorial_threshold_inRange.html
# https://docs.opencv.org/3.4.1/d0/d7a/classcv_1_1SimpleBlobDetector.html
# https://docs.opencv.org/3.4.1/d2/d29/classcv_1_1KeyPoint.html
# https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/
import csv
import cv2 as cv
import time
import Adafruit_PCA9685
import signal
import math
import sys
sys.path.append('/home/pi/VL53L0X_rasp_python/python')
import VL53L0X
import RPi.GPIO as GPIO

from ThreadedWebcam import ThreadedWebcam
from UnthreadedWebcam import UnthreadedWebcam

# The servo hat uses its own numbering scheme within the Adafruit library.
# 0 represents the first servo, 1 for the second, and so on.
LSERVO = 0
RSERVO = 1

LSHDN = 27
FSHDN = 22
RSHDN = 23

DEFAULTADDR = 0x29  # All sensors use this address by default, don't change this
LADDR = 0x2a
RADDR = 0x2b

print("Set the pin numbering scheme to the numbering shown on the robot itself.")
GPIO.setmode(GPIO.BCM)

print("Setup pins")
GPIO.setup(LSHDN, GPIO.OUT)
GPIO.setup(FSHDN, GPIO.OUT)
GPIO.setup(RSHDN, GPIO.OUT)

print("Shutdown all sensors")
GPIO.output(LSHDN, GPIO.LOW)
GPIO.output(FSHDN, GPIO.LOW)
GPIO.output(RSHDN, GPIO.LOW)

time.sleep(0.01)

print("Initialize all sensors")
lSensor = VL53L0X.VL53L0X(address=LADDR)
fSensor = VL53L0X.VL53L0X(address=DEFAULTADDR)
rSensor = VL53L0X.VL53L0X(address=RADDR)
# print("lSensor:" ,self.lSensor )

# to increase the timing budget to a more accurate but slower 200ms value
lSensor.measurement_timing_budget = 200000
fSensor.measurement_timing_budget = 200000
rSensor.measurement_timing_budget = 200000

# Connect the front sensor and start measurement
GPIO.output(FSHDN, GPIO.HIGH)
time.sleep(0.01)
fSensor.start_ranging(VL53L0X.VL53L0X_GOOD_ACCURACY_MODE)

e_t = u_t = y_t = u_rt = 0
sleep_interval = 0.05
isMax=-1

# This function is called when Ctrl+C is pressed.
# It's intended for properly exiting the program.
def ctrlC(signum, frame):
    print("Exiting")
    # Stop the servos
    pwm.set_pwm(LSERVO, 0, 0)
    pwm.set_pwm(RSERVO, 0, 0)

    # Stop measurement for all sensors
    fSensor.stop_ranging()

    # Stop the camera
    camera.stop()
    exit()


# Attach the Ctrl+C signal interrupt
signal.signal(signal.SIGINT, ctrlC)

# Initialize the servo hat library.
pwm = Adafruit_PCA9685.PCA9685()

# 50Hz is used for the frequency of the servos.
pwm.set_pwm_freq(50)

# Write an initial value of 1.5, which keeps the servos stopped.
# Due to how servos work, and the design of the Adafruit library,
# the value must be divided by 20 and multiplied by 4096.
pwm.set_pwm(LSERVO, 0, math.floor(1.5 / 20 * 4096));
pwm.set_pwm(RSERVO, 0, math.floor(1.5 / 20 * 4096));

FPS_SMOOTHING = 0.9

# Window names
WINDOW1 = "Adjustable Mask - Press Esc to quit"
WINDOW2 = "Detected Blobs - Press Esc to quit"

# Default HSV ranges
# Note: the range for hue is 0-180, not 0-255

minH = 28; minS = 169; minV = 51;
maxH = 180; maxS = 255; maxV = 255;
maxLeft=0;minLeft=0;maxRight=0;minRight=0;

startTime = time.monotonic()

def csvReader():
    # print("inside csvReader")
    arrLeft = []
    arrSpeedLeft = []
    arrSpeedRight = []
    lSpeed = []
    rSpeed = []
    global maxLeft
    global minLeft
    global maxRight
    global minRight
    with open('/home/pi/assignments/git/controlOfRobots/Lab2/calibrations.csv', mode='r') as csvfile:
        csvReader = csv.DictReader(csvfile)
        for row in csvReader:
            arrLeft.append(row["PWM"])
            arrSpeedLeft.append(row["RPS_Left"])
            arrSpeedRight.append(row["RPS_Right"])
            lSpeed.append(row["RPS_Left"])
            rSpeed.append(row["RPS_Right"])

        cnt = 0
        global wheel_calibration
        wheel_calibration= []
        for l in range(len(arrLeft)):
            sublist = []
            sublist.append(arrLeft[cnt])
            sublist.append(arrSpeedLeft[cnt])
            sublist.append(arrSpeedRight[cnt])
            cnt = cnt + 1
            wheel_calibration.append(sublist)

        cnt=0
        for x in lSpeed:
            #Initializing the values
            if cnt ==0:
                maxLeft = minLeft =x
            if float(maxLeft)< float(x):
                maxLeft = x
            if float(minLeft) > float(x):
                minLeft = x
            cnt=cnt+1
        cnt=0
        for x in rSpeed:
            #Initializing the values
            if cnt ==0:
                maxRight=x
            if float(maxRight)< float(x):
                maxRight = x
            if float(minRight) > float(x):
                minRight = x
            cnt=cnt+1
    print("minLeft: ",minLeft," maxLeft: ",maxLeft," minRight: ",minRight, " maxRight: ",maxRight)


def stopRobot(self):
        self.pwm.set_pwm(self.LSERVO, 0, math.floor(float(1.5) / 20 * 4096))
        self.pwm.set_pwm(self.RSERVO, 0, math.floor(float(1.5) / 20 * 4096))

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

def fSat(velSig):
    # Saturation function, if the desired speed is too great, set to max speed
    lowestRPS = min(float(maxRight), float(maxLeft), abs(float(minRight)), abs(float(minLeft)))
    if abs(float(velSig)) > float(lowestRPS):
        #print("inside max ifs ",lowestRPS)
        global isMax
        isMax=1
        return lowestRPS
    else:
        global isMax
        isMax==0
        return float(velSig)

def lin_interpolate(rpsL, rpsR, data_lst):

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

    if pwmL == 0 and (maxL - minL) != 0:
        # print("interpolate Left:", pwm_minL, pwm_maxL, minL, maxL, spdL)
        pwmL = (((pwm_minL * (maxL - spdL)) + (pwm_maxL * (spdL - minL))) / (maxL - minL))

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

    if pwmR == 0 and (maxL - minL) != 0:
        # print("Interpolate Right: ", pwm_minR, pwm_maxR, minR, maxR, spdR)
        pwmR = (pwm_minR * (maxR - spdR) + pwm_maxR * (spdR - minR)) / (maxR - minR)

    return (pwmL, pwmR)

def setSpeedsRPS(rpsLeft, rpsRight):
    value = lin_interpolate(rpsLeft,rpsRight,wheel_calibration)
    pwm.set_pwm(LSERVO, 0, math.floor(float(value[0]) / 20 * 4096))
    pwm.set_pwm(RSERVO, 0, math.floor(float(value[1]) / 20 * 4096))

def pControl(r_t, k_p):
    # P controller function
    currTime = time.monotonic()
    elapsedT = float(currTime) - float(startTime)
    e_t = float(r_t) - float(y_t)
    u_t = -(float(k_p) * e_t)
    rpsSpd=round((float(u_t))/(float(3.14*2.61)),2)
    u_rt = fSat(rpsSpd)
    #print("Distance: ", self.e_t, " elapsed Time: ",self.elapsedT)
    #self.u_rt = self.fSat(self.u_t)
    if abs(float(e_t)) < 0.2:
        print("inside if----------------------------------->",abs(round(float(e_t),0)))
        stopRobot()

    else:
        print("inside else----------------------------------->")
        setSpeedsRPS(u_rt,u_rt)

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
while True:
    # Calculate FPS
    now = time.time()
    fps = (fps * FPS_SMOOTHING + (1 / (now - prev)) * (1.0 - FPS_SMOOTHING))
    prev = now

    # Get a frame
    frame = camera.read()

    # Blob detection works better in the HSV color space
    # (than the RGB color space) so the frame is converted to HSV.
    frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # Create a mask using the given HSV range
    mask = cv.inRange(frame_hsv, (minH, minS, minV), (maxH, maxS, maxV))

    # Run the SimpleBlobDetector on the mask.
    # The results are stored in a vector of 'KeyPoint' objects,
    # which describe the location and size of the blobs.
    keypoints = detector.detect(mask)

    # For each detected blob, draw a circle on the frame
    frame_with_keypoints = cv.drawKeypoints(frame, keypoints, None, color=(0, 255, 0),
                                            flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # Write text onto the frame
    cv.putText(frame_with_keypoints, "FPS: {:.1f}".format(fps), (5, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
    cv.putText(frame_with_keypoints, "{} blobs".format(len(keypoints)), (5, 35), cv.FONT_HERSHEY_SIMPLEX, 0.5,
               (0, 255, 0))

    # Display the frame
    # cv.imshow(WINDOW1, mask)
    cv.imshow(WINDOW2, frame_with_keypoints)

    if len(keypoints) > 0:
        print("keypoints: ", len(keypoints))
        # print("Walking towards Wall---",self.forwardSensor())
        global y_t
        while True:
            y_t = float(fSensor.get_distance()) / 25.4
            # print("y_t: ",self.forwardSensor(),"  float(self.y_t)/25.4:",float(self.y_t));
            if float(y_t) > 45:
                print("******WARNING: EXCEEDING THE SENSOR's RANGE********")
            pControl(5, 0.6)
            time.sleep(0.05)
    else:
        print("keypoints are less than or equal to zero: ", len(keypoints))
        pwm.set_pwm(LSERVO, 0, math.floor(1.6 / 20 * 4096))
        pwm.set_pwm(RSERVO, 0, math.floor(1.5 / 20 * 4096))
        time.sleep(1)

    # Check for user input
    c = cv.waitKey(1)
    if c == 27 or c == ord('q') or c == ord('Q'):  # Esc or Q
        camera.stop()
        break

camera.stop()
