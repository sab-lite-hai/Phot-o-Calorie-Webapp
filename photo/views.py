from django.shortcuts import render,redirect, render_to_response
import requests, base64, os, csv
from django.core.files.storage import FileSystemStorage
import pymysql.cursors
import datetime
from chatterbot import ChatBot

def connect():
	connection=pymysql.connect(host='localhost',user='root',password='qwerty123',db='photocalorie',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
	return connection

def disconnect(connection):
	connection.close()

chatbot = ChatBot('Ron Obvious',trainer='chatterbot.trainers.ChatterBotCorpusTrainer')
chatbot.train("chatterbot.corpus.english")

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
			contextdata={'food':"Cannot be identified",'size':None,'serving':None,'calorie':None,'fat':None, 'carbohydrate':None, 'protein':None}
		print (contextdata)
		return render(request,'photo/result.html',contextdata)
	return render(request,'photo/home.html')

def dashboard(request):
	connection=connect()
	cursor=connection.cursor()
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
		print (cal,pro,fa,carb,fo,factor)
		sql="insert into consumption values('saurabhrathi12','%s','%f','%f','%f','%f',curdate())"%(fo,cal,fa,carb,pro)
		cursor.execute(sql)
		connection.commit()
	disconnect(connection)
	connection=connect()
	cursor=connection.cursor()
	contextdata={}
	sql="""select sum(calories) as c, sum(fats) as f, sum(carbohydrates) as ca, sum(proteins) as p from consumption where date=curdate()"""
	cursor.execute(sql)
	result=cursor.fetchone()
	cursor.fetchall()
	contextdata['calorie']=(int(result['c']*100))/100.0
	contextdata['fat']=(int(result['f']*100))/100.0
	contextdata['carbohydrate']=(int(result['ca']*100))/100.0
	contextdata['protein']=(int(result['p']*100))/100.0
	anydate=request.POST.get('anydate')
	if not anydate:
		anydate=datetime.date.today().strftime('%Y-%m-%d')
	else:
		anydate=datetime.datetime.strptime(anydate, '%Y-%m-%d').date()
	query="""select fooditem,calories,fats,carbohydrates,proteins from consumption where date='%s'"""%(anydate)
	cursor.execute(query)
	result=cursor.fetchall()
	re=[]
	for item in result:
		a=[]
		a.append(item['fooditem'])
		a.append(item['calories'])
		a.append(item['fats'])
		a.append(item['carbohydrates'])
		a.append(item['proteins'])
		re.append(a)
	result=re
	contextdata['anydate']=anydate
	contextdata['consumption']=result
	return render(request,'photo/dashboard.html',contextdata)

def chat(request):
	query=request.POST.get('query')
	print(query)
	connection=connect()
	cursor=connection.cursor()
	if query:
		q=query.split()
		print(q)
		reply=None
		for word in q:
			if word in calorie.keys():
				print(word)
				reply="Here is what I found about "+word+"\n"
				reply=reply+"For serving of "+calorie[word]['serving']+"g. It consists of calories "+calorie[word]['calorie']+", fat "+calorie[word]['fat']+"g, protein "+calorie[word]['protein']+"g, carbohydrate "+calorie[word]['carbohydrate']+"g."
				break
		if not reply:
			reply=str(chatbot.get_response(query))
		print(query,reply)
		sql="insert into chat values('saurabhrathi12','%s','%s')"%(query,reply)
		try:
			cursor.execute(sql)
			connection.commit()
			disconnect(connection)
			connection=connect()
			cursor=connection.cursor()
		except:
			pass
	sql="select query,reply from chat where user='saurabhrathi12'"
	cursor.execute(sql)
	replies=cursor.fetchall()
	contextdata={}
	r=[]
	for i in replies:
		a=[]
		a.append(i['query'])
		a.append(i['reply'])
		r.append(a)
	contextdata['replies']=r

	return render(request,'photo/chat.html',contextdata)