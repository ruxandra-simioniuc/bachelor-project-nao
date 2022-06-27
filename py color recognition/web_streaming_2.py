from flask import Flask, render_template, Response
import cv2
from naoqi import ALProxy
import numpy as np

# https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00
# Initialize the Flask app
app = Flask(__name__)

# robotIP = "192.168.90.238"
# girl
robotIP = "172.20.10.3"

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
    image = np.zeros((height, width, 3), np.uint8)

    while True:
        # success, frame = camera.read()  # read the camera frame
        # frame = cv2.flip(frame, 1)

        # get image
        result = videoDevice.getImageRemote(captureDevice)

        if result is None:
            break
        else:
            # translate value to mat
            values = map(ord, list(result[6]))
            i = 0
            for y in range(0, height):
                for x in range(0, width):
                    image.itemset((y, x, 0), values[i + 0])
                    image.itemset((y, x, 1), values[i + 1])
                    image.itemset((y, x, 2), values[i + 2])
                    i += 3

            cv2.circle(image, (width/2, height/2), 2, (0,0,255), -1)
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)