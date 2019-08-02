#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pip install flask
# pip install flask-cors
# pip install flask_script
# pip3 install requests
# python app.py runserver  -p 8000 -d -r --thread : 使用8000端口，开启debug调试模式，自动重启，使用多线程。

# pip install gunicorn
#  gunicorn -w 4 -b 127.0.0.1:4000 versions:app

import os
import sys
import uuid
import zipfile
import requests
import json
import subprocess
import hashlib

from flask import Flask, abort, request,jsonify,render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources=r'/*')

@app.route('/')
def index():
    return jsonify({"code":200})

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
        path = "./static/images/" + name
        img.save(path)
    except Exception as e:
        jsonify({"code":200})
    else:
        return jsonify({"code":200})


if __name__ == "__main__":
    print('''
███████╗███████╗███████╗ ██████╗ ██████╗      ██╗███████╗ ██████╗████████╗
██╔════╝██╔════╝██╔════╝██╔═══██╗██╔══██╗     ██║██╔════╝██╔════╝╚══██╔══╝
███████╗█████╗  █████╗  ██║   ██║██████╔╝     ██║█████╗  ██║        ██║
╚════██║██╔══╝  ██╔══╝  ██║   ██║██╔══██╗██   ██║██╔══╝  ██║        ██║
███████║███████╗███████╗╚██████╔╝██████╔╝╚█████╔╝███████╗╚██████╗   ██║
╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝\n''')
    app.run(host='0.0.0.0',port=4110)