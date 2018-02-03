from django.shortcuts import render,redirect, render_to_response
import requests, base64, os
from django.core.files.storage import FileSystemStorage

calorie=dict()
f=open('photo/caloriechart.txt','r')
lines=f.readlines()
for line in lines:
	a=line.split()
	calorie[a[0]]=a[1]
f.close()

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
			return data['description']['tags']
		except:
			pass
	except Exception as e:
		print("[Errno {0}] {1}".format(e.errno, e.strerror))
	return None

def home(request):
	if request.FILES:
		print ("Hi")
		image=request.FILES["Pic"]
		fs= FileSystemStorage()
		filename = fs.save(image.name, image)
		uploaded_file_url = fs.url(filename)
		print (uploaded_file_url)
		tags=photoidentify(uploaded_file_url)
		contextdata={}
		for tag in tags:
			if tag in calorie.keys():
				print (tag)
				contextdata['food']=tag
				contextdata['calorie']=calorie[tag]
	#	if not contextdata['food']:
	#		contextdata['food']="Cannot be identified"
	#		contextdata['calorie']=None
		return render(request,'photo/result.html',contextdata)
	return render(request,'photo/home.html')

def result(request):
	
	return render(request,'photo/result.html')