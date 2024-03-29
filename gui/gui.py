import re
import sys
import time
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import threading
import os
import signal
from subprocess import Popen, PIPE


class Timeout:

    def __init__(self, seconds=1, error_message='TimeoutError'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


class NAOGUI(tk.Tk):
    def __init__(self):
        self.frame = None
        self.thread = None
        self.thread2 = None

        self.thread3 = None
        self.thread4 = None
        self.thread5 = None
        self.thread_finished = False
        self.stopEvent = None

        self.root = tk.Tk()
        self.panel = None
        self.cap = None

        self.currentIp = "172.20.10.3"
        self.currentObject = "flamingo"
        self.currentColor = "red"

        self.root.geometry("590x450")

        self.space = tk.Label(self.root)
        self.space.grid(column=0, row=0)

        self.btn_Stream = tk.Button(self.root, text="Start stream",
                                    command=self.streamAndDisplay)
        # self.btn_Stream.pack(fill="both", expand="yes", padx=10, pady=10, anchor="w")
        self.btn_Stream.grid(row=0, column=1, pady=(10, 5), sticky="ew")

        self.btn_Task1 = tk.Button(self.root, text="Ask for an object", command=self.startTask1)
        self.btn_Task1.grid(row=1, column=1, pady=(10, 5), sticky="ew")
        self.btn_Task1['state'] = 'disable'
        # self.btn_Task1.pack(fill="both", expand="yes", padx=10, pady=10, anchor="w")

        self.btn_Task2 = tk.Button(self.root, text="Go to object",
                                   command=self.startTask2)
        # self.btn_Task2.pack(fill="both", expand="yes", padx=10, pady=10, anchor="w")
        self.btn_Task2.grid(row=2, column=1, pady=(10, 5), sticky="ew")
        self.btn_Task2['state'] = 'disable'

        self.ipVar = tk.StringVar(self.root, "172.20.10.3")

        self.radio_ip1 = tk.Radiobutton(self.root, text="172.20.10.3", variable=self.ipVar, value="172.20.10.3")
        self.radio_ip1.grid(row=0, column=3, sticky="ew")

        self.radio_ip2 = tk.Radiobutton(self.root, text="172.20.10.5", variable=self.ipVar, value="172.20.10.5")
        self.radio_ip2.grid(row=0, column=4, sticky="ew")

        self.radio_ip3 = tk.Radiobutton(self.root, text="other", variable=self.ipVar, value="0")
        self.radio_ip3.grid(row=0, column=5, sticky="ew")

        self.text_ip = tk.Text(self.root, height=1, width=15)
        self.text_ip.grid(row=0, column=6, sticky="ew")

        self.label_ip = tk.Label(self.root, text="IP address:")
        self.label_ip.grid(row=0, column=2, padx=5)

        self.label_color = tk.Label(self.root, text="Choose color")
        self.label_color.grid(row=1, column=2, padx=5)

        self.colorVar = tk.StringVar()
        self.combo_color = ttk.Combobox(self.root, textvariable=self.colorVar, width=10)
        self.combo_color['values'] = ('red', 'blue', 'yellow', 'green')
        self.combo_color.grid(row=1, column=3)
        self.combo_color.current(0)

        self.label_object = tk.Label(self.root, text="Choose object")
        self.label_object.grid(row=2, column=2, padx=5)

        self.objectVar = tk.StringVar()
        self.combo_object = ttk.Combobox(self.root, textvariable=self.objectVar, width=10)
        self.combo_object['values'] = ('bear', 'flamingo', 'duck', 'blue ball', 'frog', 'orange spike', 'dino')
        self.combo_object.grid(row=2, column=3)
        self.combo_object.current(0)

        self.text_log = tk.Text(self.root, height=4, width=55, fg='red')
        self.text_log.grid(row=3, column=1, columnspan=5)
        self.text_log.configure(state=tk.DISABLED)

        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()

        # set a callback to handle when the window is closed
        self.root.wm_title("NAO Interactive System")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    def test(self):
        print('i was pressed')

    def streamAndDisplay(self):

        ok = True
        self.currentIp = self.ipVar.get()

        print("ip:" + str(self.currentIp))

        if self.currentIp == "0":
            self.currentIp = self.text_ip.get("1.0", 'end-1c')
            print("ip from text box: " + str(self.currentIp))
            if 7 > len(self.currentIp) or len(self.currentIp) > 16 or re.search('[a-zA-Z]', self.currentIp):
                self.text_log.configure(state=tk.NORMAL)
                self.text_log.insert(tk.END, "ERROR: IP Address is not ok\n")
                self.text_log.configure(state=tk.DISABLED)
                ok = False

        if ok:
            self.radio_ip1.configure(state=tk.DISABLED)
            self.radio_ip2.configure(state=tk.DISABLED)
            self.radio_ip3.configure(state=tk.DISABLED)
            self.text_log.configure(state=tk.DISABLED)
            self.label_ip.configure(state=tk.DISABLED)

            self.btn_Stream["state"] = "disable"
            self.thread = threading.Thread(target=self.startStream, args=())
            self.thread.daemon = True
            self.thread.start()

            time.sleep(5)

            self.cap = cv2.VideoCapture('http://127.0.0.1:5000/video_feed10')
            self.thread2 = threading.Thread(target=self.videoLoop, args=())
            self.thread2.daemon = True
            self.thread2.start()

            if self.thread2.is_alive():
                self.btn_Task1['state'] = 'normal'
                self.btn_Task2['state'] = 'normal'

    def videoLoop(self):
        try:
            while not self.stopEvent.is_set():
                ret, self.frame = self.cap.read()

                if ret:
                    image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)

                    # initialize panel
                    if self.panel is None:
                        self.panel = tk.Label(image=image, width=320, height=240)
                        self.panel.image = image
                        self.panel.grid(row=4, column=1, columnspan=6, pady=5)

                    # update panel image
                    else:
                        self.panel.configure(image=image)
                        self.panel.image = image
                else:
                    break
        except RuntimeError as e:
            print("RuntimeError")

    def startStream(self):

        print('pressed button')
        os.system(
            "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\nao_everything\\venv\\Scripts\\python "
            "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\nao_everything\\web_streaming.py " + str(
                self.currentIp))

    def startTask1(self):
        self.thread3 = threading.Thread(target=self.task1, args=())
        self.thread3.daemon = True
        self.thread3.start()

    def startTask2(self):

        self.thread5 = threading.Thread(target=self.startYolo, args=())
        self.thread5.daemon = True
        self.thread5.start()

        if self.thread5.is_alive():
            time.sleep(5)
            self.thread4 = threading.Thread(target=self.task2, args=())
            self.thread4.daemon = True
            self.thread4.start()

    def startYolo(self):

        path_to_weights = "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\yolo_project\\yolov5\\runs\\train\\yolo_toys_v2_det\\weights\\best.pt"

        arguments = "--source http://127.0.0.1:5000/video_feed10 --weights " + path_to_weights + " --save-conf --name yolo_toys_v2_det --save-txt"

        os.system(
            "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\yolo_project\\yolov5\\venv\\Scripts\\python "
            "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\yolo_project\\yolov5\\detect.py " + arguments)

    def task1(self):

        self.currentColor = self.colorVar.get()

        self.btn_Task2["state"] = "disable"

        os.system(
            "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\nao_everything\\venv\\Scripts\\python "
            "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\nao_everything\\task1.py " + str(
                self.currentIp) + " " + str(self.currentColor))

        self.btn_Task2["state"] = "normal"

    def task2(self):
        self.currentObject = self.objectVar.get()

        self.btn_Task1["state"] = "disable"

        os.system(
            "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\nao_everything\\venv\\Scripts\\python "
            "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\nao_everything\\task2.py " + str(
                self.currentIp) + " " + str(self.currentObject))

        # os.system(
        #     "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\nao_everything\\venv\\Scripts\\python "
        #     "D:\\RUXI_DOC\\Descktop\\fACultate\\LICENTA\\licenta-nao\\nao_everything\\aux_py\\test.py " + str(
        #         self.currentIp) + " " + str(self.currentObject))

        self.btn_Task1["state"] = "normal"

    def onClose(self):
        self.stopEvent.set()
        self.root.quit()
        sys.exit(0)

    def monitorThread(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.monitorThread(thread))
            self.thread_finished = True
        else:
            self.thread_finished = True
