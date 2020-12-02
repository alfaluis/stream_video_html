import argparse
import time

from flask import Flask, render_template, Response
import cv2
import utils
from train_and_detect import identify_from_video

app = Flask(__name__)
HEIGHT = 240
WIDTH = 320
GROUP_ID = 'building-1-id'
GROUP_NAME = 'building-1'


@app.route('/')
def index():
    return render_template('index.html', w=WIDTH, h=HEIGHT)


def gen():
    while True:
        ret, frame = vid.read()
        frame = identify_from_video(endpoint=ENDPOINT, key=KEY, group_id=GROUP_ID, frame=frame)
        img_send = cv2.imencode('.jpg', frame)[1].tobytes()

        time.sleep(1)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_send + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(),  mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", "--KEY", required=True, help="Access key of endpoint")
    ap.add_argument("-sn", "--SERVICE_NAME", required=True, help="Face service name")
    args = vars(ap.parse_args())

    # configure the face client
    KEY = args['KEY']
    ENDPOINT = 'https://{0}.cognitiveservices.azure.com/'.format(args['SERVICE_NAME'])

    # create a video object and configure size of the output image
    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    # run app
    app.run(debug=False)

    # release camera
    vid.release()
