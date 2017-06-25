########### Python 3.2 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '03419b61d0c34ae7bce784ed92fdbe80',
}

params = urllib.parse.urlencode({
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
})

body = '''
{
    "name":"sample_list",
    "userData":"User-provided data attached to the face list"
}'''

faceListId = '3'

try:
    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("PUT", "/face/v1.0/facelists/%s?%s" % (faceListId, params), body, headers)
    #print(body)
    #print("/face/v1.0/facelists/%s}?%s" % (faceListId, params))
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

####################################
