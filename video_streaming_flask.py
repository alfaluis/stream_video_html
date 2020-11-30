import argparse
import time
import json
import os
from flask import Flask, render_template, Response, request
import cv2
import utils
import shutil

app = Flask(__name__, static_folder='static', template_folder='templates')
HEIGHT = 240
WIDTH = 320
start_take_photo = False
start_time = 0
count_img = 0
folder_name = ''
root = os.path.join(os.getcwd(), 'data')


@app.route('/')
def index():
    return render_template('index.html', w=WIDTH, h=HEIGHT)


def create_folder(path_to_create):
    if os.path.exists(path_to_create):
        shutil.rmtree(path_to_create)
    os.makedirs(path_to_create)


def gen():
    global start_take_photo, count_img, start_time, folder_name
    while True:
        ret, frame = vid.read()
        img = cv2.imencode('.jpg', frame)[1].tobytes()

        if start_take_photo:
            create_folder(os.path.join(root, folder_name))

            if time.time() - start_time > 3:
                start_take_photo = False
            print('taking pictures')
            cv2.imwrite(os.path.join(root, folder_name, 'img_{}.jpg'.format(count_img)), frame)
            count_img += 1
        else:
            start_time = time.time()
            count_img = 0

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


@app.route('/route/to/change_color', methods=['POST'])
def change_color():
    global start_take_photo, folder_name
    start_take_photo = bool(request.form['take_pics'])
    in_floor = request.form['floor'].replace(' ', '')
    in_name = request.form['name'].replace(' ', '')
    folder_name = in_name + in_floor
    print(start_take_photo, in_floor, in_name, folder_name)
    return json.dumps({'Status': "OK"})


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
    app.run(debug=True)

    # release camera
    vid.release()

