import cv2
#from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tk
import threading
import datetime
import imutils
import os


class PhotoBoothApp:
    def __init__(self):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        #self.vs = vs
        #self.outputPath = outputPath
        self.frame = None
        self.thread = None
        self.stopEvent = None
        # initialize the root window and image panel
        self.root = tk.Tk()
        self.panel = None

        # create a button, that when pressed, will take the current
        # frame and save it to file
        btn = tk.Button(self.root, text="Start stream!",
                         command=self.startStream)
        btn.pack(side="bottom", fill="both", expand="yes", padx=10,
                 pady=10)



        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()

        # set a callback to handle when the window is closed
        self.root.wm_title("NAO Interactive System")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)


    def videoLoop(self):
        try:
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it to
                # have a maximum width of 300 pixels
                ret, self.frame = self.cap.read()

                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                # if the panel is not None, we need to initialize it
                if self.panel is None:
                    self.panel = tk.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)

                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")

    def startStream(self):

        print('pressed button')
        os.system("py -2 D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\nao_everything\\web_streaming.py")

        self.cap = cv2.VideoCapture('http://127.0.0.1:5000/video_feed')
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        # # grab the current timestamp and use it to construct the
        # # output path
        # ts = datetime.datetime.now()
        # filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        # p = os.path.sep.join((self.outputPath, filename))
        # # save the file
        # cv2.imwrite(p, self.frame.copy())
        # print("[INFO] saved {}".format(filename))

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.cap.release()
        self.root.quit()




# cap = cv2.VideoCapture('http://127.0.0.1:5000/video_feed')
#
# while True:
#     ret, frame = cap.read()
#     """
#     your code here
#     """
#     cv2.imshow('frame', frame)
#     if cv2.waitKey(20) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()
