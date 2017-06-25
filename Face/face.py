import http.client, urllib.request, urllib.parse, urllib.error, base64, requests, json
import sys
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD
import h5py

def printlog(s):
    with open("log.log", "a") as f:
        f.write(str(s) + "\n")


subscription_key = '03419b61d0c34ae7bce784ed92fdbe80'

uri_base = 'https://westus.api.cognitive.microsoft.com'


# def search_face(face_id):
#     body = {
#         "faceId": face_id,
#         "faceListId": "aihackathon",
#         "maxNumOfCandidatesReturned": 10,
#         "mode": "matchPerson"
#     }
#     api = "https://westus.api.cognitive.microsoft.com/face/v1.0/findsimilars"
#     r = requests.post(api, headers=headers, data=json.dumps(body))
#     faces = r.json()
#     person = faces[0]
#     for i in faces:
#         if person["confidence"] < i["confidence"]:
#             person = i
#     print(person["persistedFaceId"])


# Request headers.
headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '03419b61d0c34ae7bce784ed92fdbe80',
}

# Request parameters.
params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'emotion',
}

# Body. The URL of a JPEG image to analyze.
# body = {'url': 'https://upload.wikimedia.org/wikipedia/commons/c/c4/RH_Louise_Lillian_Gish.jpg'}
if len(sys.argv) == 2:
    img_url = sys.argv[1]
else:
    img_url = 'http://43.241.238.58:5000/static/upload/IMG_201706250113327673.jpg'
body = {'url': img_url}

try:
    # Execute the REST API call and get the response.
    import time
    time.sleep(4)
    printlog("BEFORE POST")
    response = requests.request('POST', uri_base + '/face/v1.0/detect', json=body, data=None, headers=headers, params=params)
    printlog("AFTER POST")

    data = json.loads(response.text)

    printlog("JSON LOADED")
    printlog(str(data))
    printlog("")

    emotions = np.zeros((len(data), 8))
    attentions = np.zeros(len(data))
    faceID = []
    positions = np.zeros((len(data), 4))

    for i in range(len(data)):
        emotions[i][0] = data[i]['faceAttributes']['emotion']['fear']
        emotions[i][1] = data[i]['faceAttributes']['emotion']['disgust']
        emotions[i][2] = data[i]['faceAttributes']['emotion']['neutral']
        emotions[i][3] = data[i]['faceAttributes']['emotion']['happiness']
        emotions[i][4] = data[i]['faceAttributes']['emotion']['contempt']
        emotions[i][5] = data[i]['faceAttributes']['emotion']['surprise']
        emotions[i][6] = data[i]['faceAttributes']['emotion']['anger']
        emotions[i][7] = data[i]['faceAttributes']['emotion']['sadness']
        positions[i][0] = data[i]['faceRectangle']['left']
        positions[i][1] = data[i]['faceRectangle']['height']
        positions[i][2] = data[i]['faceRectangle']['width']
        positions[i][3] = data[i]['faceRectangle']['top']
        faceID.append(data[i]['faceId'])

    printlog("FACEID PROCESSED")
    # print(emotions)
    # print(positions)
    # print(faceID)
    # Use neural network to determine the attention of student
    model = Sequential()
    model.add(Dense(64, activation='relu', input_dim=8))
    model.add(Dropout(0.25))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(1, activation='sigmoid'))
    model.load_weights('model.h5')
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='mse',
                  optimizer=sgd,
                  metrics=['accuracy'])
    attentions = model.predict(emotions)
    printlog("MODEL FINISHED")
    # print(attentions)

except Exception as e:
    print('Error:')
    print(e)


headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '03419b61d0c34ae7bce784ed92fdbe80',
}

params = urllib.parse.urlencode({

})
similarity = []

print('data:', data)
print('faceID:', faceID)
print('len(data): ', len(data))
print('len(faceID): ', len(faceID))

for i in range(len(data)):

    printlog('i: ' + str(i))
    printlog('len(faceID): ' + str(len(faceID)))
    printlog('faceID: ' + str(faceID))
    printlog('data: ' + str(data))

    body = """{
        "faceId":\"""" + str(faceID[i]) + """\",
        "faceListId":"aihackathon",
        "maxNumOfCandidatesReturned":10,
        "mode": "matchPerson"
    }"""

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/findsimilars?%s" % params, body, headers)
        # print(body)
        response = conn.getresponse()
        data = response.read()
        # Compute the most similar id here
        faces = json.loads(data.decode('utf-8'))
        if len(faces) == 0:
            continue
        # print('faces:', faces)
        person = faces[0]
        for i in faces:
            if person["confidence"] < i["confidence"]:
                person = i
        # print(person["persistedFaceId"])
        faceId = person["persistedFaceId"]
        # print(json.loads(data.decode('utf-8')))
        similarity.append(faceId)
        # print(similarity)
        conn.close()
    except Exception as e:
        # print("[Errno {0}] {1}".format(e.errno, e.strerror))
        print(e)

if len(attentions) != 0:
    print(list(zip(similarity, attentions[0])))

exit(0)
