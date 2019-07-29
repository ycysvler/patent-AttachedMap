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

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=4110)