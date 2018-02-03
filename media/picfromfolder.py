########### Python 3.6 #############
import requests, base64

headers = {
    # Request headers.
    'Content-Type': 'application/octet-stream',

    # NOTE: Replace the "Ocp-Apim-Subscription-Key" value with a valid subscription key.
    'Ocp-Apim-Subscription-Key': '07df2be5e9fb46b498edf414f709a24a',
}

params = {
    # Request parameters. All of them are optional.
    'visualFeatures': 'Categories,Description',
    #'details': 'Celebrities',
    'language': 'en',
}

fil='8'

# Replace the three dots below with the full file path to a JPEG image of a celebrity on your computer or network.
try:
    file=fil+'.jpg'
    image = open(file,'rb').read() # Read image file in binary mode
except:
    file=fil+'.jpeg'
    image = open(file,'rb').read()
print("Processing")
try:
    # NOTE: You must use the same location in your REST call as you used to obtain your subscription keys.
    #   For example, if you obtained your subscription keys from westus, replace "westcentralus" in the 
    #   URL below with "westus".
    response = requests.post(url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/analyze',
                             headers = headers,
                             params = params,
                             data = image)
    data = response.json()
    print (data)
    """
    try:
        print("Category: ",data['categories'][0]['name'])
    except:
        pass
    try:
        print("Description: ",data['description']['captions'][0]['text'])
    except:
        pass
    """
    try:
        print("Tags: ",data['description']['tags'])
    except:
        pass
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))
####################################

