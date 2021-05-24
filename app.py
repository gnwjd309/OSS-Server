from flask import Flask, Response, send_file, request, jsonify
import mysql.connector
import sys
import json
import socket
from requests import get
import Sentiment_analysis
import threading
import time
import TTS
import scipy.io.wavfile as swavfile
app = Flask(__name__)
from os import system

class Worker(threading.Thread):

    def __init__(self, name):
        super().__init__()
        self.name = name            # thread 이름 지정

    def run(self):
        while(1):
            system("python Operation.py")
            time.sleep(120)

@app.route('/userLogin', methods = ['GET', 'POST'])
def chat():
    msg_received = request.get_json()
    msg_subject = msg_received["subject"]

    if msg_subject == "register":
        return register(msg_received)
    elif msg_subject == "login":
        return login(msg_received)
    else:
        return "Invalid request."

def register(msg_received):
    id = msg_received["id"]
    name = msg_received["name"]
    pw = msg_received["pw"]

    select_query = "SELECT * FROM users where id = " + "'" + id + "'"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()
    if len(records) != 0:
        return "Another user used the username. Please chose another username."

    insert_query = "INSERT INTO users (id,name,pw) VALUES (%s,%s,MD5(%s))"
    insert_values = (id,name,pw)
    try:
        db_cursor.execute(insert_query, insert_values)
        chat_db.commit()
        sql="CREATE TABLE "+id+"(title VARCHAR(255) NOT NULL, content VARCHAR(255) NOT NULL,summary VARCHAR(255) NOT NULL,keyword VARCHAR(255) NOT NULL,sentiment VARCHAR(255) NOT NULL, registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)default character set utf8 collate utf8_general_ci"
        db_cursor.execute(sql)
        chat_db.commit()
        return "success"
    except Exception as e:
        print("Error while inserting the new record :", repr(e))
        return "failure"

def login(msg_received):
    id= msg_received["id"]
    pw = msg_received["pw"]

    select_query = "SELECT name FROM users where id = " + "'" + id + "' and pw = " + "MD5('" + pw + "')"
    db_cursor.execute(select_query)
    records = db_cursor.fetchall()

    if len(records) == 0:
        return "failure"
    else:
        return "success"
try:
    chat_db = mysql.connector.connect(host="localhost", user="root", passwd="0000", database="user",charset='utf8')
except:
    sys.exit("Error connecting to the database. Please check your inputs.")
db_cursor = chat_db.cursor()

@app.route('/ai', methods = ['GET', 'POST'])
def ai():
    msg_received = request.get_json()
    print(msg_received)
    msg = msg_received["msg"]
    path = msg_received["path"]
    arr=path.split('/')
    if "읽어" in msg :
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return "http://%s:%s/audio/%s/%s"% (get("https://api.ipify.org").text, PORT,arr[1],arr[2])
    elif "요약" in msg :
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return "http://%s:%s/summary/%s/%s" % (get("https://api.ipify.org").text, PORT, arr[1],arr[2])
    else:
        return "fail"

@app.route('/audio/<category>/<audionum>')
def streamwav(category,audionum):
    print(audionum)
    print(category)
    def generate(category,audionum):
        with open("news/%s/%s.wav" %(category,audionum), "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(category,audionum), mimetype="audio/x-wav")

@app.route('/summary/<category>/<audionum>')
def streamsummary(category,audionum):
    print(audionum)
    print(category)
    def generate(category,audionum):
        with open("summary/%s/%s.wav" %(category,audionum), "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
    return Response(generate(category,audionum), mimetype="audio/x-wav")


@app.route('/insert/<id>', methods=['POST', 'GET'])

def insert(id):
    msg_received = request.get_json()
    title = msg_received["title"]
    content = msg_received["content"]
    summary, keyword, sentiment = Sentiment_analysis.data(content)
    insert_query = "INSERT INTO "+id+" (title,content,summary, keyword, sentiment) VALUES (%s,%s,%s,%s,%s)"
    insert_values = (title, content,','.join(summary),','.join(keyword),','.join(sentiment))
    try:
        db_cursor.execute(insert_query, insert_values)
        chat_db.commit()
        return "success"
    except Exception as e:
        print("Error while inserting the new record :", repr(e))
        return "failure"

@app.route('/getdata/<id>', methods=['POST', 'GET'])

def getdata(id):

    insert_query = "SELECT * FROM user."+id
    try:
        db_cursor.execute(insert_query)
        result=db_cursor.fetchall()
        sum_result_string=""
        for i in result:
            title, content, summary , keyword , sentiment , date = i
            date= date.strftime('%Y-%m-%d %H:%M:%S')
            result_string="{{"+title+"//"+content+"//"+summary+"//"+keyword+"//"+sentiment+"//"+date+"}}"
            sum_result_string+=result_string
        return sum_result_string
    except Exception as e:
        print("Error while inserting the new record :", repr(e))
        return "failure"
@app.route('/tts/<content>')
def tts(content):
    audio = TTS.tts(content)
    swavfile.write("audio.wav", 22050, data=audio.numpy())
    return send_file("audio.wav")
t = Worker("Crawl")  # sub thread 생성
t.start() #크롤릴 코드 주석처리하면 실행 안됨
if __name__ == '__main__':
    PORT = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        print('[*] Open http://%s:%s on your browser ' % (s.getsockname()[0], PORT))
    app.run(host='0.0.0.0', port=PORT)


