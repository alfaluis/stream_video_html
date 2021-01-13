import glob
import os
import time
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, APIErrorException
import cv2
import utils


def train_person_group(key, endpoint, group_id, group_name, path_folder, person_group_name):
    """Function to add a new user to the Azure Service Identification.

    @param key: key connection of Azure Service
    @type key: str
    @param endpoint: Endpoint Azure Service
    @type endpoint: str
    @param group_id: Group ID of the identify service
    @type group_id: str
    @param group_name: Group Name of the identify service
    @type group_name: str
    @param path_folder: Folder path with the images of the user to add
    @type path_folder: str
    @param person_group_name: Name used to store the user in the Service
    @type person_group_name: str
    @return: Return train success or fail
    @rtype: str
    """
    face_client = FaceClient(endpoint, CognitiveServicesCredentials(key))

    print('Person group:', group_name)
    try:
        # create a PersonGroup reference class
        face_client.person_group.create(person_group_id=group_id, name=group_name, recognition_model="recognition_03")
    except APIErrorException:
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
    return training_status.status


def process_response(response):
    """This function try to clean the response got from the Azure Face Service.
       There are few cases to cover to receive a clean answer:
            - Response type list: If list is empty then no face/person detected/identified, else we return the list
            - Response type dict: If dict contains key 'name' then it is returning person_info,
                else the it's returning an error. If error code is 429 we exceed the free tier otherwise there is a
                connection error message

    @param response: Object with the response receive from Azure Service
    @type response: Dict or List
    @return: response object or None
    @rtype: (Dict, List or None,
    """
    if isinstance(response, list):
        if len(response) == 0:
            return None, 0
        else:
            return response, 0
    elif isinstance(response, dict):
        try:
            response['name']
            return response, 0
        except KeyError:
            print('error handling')
            err_code = response['error']['code']
            if int(err_code) == 429:
                return None, 10
            else:
                raise Exception(response['error'])
    else:
        return None, 0


def detect_face(endpoint, key, frame):
    """Run request to Azure Face service and return faces ID detected

    @param endpoint: Endpoint Azure Service
    @type endpoint: str
    @param key:  key connection of Azure Service
    @type key: str
    @param frame: Frame Image
    @type frame: numpy.ndarray
    @return: (List with all faceIds and rectangles of the detected faces, sleep seconds)
    @rtype: (list or None, int)
    """
    img = cv2.imencode('.jpg', frame)[1].tobytes()
    attributes = ''
    detected_faces = utils.detect_face_stream(endpoint=endpoint, key=key, image=img, face_attributes=attributes,
                                              recognition_model='recognition_03')

    detected_faces, sleep_time = process_response(detected_faces)
    return detected_faces, sleep_time


def identify_and_process(detected_faces, endpoint, key, group_id):
    identify_response = list()

    # Face Ids to search in the person group (10 max)
    faces_ids = [f['faceId'] for f in detected_faces]
    identify_output = utils.identify_faces(endpoint=endpoint, key=key, group_id=group_id, face_id_list=faces_ids)
    identify_output, sleep_time = process_response(identify_output)
    if sleep_time == 10:
        time.sleep(sleep_time)

    if identify_output is not None:
        for person in identify_output:
            # print(person)
            try:
                # get the most confidence candidate to process
                candidate = person['candidates'][0]
                # while cycle to ensure we return person info (free tier limit)
                person_info = None
                while person_info is None:
                    person_info = utils.get_person_info(endpoint, key, group_id, candidate['personId'])
                    person_info, sleep_time = process_response(person_info)
                    if sleep_time == 10:
                        time.sleep(sleep_time)

                identify_response.append({'faceId': person['faceId'],
                                          'name': person_info['name'],
                                          'confidence': candidate['confidence']})
            except IndexError:
                # No candidates found
                identify_response.append({'faceId': person['faceId'],
                                          'name': None,
                                          'confidence': 0})
        return identify_response
    return None


def identify_from_video(endpoint, key, group_id, frame):
    """ Main function to detect faces in 'frame' and detect if its are contained in the 'group_id'

    @param endpoint: Endpoint Azure Service
    @type endpoint: str
    @param key: key connection of Azure Service
    @type key: str
    @param group_id:
    @type group_id: str
    @param frame: Frame Image
    @type frame: numpy.ndarray
    @return: (frame image, string name)
    @rtype: (numpy.ndarray, str or None)
    """
    start_measure = time.time()
    thickness = 2
    detected_faces, sleep_time = detect_face(endpoint, key, frame)
    print(detected_faces)
    if sleep_time == 10:
        time.sleep(sleep_time)

    if detected_faces is not None:
        faces_info = identify_and_process(detected_faces, endpoint, key, group_id)
        print('Detected: {} and Info {}'.format(detected_faces, faces_info))
        for face, info in zip(detected_faces, faces_info):
            if info['confidence'] > 0.5:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
            frame = cv2.rectangle(frame, *utils.get_rectangle(face), color, thickness)

        print('Total time required:', time.time() - start_measure)
        return frame, faces_info

    print('Total time required:', time.time() - start_measure)
    return frame, None
