from django.shortcuts import render,redirect, render_to_response
import requests, base64, os, csv
from django.core.files.storage import FileSystemStorage
import pymysql.cursors

def connect():
	connection=pymysql.connect(host='localhost',user='user',password='qwerty123',db='photocalorie',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
	return connection

def disconnect(connection):
	connection.close()

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

def dashboard(request):
	cal=request.POST.get('calorie')
	pro=request.POST.get('protein')
	fa=request.POST.get('fat')
	carb=request.POST.get('carbohydrate')
	fo=request.POST.get('food')
	factor=request.POST.get('factor')
	if cal and pro and fa and carb and fo and factor:
		factor=float(factor)
		cal=float(cal)*factor
		pro=float(pro)*factor
		fa=float(fa)*factor
		carb=float(carb)*factor
		sql="insert into fooditem values('saurabhrathi12','%s','%f','%f','%f','%f',curdate())"%(fo,cal,fa,carb,pro)
		try:
			cursor.execute(sql)
		except:
			pass
	contextdata={}
	connection=connect()
	cursor=connection.cursor()
	sql="""select sum(calories), sum(fats), sum(carbohydrates), sum(proteins) from consumption where date=curdate()"""
	cursor.execute(sql)
	result=cursor.fetchone()
	contextdata['calorie']=result[0]
	contextdata['fat']=result[1]
	contextdata['carbohydrate']=result[2]
	contextdata['protein']=result[3]
	anydate=request.POST.get('anydate')
	if not anydate:
		anydate=datetime.date.today().strftime('%Y-%m-%d')
	else:
		anydate=datetime.datetime.strptime(anydate, '%Y-%m-%d').date()
	query="""select fooditem,calories,fats,carbohydrates,proteins from consumption where date='%s')"""%(anydate)
	cursor.execute(sql)
	result=cursor.fetchall()
	contextdata['anydate']=anydate
	contextdata['consumption']=result
	return render(request,'photo/dashboard.html',contextdata)
