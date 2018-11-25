import cv2
import numpy as np
import base64
import os
from threading import Thread
import time
import random
from Queue import Queue

extractionQueue = Queue(10)
fileName = 'clip.mp4'

class ProducerThread(Thread):
    def run(self):
        global extractionQueue
        global fileName

        while True:
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

            print("Frame extraction complete")
            time.sleep(random.random())


class ConsumerThread(Thread):
    def run(self):
        global extractionQueue
        global fileName

        while True:
            # initialize frame count
            num = 0

            # go through each frame in the buffer until the buffer is empty
            while not extractionQueue.empty():
                # get the next frame
                frameAsText = extractionQueue.get()

                # decode the frame
                jpgRawImage = base64.b64decode(frameAsText)

                # convert the raw frame to a numpy array
                jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

                # get a jpg encoded frame
                img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

                print("Displaying frame {}".format(num))

                # display the image in a window called "video" and wait 42ms
                # before displaying the next frame
                cv2.imshow("Video", img)
                if cv2.waitKey(42) and 0xFF == ord("q"):
                    break

                num += 1

            print("Finished displaying all frames")
            # cleanup the windows
            cv2.destroyAllWindows()
            time.sleep(random.random())

ProducerThread().start()
ConsumerThread().start()
