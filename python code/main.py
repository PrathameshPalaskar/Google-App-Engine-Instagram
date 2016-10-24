import base64
import json
from collections import defaultdict

from bson import ObjectId
from flask import Flask,render_template,request,session
from pymongo import MongoClient
import gridfs
import os,datetime

app = Flask(__name__)
app.secret_key = 'PRATHAMESH123'

def create_conn():
    client=MongoClient('mongodb://********/')
    return client


@app.route('/')
def hello_world():
    return render_template('upload.html')

#this is the module for registration of a new user
@app.route('/register',methods=['POST'])
def register():
    print "Registration method entered"
    conn=create_conn()
    user_name=request.form['user_name']

    passw=request.form['user_pass']
    print "got user and password"
    count=conn.db.users.insert_one({'username':user_name,'password':passw})
    print count
    conn.close()
    #return render_template('login.html')
    return "Registration successful"

#this is the module for login of the user and validation 
@app.route('/login',methods=['POST'])
def login():
    conn=create_conn()
    print "connection created"
    user_name = request.form['user_name']
    passw = request.form['user_pass']
    sample=datetime.datetime.date()
    print sample
    #grp=request.form['group_name']
    result=conn.db.users.find_one({'username':user_name},{'password':1,'_id':0})
    print result
    '''if (user_name == '***********' and passw == '*****'):
        conn.close()
        return render_template('new.html')'''
    if passw == result['password']:
        session['user_name'] = user_name
        '''if grp:
            conn.db.users.update({'username':session['user_name']},{"$set":{"Group":grp}})'''



        conn.close()
        return render_template("upload.html")

    else:
        conn.close()
        return "Please go back"

#Upload module for uploading the picures & comments,limiting file size and number of pictures
    
@app.route('/upload',methods=['POST'])
def upload():
    conn=create_conn()
    mongoobj=conn.db
    fs=gridfs.GridFS(mongoobj)
    files=request.files['file_upload']
    comments=str(request.values['comment'])
    str_time=datetime.datetime.now()
    cnt_photo_id=1
    #getgroup=conn.db.users.find_one({"username": session['user_name']},{"Group":1,"_id":0})
    #getgroup=getgroup['Group']
    #print getgroup
    #n = conn.db.photo_count.find_one({"username": session['user_name']}, {"count": 1, "_id": 0})
    '''if n:
        num = n['count']
        if num <= 5:
            num = num + 1
            conn.db.photo_count.update({"username": session['user_name']}, {"$set": {"count": num}})

        else:
            return "Exceeded limit"

    else:
        count = 1
        conn.db.photo_count.insert({"username": session['user_name'], "count": count})'''
    #conn.db.photo_count.insert({"username": session['user_name'],"uploadtime":str_time})

    s = os.stat(files.filename)
    photo_size = s.st_size
    if photo_size > 300000:
        return "file size large"

    pic_no = fs.put(files, filename=files.filename)
    #conn.db.photos.insert({"username": session["user_name"], "photoid": pic_no, "comments": comments,"Group":getgroup,"uploadtime":str_time})
    conn.db.photos.insert({"cnt_photoid": cnt_photo_id, "photoid": pic_no, "comments": comments,"uploadtime":str_time})
    cnt_photo_id=cnt_photo_id+1
    conn.close()

    return "Successfully"

'''@app.route('/upload',methods=['POST'])
def upload():
    conn = create_conn()
    files = request.files['file_upload']
    comments = str(request.values['comment'])
    with open(files.filename,'rb') as f:
        encoded_string = base64.b64encode(f.read())
    print encoded_string
    #num=conn.db.pictures.find_one({"username":session['user_name']},{"count":1,"_id":0})
    conn.db.users.insert_one({"username":session['user_name'],'image':encoded_string})
    conn.close()
    return "success"'''

'''@app.route('/retrieve',methods=['POST'])
def retrieve():
    conn=create_conn()
    data=conn.db.users.find()
    data1 = json.loads(json.dumps(data))
    img = data1[0]
    img1 = img['image']
    decode = img1.decode()
    img_tag = '<img alt="sample" src="data:image/png;base64,{0}">'.format(decode)
    return str(img_tag)'''


#Module for displaying pictures and associated content for all users
@app.route('/all_user_pics', methods=['POST'])
def show_photo():
    conn_db_time=datetime.datetime.now()
    x=int(request.values['number'])
    conn = create_conn()
    conn_db_end=datetime.datetime.now()
    conn_db_total=conn_db_end-conn_db_time
    mongoobj = conn.db
    fs = gridfs.GridFS(mongoobj)
    #info = conn.db.photos.find({}, {"cnt_photoid":1, "photoid":1, "comments":1,"Group":0,"uploadtime":0,"_id" :0}).limit(x)
    str_total_time = datetime.datetime.now()
    info = conn.db.photos.find({}, {"cnt_photoid": 1, "photoid": 1, "comments": 1, "_id": 0}).limit(x)
    data = defaultdict(list)
    for find in info:
        individual_time_str=datetime.datetime.now()
        ids = find["photoid"]
        name = find["cnt_photoid"]
        comments = find["comments"]
        individual_time_end=datetime.datetime.now()
        individual_total=individual_time_end-individual_time_str
        #getgroups= find["Group"]
        #times=find["uploadtime"]
        print ids,comments
        picdata = fs.get(ids).read()
        pic1 = "data:image/jpeg;base64," + base64.b64encode(picdata)
        lists=[]
        #lists.append(pic1)
        lists.append(comments)
        lists.append(individual_total)
        #lists.append(getgroups)
        #lists.append(times)
        data[name].append(lists)

    conn.close()
    end_total_time = datetime.datetime.now()
    total = end_total_time - str_total_time
    return render_template('photoview.html', data=data,total=total,dbtime=conn_db_total)

'''@app.route('/admin',methods=['POST'])
def admin():
    conn=create_conn()
    tag=request.form['tag']
    #res=conn.db.users.find_one({},{'_id',1})
    #id2=res['_id2']
    conn.db.users.update({'username':'admin'},{'tags':{"":tag}})
    conn.close()
    return render_template('new.html')'''



#Module for displaying the images of a specific user
@app.route('/view_only_user', methods=['POST'])
def show_my_photo():
    conn=create_conn()
    mongoobj=conn.db

    name = session["user_name"]

    info = conn.db.photos.find({"username":name},{"photoid" : 1,"comments":1, "_id":0})
    data = defaultdict(list)
    for find in info:
        ids = find["photoid"]
        comments = find["comments"]
        fs = gridfs.GridFS(mongoobj)
        picdata = fs.get(ids).read()
        pic1 = "data:image/jpeg;base64," + base64.b64encode(picdata)
        lists=[]
        lists.append(pic1)
        lists.append(comments)
        data[ids].append(lists)

    conn.close()

    return render_template('PersonalPics.html',data = data)

#Module for deleting pictures and associated content of that specific user
@app.route('/delete_photo',methods=['POST'])
def delete_photo():
    conn = create_conn()
    mongoobj = conn.db
    fs = gridfs.GridFS(mongoobj)
    picid = str(request.form['id'])
    pic_id = ObjectId(picid)

    name = session["user_name"]
    '''cnt = conn.db.photo_count.find_one({"username": name}, {"count": 1,"_id" :0})
    print cnt["count"]
    cnt1 = cnt["count"]-1
    conn.db.photo_count.update({"username": name}, {"$set": {"count": cnt1}})'''

    conn.db.photos.delete_one({"photoid" : pic_id})
    conn.db.fs.files.delete_one({"_id": pic_id})
    conn.db.fs.chunks.delete_one({"files_id": pic_id})

    conn.close()
    return "deleted"



if __name__ == '__main__':
    app.run()
