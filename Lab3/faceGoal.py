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

import cv2 as cv
import time
from ThreadedWebcam import ThreadedWebcam


class faceGoal(ThreadedWebcam):

    # To do initialization
    def __init__(self):
        super().__init__()
        self.FPS_SMOOTHING = 0.9

        # Window names
        self.WINDOW1 = "Adjustable Mask - Press Esc to quit"
        self.WINDOW2 = "Detected Blobs - Press Esc to quit"

        # Default HSV ranges
        # Note: the range for hue is 0-180, not 0-255
        self.minH = 0; self.minS = 127; self.minV = 0;
        self.maxH = 180; self.maxS = 255; self.maxV = 255;

        # Initialize the threaded camera
        # You can run the unthreaded camera instead by changing the line below.
        # Look for any differences in frame rate and latency.
        self.camera = ThreadedWebcam() # UnthreadedWebcam()
        self.camera.start()

        # Initialize the SimpleBlobDetector
        self.params = cv.SimpleBlobDetector_Params()
        self.detector = cv.SimpleBlobDetector_create(self.params)


    # These functions are called when the user moves a trackbar
    def onMinHTrackbar(self,val):
        # Calculate a valid minimum red value and re-set the trackbar.

        self.minH = min(val, self.maxH - 1)
        cv.setTrackbarPos("Min Hue", self.WINDOW1, self.minH)

    def onMinSTrackbar(self,val):

        self.minS = min(val, self.maxS - 1)
        cv.setTrackbarPos("Min Sat", self.WINDOW1, self.minS)

    def onMinVTrackbar(self,val):

        self.minV = min(val, self.maxV - 1)
        cv.setTrackbarPos("Min Val", self.WINDOW1, self.minV)

    def onMaxHTrackbar(self,val):

        self.maxH = max(val, self.minH + 1)
        cv.setTrackbarPos("Max Hue", self.WINDOW1, self.maxH)

    def onMaxSTrackbar(self,val):

        self.maxS = max(val, self.minS + 1)
        cv.setTrackbarPos("Max Sat", self.WINDOW1, self.maxS)

    def onMaxVTrackbar(self,val):

        self.maxV = max(val, self.minV + 1)
        cv.setTrackbarPos("Max Val", self.WINDOW1, self.maxV)


    def  blobDetect(self):
        print("***inside Blob Detect***")
        # Attempt to open a SimpleBlobDetector parameters file if it exists,
        # Otherwise, one will be generated.
        # These values WILL need to be adjusted for accurate and fast blob detection.
        fs = cv.FileStorage("params.yaml", cv.FILE_STORAGE_READ); #yaml, xml, or json
        if fs.isOpened():
            self.detector.read(fs.root())
        else:
            print("WARNING: params file not found! Creating default file.")

            fs2 = cv.FileStorage("params.yaml", cv.FILE_STORAGE_WRITE)
            self.detector.write(fs2)
            fs2.release()

        fs.release()

        # Create windows
        cv.namedWindow(self.WINDOW1)
        cv.namedWindow(self.WINDOW2)

        # Create trackbars
        cv.createTrackbar("Min Hue", self.WINDOW1, self.minH, 180, self.onMinHTrackbar)
        cv.createTrackbar("Max Hue", self.WINDOW1, self.maxH, 180, self.onMaxHTrackbar)
        cv.createTrackbar("Min Sat", self.WINDOW1, self.minS, 255, self.onMinSTrackbar)
        cv.createTrackbar("Max Sat", self.WINDOW1, self.maxS, 255, self.onMaxSTrackbar)
        cv.createTrackbar("Min Val", self.WINDOW1, self.minV, 255, self.onMinVTrackbar)
        cv.createTrackbar("Max Val", self.WINDOW1, self.maxV, 255, self.onMaxVTrackbar)

        fps, prev = 0.0, 0.0
        while True:
            # Calculate FPS
            now = time.time()
            print(now,"  ",prev);
            fps = (fps*self.FPS_SMOOTHING + (1/(now - prev))*(1.0 - self.FPS_SMOOTHING))
            prev = now
            print("fps:",fps)
            # Get a frame
            frame = self.camera.read()

            # Blob detection works better in the HSV color space
            # (than the RGB color space) so the frame is converted to HSV.
            frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

            # Create a mask using the given HSV range
            mask = cv.inRange(frame_hsv, (self.minH, self.minS, self.minV), (self.maxH, self.maxS, self.maxV))

            # Run the SimpleBlobDetector on the mask.
            # The results are stored in a vector of 'KeyPoint' objects,
            # which describe the location and size of the blobs.
            keypoints = self.detector.detect(mask)

            # For each detected blob, draw a circle on the frame
            frame_with_keypoints = cv.drawKeypoints(frame, keypoints, None, color = (0, 255, 0), flags = cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

            # Write text onto the frame
            cv.putText(frame_with_keypoints, "FPS: {:.1f}".format(fps), (5, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
            cv.putText(frame_with_keypoints, "{} blobs".format(len(keypoints)), (5, 35), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))

            # Display the frame
            cv.imshow(self.WINDOW1, mask)
            #cv.imshow(self.WINDOW2, frame_with_keypoints)

            # Check for user input
            c = cv.waitKey(1)
            if c == 27 or c == ord('q') or c == ord('Q'): # Esc or Q
                self.camera.stop()
                break

        self.camera.stop()

obj=faceGoal()
obj.blobDetect()
