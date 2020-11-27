import argparse
import time

from flask import Flask, render_template, Response
import cv2
import utils

app = Flask(__name__, static_folder='static', template_folder='templates')
HEIGHT = 240
WIDTH = 320


@app.route('/')
def index():
    return render_template('index.html', w=WIDTH, h=HEIGHT)


def gen():
    while True:
        ret, frame = vid.read()
        img = cv2.imencode('.jpg', frame)[1].tobytes()
        detected_faces = utils.detect_face_stream(endpoint=ENDPOINT, key=KEY, image=img)

        print('Image num face detected {}'.format(detected_faces))
        color = (255, 0, 0)
        thickness = 2
        for face in detected_faces:
            print(face)
            frame = cv2.rectangle(frame, *utils.get_rectangle(face), color, thickness)
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

