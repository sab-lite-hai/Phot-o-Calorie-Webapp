from django.shortcuts import render,redirect, render_to_response
import requests, base64, os, csv
from django.core.files.storage import FileSystemStorage

calorie=dict()
f=csv.reader(open('photo/caloriechart.csv', 'rt'))
data=[]
for row in f:
	data.append(row)
data=data[1::]
for row in data:
	calorie[row[0]]=dict()
	calorie[row[0]]['size']=row[1]
	calorie[row[0]]['serving']=row[2]
	calorie[row[0]]['calorie']=row[3]
	calorie[row[0]]['fat']=row[4]
	calorie[row[0]]['carbohydrate']=row[5]
	calorie[row[0]]['protein']=row[6]

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
	calorie.keys()
	if request.FILES:
		image=request.FILES["Pic"]
		fs= FileSystemStorage()
		filename = fs.save(image.name, image)
		uploaded_file_url = fs.url(filename)
		print (uploaded_file_url)
		tags=photoidentify(uploaded_file_url)
		contextdata={}
		k=1
		for tag in tags:
			if tag in calorie.keys():
				k=0
				contextdata['food']=tag
				for key in calorie[tag]:
					contextdata[key]=calorie[tag][key]
				break
		if k:
			contextdata['food']="Cannot be identified"
			contextdata['calorie']=None
		print (contextdata)
		return render(request,'photo/result.html',contextdata)
	return render(request,'photo/home.html')

def result(request):
	
	return render(request,'photo/result.html')