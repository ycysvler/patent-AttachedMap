#coding=utf-8
import sys
import os,shutil
import cv2
import uuid
import time
import json
import numpy
import urllib
import threading
from multiprocessing import Process, Pipe
sys.path.append("./dll")

from IObjZoneDetect import ICartwheelZoneDetect
from flask import Flask,request ,Response
from flask_cors import CORS
app_conn, service_conn = Pipe()

R = threading.Lock()

def app_progress():
    app.run(debug=False,host='0.0.0.0', port=4001)

# 这里是一个单独的进程，用于计算特征
def caculator_progress(conn):
    model_dir = "/root/models"
    detector = ICartwheelZoneDetect(model_dir)
    print('model init complete!')
    # 下面是计算流程
    while True:
        imagepath = conn.recv()
        im = cv2.imread(imagepath)
        result = detector.detect(im)
        conn.send(result)

# 下面是Http处理部分
app = Flask(__name__)
CORS(app, resources=r'/*')
@app.route('/upload', methods=['POST'], strict_slashes=False)
def upload():
    try:
        img = request.files['image']
    except:
        img = None

    try:
        if img is None:
            return Response(json.dumps({"code":400, "error":"missing parameter [image]"}),mimetype='application/json')
        name = str(uuid.uuid1()) + ".jpg"
        path = "/root/cartwheel/temp/" + name
        path_error = "/root/cartwheel/error/" + name
        
        img.save(path)
        R.acquire()
        app_conn.send(path)
        result = app_conn.recv()
        R.release()
        data = {"code":500}
        if len(result) > 0:
            count = result[0]
            if count == 1:
                count = 2
            data = {"code":200, "data":{"count":count,"detail":result[1]}}
        
         
        os.remove(path)        
    except Exception as e:
        shutil.move(path, path_error)
        return Response(json.dumps({"code":500, "error":str(e)}), mimetype="application/json")
    else:
        return Response(json.dumps(data,cls=ComplexEncoder), mimetype='application/json')

@app.route('/path')
def caculator(): 
    image = request.args.get("image")
 
    if (image is None):
        return Response('missing parameter [image]', status=403)
    # 声明特征返回值
    result = None
    try:
        time_start = time.time() 
        # 计算特征值
        R.acquire()
        app_conn.send(image)
        time_vehicle_detect = time.time()
        result = app_conn.recv()  
        R.release()
    except(ex1):
        return Response(str(ex1), status=500)
    else: 
        print(result)
        return Response(json.dumps(result, cls=ComplexEncoder),mimetype='application/json')

# 用于json 序列化中处理numpy.float32类型
class ComplexEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, numpy.float32):
      return round(float(obj),4)
    else:
      return json.JSONEncoder.default(self, obj)

if __name__ == '__main__':
    process = Process(target=app_progress)
    # 启动计算集成等待努力工作
    process.start()
    caculator_progress(service_conn)
