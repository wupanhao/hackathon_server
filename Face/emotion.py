########### Python 3.2 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64, sys
import json
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD
import h5py


emotions = np.zeros((len(data), 8))
attentions = np.zeros(len(data))
positions = np.zeros((len(data), 4))


headers = {
    # Request headers. Replace the placeholder key below with your subscription key.
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '856148e7a79644ceb1cb7886cb550bd9',
}

params = urllib.parse.urlencode({
})

# Replace the example URL below with the URL of the image you want to analyze.
body = "{ 'url': 'https://upload.wikimedia.org/wikipedia/commons/3/39/Student_in_Class_%283618969705%29.jpg' }"

try:
    # NOTE: You must use the same region in your REST call as you used to obtain your subscription keys.
    #   For example, if you obtained your subscription keys from westcentralus, replace "westus" in the
    #   URL below with "westcentralus".
    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("POST", "/emotion/v1.0/recognize?%s" % params, body, headers)
    response = conn.getresponse()
    res = str(response.read(), encoding="utf-8")
    data = json.loads(res)

    for i in range(len(data)):
        emotions[i][0] = data[i]['scores']['fear']
        emotions[i][1] = data[i]['scores']['disgust']
        emotions[i][2] = data[i]['scores']['neutral']
        emotions[i][3] = data[i]['scores']['happiness']
        emotions[i][4] = data[i]['scores']['contempt']
        emotions[i][5] = data[i]['scores']['surprise']
        emotions[i][6] = data[i]['scores']['anger']
        emotions[i][7] = data[i]['scores']['sadness']
        positions[i][0] = data[i]['faceRectangle']['left']
        positions[i][1] = data[i]['faceRectangle']['height']
        positions[i][2] = data[i]['faceRectangle']['width']
        positions[i][3] = data[i]['faceRectangle']['top']
    #print(emotions)
    #print(positions)
    #Use neural network to determine the attention of student
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
    #print(attentions)



    conn.close()
except Exception as e:
    print(e.args)
####################################
