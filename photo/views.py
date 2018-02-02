from django.shortcuts import render,redirect
import requests, base64
from django.core.files.storage import FileSystemStorage
import os

def photoidentify(file):
	headers = {
		'Content-Type': 'application/octet-stream',
		'Ocp-Apim-Subscription-Key': '07df2be5e9fb46b498edf414f709a24a',
	}
	params = {
		'visualFeatures': 'Categories,Description',
		'language': 'en',
	}
	image = open(os.getcwd()+file,'rb').read()
	print ("Loading content")
	try:
		response = requests.post(url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/analyze',
								 headers = headers,
								 params = params,
								 data = image)
		data = response.json()
		print (data)
		try:
			print("Tags: ",data['description']['tags'])
		except:
			pass
	except Exception as e:
		print("[Errno {0}] {1}".format(e.errno, e.strerror))

def home(request):
	if request.FILES:
		print ("Hi")
		image=request.FILES["Pic"]
		fs= FileSystemStorage()
		filename = fs.save(image.name, image)
		uploaded_file_url = fs.url(filename)
		print (uploaded_file_url)
		photoidentify(uploaded_file_url)
	return render(request,'home.html')
