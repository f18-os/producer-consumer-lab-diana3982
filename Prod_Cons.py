import cv2
import numpy as np
import base64
import os
from threading import Thread, Condition
import time
import random
from Queue import Queue

extractionQueue = Queue(10)
displayQueue = Queue(10)
#condition = Condition()

fileName = 'clip.mp4'

class ExtractThread(Thread):
    def run(self):
        global extractionQueue
        global fileName

        while True:
            #condition.acquire()

            # Initialize frame count
            count = 0

            # open video file
            vidcap = cv2.VideoCapture(fileName)

            # read first image
            success,image = vidcap.read()

            print("Reading frame {} {} ".format(count, success))

            while success:

                # get a jpg encoded frame
                success, jpgImage = cv2.imencode('.jpg', image)

                #encode the frame as base 64 to make debugging easier
                jpgAsText = base64.b64encode(jpgImage)

                # add the frame to the buffer
                extractionQueue.put(jpgAsText)

                success,image = vidcap.read()
                print('Reading frame {} {}'.format(count, success))

                count += 1
                time.sleep(random.random())



            print("Frame extraction complete")

class GrayscaleThread(Thread):
    def run(self):
        global extractionQueue
        global displayQueue
        global fileName

        while True:
            #condition.acquire()
            num = 0

            if extractionQueue:

                print("Converting frame {}".format(num))

                # get the next frame
                frameAsText = extractionQueue.get()

                # decode the frame
                jpgRawImage = base64.b64decode(frameAsText)

                # convert the raw frame to a numpy array
                jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

                # get a jpg encoded frame
                img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

                #print(img)

                # convert the extracted frame to grayscale
                grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                extractionQueue.task_done()
                displayQueue.put(grayscaleFrame)


                #condition.notify()
                #condition.release()
                time.sleep(random.random())

class DisplayThread(Thread):
    def run(self):
        global displayQueue
        global fileName

        while True:
            #condition.acquire()

            # initialize frame count
            count = 0
            while displayQueue:
                # get the next frame
                frameAsText = displayQueue.get()

                # decode the frame
                jpgRawImage = base64.b64decode(frameAsText)

                # convert the raw frame to a numpy array
                jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

                # get a jpg encoded frame
                img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

                print("Displaying frame {}".format(count))

                # display the image in a window called "video" and wait 42ms
                # before displaying the next frame
                cv2.imshow("Video", img)
                if cv2.waitKey(42) and 0xFF == ord("q"):
                    break

                #condition.notify()
                #condition.release()
                displayQueue.task_done()
                time.sleep(random.random())
                count += 1



        #print("Finished displaying all frames")
        # cleanup the windows
        cv2.destroyAllWindows()

ExtractThread().start()
GrayscaleThread().start()
DisplayThread().start()
