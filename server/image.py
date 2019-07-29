# coding=UTF-8
# -*- coding: UTF-8 -*-


import sys
import mongodb
import bson.binary
import config
import time
import os
import datetime
import time
from bson import ObjectId

# pip3 install pymongo

class ImageDAO:
    def __init__(self):
        self.db = mongodb.db()

    '''
    按名称查找图片
    '''
    def SingleByName(self, name):
        item = self.db.image.find_one({"name":name}, {"name":1})
        print(item)

    '''
    按序号查找图片
    '''
    def SingleByIndex(self, index):
        item = self.db.image.find_one({"index":index}, {"name":1})
        print(item)

    '''
    图片数据写入数据库
    '''
    def Insert(self, name, code, type, state, source, feature, index):
        item = {}
        item['name'] = name.replace('\n','')
        item['code'] = code
        item['type'] = type
        item['state'] = state
        item['source'] = source
        item['feature'] = feature
        item['index'] = index
        item['createtime'] = datetime.datetime.utcnow()
        return self.images.insert_one(item)

    '''
    读取图片数据
    '''
    def __readImageBinary(self, path):
        file = open(path, 'rb')
        data = file.read()
        file.close()
        return data

    '''
    图片写文件
    '''
    def __writeImageFile(self, path, data):
        file = open(path, 'wb')
        file.write(data)
        file.close()

    def Insert_Test(self):
        filesname = "/Users/ycysvler/Downloads/WX20190704-122440.png"
        #datatmp = open(filesname, 'rb')
        data=self.__readImageBinary(filesname)
        result = self.Insert("a.jpg","pab","-17", 0, data, "" , 1)
        #datatmp.close()
        print(result)

    def Find(self, id):
        images = mongodb.db().image
        item = images.find_one({"_id":ObjectId(id)})
        filesname = "/Users/ycysvler/Downloads/111-111.png"
        datatmp = open(filesname, 'wb')
        datatmp.write(item['source'])
        datatmp.close()
        print('complete')



if __name__ == '__main__':
    x = ImageDAO()

    x.SingleByIndex(13)
    #x.Find("5d3ec0aad1bd6bd9de418d8f")








