from flask import Flask, request, abort
import requests
import json
from Project.Config import *
app = Flask(__name__)
import urlfetch
from linebot import LineBotApi
from flask import send_file
import PIL  
from PIL import Image
import io
from io import BytesIO
import tensorflow as tf
from tensorflow import keras
import numpy as np

line_bot_api = LineBotApi(Channel_access_token)
model = tf.keras.models.load_model(r"testep1000.model")
class_names = ['cbb', 'cbsd', 'cgm', 'cmd', 'healthy']
#['โรคใบไหม้ของมันสาปะหลัง', 'โรคแผลขีดสีน้ำตาลของมันสำปะหลัง', 'โรคไวรัสใบด่างของมันสาปะหลัง', 'โรคใบด่างของมันสำปะหลัง', 'ใบมันสำปะหลังสุขภาพดี']

@app.route('/webhook', methods=['POST','GET'])
def webhook():
    if request.method == 'POST':
        payload = request.json
        Reply_token = payload['events'][0]['replyToken']
        print(Reply_token)
        type = payload['events'][0]['message']['type']
        print("type=")
        print(type)
        print(payload['events'][0]['message']['id'])
        if type == 'image':
            Reply_messasge = 'ได้รับรูปแล้ว'
            ReplyMessage(Reply_token,Reply_messasge,Channel_access_token)
        elif type == 'text':
            message = payload['events'][0]['message']['text']
            if 'ทดสอบ' in message:
                Reply_messasge = 'ทดสอบรับข้อความ'
                ReplyMessage(Reply_token,Reply_messasge,Channel_access_token)
                
            else :
                Reply_messasge = 'ได้รับข้อความ'
                ReplyMessage(Reply_token,Reply_messasge,Channel_access_token)
        else :
            Reply_messasge = ''
            ReplyMessage(Reply_token,Reply_messasge,Channel_access_token)
        
        return request.json, 200

    elif request.method == 'GET' :
        return 'this is method GET!!!' , 200

    else:
        abort(400)


@app.route('/')
def hello():
    return 'hello webhook',200

@app.route('/image')
def urlimage():
    path = request.args.get('path')
    filename = f"saveimg\\{path}.jpg"
    return send_file(filename, mimetype='image/jpg'),200

def getImage(message_id,Line_Acees_Token):
    LINE_API = 'https://api-data.line.me/v2/bot/message/'+message_id+'/content'
    print(LINE_API)
    Authorization = 'Bearer {}'.format(Line_Acees_Token) ##ที่ยาวๆ
    data = urlfetch.get(LINE_API, headers = {'Authorization':Authorization})
    img_list =  [i for i in data]
    img = img_list[0]
    for i in img_list[1:]:
        img+=i

    print(len(img))

    img_PLT_jpeg = Image.open(io.BytesIO(img))
    b = BytesIO()
    img_1 = img_PLT_jpeg.convert('RGB')

    img_2 = img_PLT_jpeg.resize((180, 180), Image.ANTIALIAS)
    
    img_3 = img_2.convert('RGB')
    img_3.save(b,format='jpeg')

    img_array = keras.preprocessing.image.img_to_array(img_3)
    img_array = tf.expand_dims(img_array, 0)
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    img_1.save(f'Project\\saveimg\\{class_names[np.argmax(score)]}_{message_id}.jpg')

    return class_names[np.argmax(score)]

def ReplyMessage(Reply_token, TextMessage, Line_Acees_Token):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'

    Authorization = 'Bearer {}'.format(Line_Acees_Token) ##ที่ยาวๆ
    print(Authorization)
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization':Authorization
    }
    payload = request.json
    if (payload['events'][0]['message']['type']=='image'):
        predict = getImage(payload['events'][0]['message']['id'],Channel_access_token)
        respon=""
        if predict == 'cbb':
            respon = (f"ภาพนี้น่าจะเป็นภาพของโรคใบไหม้ของมันสำปะหลัง")
        elif predict == 'cbsd':
            respon = (f"ภาพนี้น่าจะเป็นภาพของโรคแผลขีดสีน้ำตาลของมันสำปะหลัง")
        elif predict == 'cgm':
            respon = (f"ภาพนี้น่าจะเป็นภาพของโรคไวรัสใบด่างของมันสำปะหลัง")
        elif predict == 'cmd':
            respon = (f"ภาพนี้น่าจะเป็นภาพของโรคใบด่างของมันสำปะหลัง")
        elif predict == 'healthy':
            respon = (f"ภาพนี้น่าจะเป็นภาพของใบมันสำปะหลังสุขภาพดี")
        
        url = (f"https://4cdd-27-55-71-55.jp.ngrok.io/image?path={predict}_{payload['events'][0]['message']['id']}")
        print(url)
        data = {
            "replyToken":Reply_token,
            "messages":[{
                "type":"text",
                "text":TextMessage+'\n'+"บันทึกเรียบร้อย\n"+respon
            }]
        }
    
    elif (payload['events'][0]['message']['type']=='text'):
        data = {
            "replyToken":Reply_token,
            "messages":[{
                "type":"text",
                "text":TextMessage
            }]
        }

    else:
        data = {
            "replyToken":Reply_token,
            "messages":[{
                "type":"text",
                "text":"ได้รับบางอย่างจากผู้ใช้"
            }]
        }

    data = json.dumps(data) ## dump dict >> Json Object
    r = requests.post(LINE_API, headers=headers, data=data) 
    return 200