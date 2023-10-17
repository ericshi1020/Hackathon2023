import os
import threading
import webbrowser

from flask import Flask, request
from flask_cors import CORS, cross_origin
from application.application_start import user
from facerecognition_opencv import face_detection
from flask_socketio import SocketIO, emit
from application.tts_ws_python3_xunfei import Ws_Param, pcm2wav
import base64
import json
import os
import ssl
import _thread as thread
import websocket
from time import sleep

app = Flask(__name__)
socketio = SocketIO(app)
app.register_blueprint(user)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'application/json'
webbrowser.get('chrome')


# conn = sqlite3.connect('test.db')
# conn.row_factory = dict_factory
# cursor = conn.cursor()

# cursor.rowcount
# 提交事务:
# conn.commit()

def startApplication():
    socketio.run(app, port=2020, host="127.0.0.1", debug=False)
    # startapp.startApp(personInfo)

def getRecent3sPersonInit():
    sleep(3.5)
    personId = face_detection.getRecent3sUser()
    print(personId)

    webbrowser.open_new('http://localhost:2020/' + str(personId))

@app.route('/generatevoice')
def generateVoice():
    text = request.args.get("text")

    def on_message(ws, message):
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            print(message)
            if status == 2:
                print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:

                with open('./demo.pcm', 'ab') as f:
                    f.write(audio)

        except Exception as e:
            print("receive msg,but parse exception:", e)

    # 收到websocket错误的处理
    def on_error(ws, error):
        print("### error:", error)

    # 收到websocket关闭的处理
    def on_close(ws):
        print("### closed ###")

    # 收到websocket连接建立的处理
    def on_open(ws):
        def run(*args):
            d = {"common": wsParam.CommonArgs,
                 "business": wsParam.BusinessArgs,
                 "data": wsParam.Data,
                 }
            d = json.dumps(d)
            print("------>开始发送文本数据")
            ws.send(d)
            if os.path.exists('./demo.pcm'):
                os.remove('./demo.pcm')

        thread.start_new_thread(run, ())

    print("receive request generate voice: " + text + "!!!")
    # 测试时候在此处正确填写相关信息即可运行
    wsParam = Ws_Param(APPID='8608c97f', APISecret='MzAzYTY5MjJmZWQ0MmM1YjIwODBiNGRi',
                       APIKey='b30ba135f89c685f97e2745fea6253b9',
                       Text=text)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    pcm2wav("demo.pcm", text + ".wav")
    socketio.emit('response_data',
                  {'data': "data", 'count': 1},
                  namespace='/test_conn')
    return "success"


@socketio.on("test_conn")
def message(msg):
    print("message", msg)


if __name__ == '__main__':
    t1 = threading.Thread(target=startApplication)
    t1.start()

    t2 = threading.Thread(target=getRecent3sPersonInit)
    t2.start()

    current_path = os.path.dirname(__file__)

    face_detection.faceRecognition(current_path)

