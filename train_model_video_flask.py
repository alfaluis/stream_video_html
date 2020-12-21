import argparse
import time
import json
import os
from flask import Flask, render_template, Response, request, jsonify
import cv2
import shutil
from train_and_detect import train_person_group


app = Flask(__name__, static_folder='static', template_folder='templates')
HEIGHT = 240
WIDTH = 320
GROUP_ID = 'building-1-id'
GROUP_NAME = 'building-1'
start_take_photo = False
train_status = None
start_time = 0
count_img = 0
folder_name, folder_path = '', ''
root = os.path.join(os.getcwd(), 'data')


def create_folder(path_to_create):
    if os.path.exists(path_to_create):
        shutil.rmtree(path_to_create)
    os.makedirs(path_to_create)


def gen():
    global start_take_photo, count_img, start_time, folder_path
    while True:
        ret, frame = vid.read()
        img = cv2.imencode('.jpg', frame)[1].tobytes()

        if start_take_photo:
            if count_img == 0:
                folder_path = os.path.join(root, folder_name)
                create_folder(folder_path)

            if time.time() - start_time >= 3:
                start_take_photo = False
                print('Stop Taking photos')
            else:
                print('taking pictures')
                cv2.imwrite(os.path.join(root, folder_name, 'img_{}.jpg'.format(count_img)), frame)
                count_img += 1
                time.sleep(0.2)
        else:
            start_time = time.time()
            count_img = 0

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html', w=WIDTH, h=HEIGHT)


@app.route('/video_feed')
def video_feed():
    return Response(gen(),  mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/client_info', methods=['POST'])
def change_color():
    global start_take_photo, folder_name
    response = request.get_json()
    start_take_photo = bool(response['take_pics'])
    in_floor = response['floor'].replace(' ', '')
    in_name = response['name'].replace(' ', '')
    folder_name = in_name + in_floor
    while start_take_photo:
        print(start_take_photo, in_floor, in_name, folder_name)
        time.sleep(.2)
    return json.dumps({'UploadProcess': "Success"})


@app.route('/training_status', methods=['GET'])
def testfn():
    global train_status, start_time
    start_time = time.time()
    train_status = train_person_group(key=KEY, endpoint=ENDPOINT, group_id=GROUP_ID, group_name=GROUP_NAME,
                                      path_folder=folder_path, person_group_name=folder_name)
    message = {'TrainStatus': train_status}
    return jsonify(message)  # serialize and use JSON headers


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

