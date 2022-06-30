import argparse

from flask import Flask, render_template, Response
import cv2
from naoqi import ALProxy
import numpy as np

# https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00
# Initialize the Flask app
import utils_camera_voice as camera

app = Flask(__name__)

# robotIP = "192.168.90.238"
# girl
# robotIP = "172.20.10.3"

robotIP = ""

# boy
# robotIP = "172.20.10.5"
port = 9559


def gen_frames():
    videoDevice = ALProxy('ALVideoDevice', robotIP, port)

    AL_kQVGA = 1  # 320x240
    AL_kBGRColorSpace = 13
    FPS = 30
    captureDevice = videoDevice.subscribeCamera(
        "test", 1, AL_kQVGA, AL_kBGRColorSpace, FPS)

    # create image
    width = 320
    height = 240

    while True:
        # get image
        result = videoDevice.getImageRemote(captureDevice)

        if result is None:
            break
        else:
            image = camera.getMatValues(result, height, width)

            # this line can be commented
            # it draws a small red circle in the middle of the image
            cv2.circle(image, (width / 2, height / 2), 2, (0, 0, 255), -1)
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


def gen_frames_webcam():
    cam = cv2.VideoCapture(0)

    while True:
        ret, frame = cam.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames_webcam(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Arguments for running Task 2")
    parser.add_argument("robotIP", help="The robot ip as a string")
    args = parser.parse_args()

    robotIP = args.robotIP

    app.run(debug=True)
