import glob
import os
import time
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, APIErrorException
import cv2
import utils


def train_person_group(key, endpoint, group_id, group_name, path_folder, person_group_name):

    face_client = FaceClient(endpoint, CognitiveServicesCredentials(key))

    print('Person group:', group_name)
    try:
        # create a PersonGroup reference class
        face_client.person_group.create(person_group_id=group_id, name=group_name, recognition_model="recognition_03")
    except APIErrorException as err:
        print('person group {0}:{1} already exist.'.format(group_id, group_name))

    # create Person object inside the person group
    person_obj = face_client.person_group_person.create(group_id, person_group_name)

    # search for images in folder path
    path_to_images = glob.glob(os.path.join(path_folder, '*.jpg'))
    for path_ in path_to_images:
        print(path_)
        w = open(path_, 'r+b')
        face_client.person_group_person.add_face_from_stream(group_id, person_obj.person_id, w, detection_model="detection_01")

    print('Training the person group...')
    # Train the person group
    face_client.person_group.train(group_id)
    while True:
        training_status = face_client.person_group.get_training_status(group_id)
        print("Training status: {}.".format(training_status.status))
        print()
        if training_status.status is TrainingStatusType.succeeded:
            break
        elif training_status.status is TrainingStatusType.failed:
            print('Training the person group has failed.')
        time.sleep(5)


def identify_from_video(endpoint, key, group_id, frame):
    img = cv2.imencode('.jpg', frame)[1].tobytes()
    attributes = ''
    detected_faces = utils.detect_face_stream(endpoint=endpoint, key=key, image=img, face_attributes=attributes,
                                              recognition_model='recognition_03')

    print(detected_faces)
    # ADD CONDITIONAL, IF DETECTED IS EMPTY END FUNCTION
    faces_ids = [f['faceId'] for f in detected_faces]
    identify_output = utils.identify_faces(endpoint=endpoint, key=key, group_id=group_id, face_id_list=faces_ids)
    print(identify_output)
    thickness = 2
    for person in identify_output:
        print(type(person['faceId']))
        print('Result of face: {0}.'.format(person['faceId']))
        face = [face for face in detected_faces if face['faceId'] == person['faceId']][0]
        if not len(person['candidates']) == 0:
            candidate = person['candidates'][0]
            print('Identified in {} with a confidence: {}.'.format(person['faceId'], candidate['confidence']))
            person_info = utils.get_person_info(endpoint, key, group_id, candidate['personId'])
            print('Name Group person identified: {0}'.format(person_info['name']))
            color = (0, 255, 0)
            frame = cv2.rectangle(frame, *utils.get_rectangle(face), color, thickness)
            x, y = face['faceRectangle']['left'], face['faceRectangle']['top'] - 5
            cv2.putText(frame, person_info['name'], (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)
        else:
            print('no match found')
            color = (255, 0, 0)
            frame = cv2.rectangle(frame, *utils.get_rectangle(face), color, thickness)
    
    return frame
