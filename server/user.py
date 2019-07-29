# coding=UTF-8
# -*- coding: UTF-8 -*-

'''
这是用于导入机器人的脚本
# initRobot         从一个文本文件，导入机器人名字到 robot.robot 表
# initAvatar        从一个目录，导入头像图片到七牛，并保存数据到 robot.avatar 表
# robotToUser       从机器人表，向用户表导入机器人
# clearUserByRobot  根据机器人表，清理用户表里面的机器人
'''

import sys
import mongodb
import bson.binary
import config
import time
import os
import datetime
import argparse
import uuid
import time
from bson import ObjectId
from qiniu import Auth, put_file, etag
import qiniu.config

#reload(sys)
#sys.setdefaultencoding('utf-8')

# pip3 install pymongo
# pip3 install qiniu

# 从文件导入机器人名字
def initRobot(base, gender=1):
    f = open(base,"r")      # 设置文件对象
    data = f.readlines()    # 直接将文件中按行读到list里，效果与方法2一样
    f.close()               # 关闭文件

    robots = mongodb.db('robot').robot

    i = 1
    for name in data:
        item = {}
        item['fullName'] = name.replace('\n','')
        item['gender'] = gender
        item['portalId'] = None
        item['userId'] = None
        item['avatar'] = None
        robots.insert(item)
        print i,'\t',item['fullName']
        i=i+1
    return None

# 遍历目录，上传头像
def initAvatar(base, gender=1):
    images = os.listdir(base)

    count = len(images)

    i = 1

    avatars = mongodb.db('robot').avatar

    # 遍历文件目录
    for name in images:
        filename = os.path.join(base, name)

        if os.path.isfile(filename):
            # 获取七牛地址
            path = qiniuUploadImage(filename)
            item = {}
            item['path'] = path
            item['gender'] = gender
            item['name'] = name
            avatars.insert(item)
            print ' ' + str(i) + '/' + str(count),'\t', path,'\t', name
        i=i+1

# 上传图片到七牛，返回文件地址
def qiniuUploadImage(filename):
    #需要填写你的 Access Key 和 Secret Key
    access_key = config.qiniu['accessKey']
    secret_key = config.qiniu['secretKey']
    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = config.qiniu['bucket']
    #上传后保存的文件名
    key = 'image/' + str(uuid.uuid1()).replace('-','') + os.path.splitext(filename)[1]
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    #要上传文件的本地路径
    localfile = filename
    ret, info = put_file(token, key, localfile)
    if info.exception == None:
        return bucket_name + "://" + key
    else:
        return None

def robotToKol(portalId):

    robots = list(mongodb.db('robot').robot.find({"userId":{"$ne":None}}))
    count = len(robots)     # 一共有多少个机器人

    print '\033[0;30;44m','从机器人表导入kol:',portalId, count,'\033[0m'

    i = 0
    while i < len(robots):
        # 机器人数据
        robot = robots[i]
        # 用户数据
        user = {}
        user['userId'] = robot['userId']
        user['portalId'] = ObjectId(portalId)
        user['createTime'] = datetime.datetime.utcnow()
        # 插入用户数据
        u = mongodb.db('vision').portal_user.insert(user)
        print str(i) + '/' + str(count), '\t', 'ID:',u,'\t','createTime:', user['createTime']
        i = i+1
    print ' 本次导入KOL:', i

# 从机器人导入用户
def robotToUser(gender=1):
    print '\033[0;30;44m','从机器人表导入用户，性别:',gender,'\033[0m'

    avatars = list(mongodb.db('robot').avatar.find({"gender":gender}))
    robots = list(mongodb.db('robot').robot.find({"gender":gender, "userId":None}))

    count = len(robots)     # 一共有多少个机器人

    i = 0
    while i < len(robots):
        # 机器人数据
        robot = robots[i]
        # 用户数据
        user = {}

        if i < len(avatars):
            user['avatar'] = avatars[i]['path']

        user['fullName'] = robot['fullName']
        user['gender'] = robot['gender']
        user['favoriteCount'] = 0
        user['createTime'] = datetime.datetime.utcnow()
        # 插入用户数据
        u = mongodb.db('vision').user.insert(user)
        print str(i) + '/' + str(count), '\t', 'ID:',u,'\t','gender:', user['gender'], '\t', 'createTime:', user['createTime'], '\t', 'fullName:',user['fullName']
        # 将用户ID回写到机器人表
        mongodb.db('robot').robot.update({"_id":ObjectId(robot["_id"])}, {"$set":{"userId":u}})

        i = i+1

    print ' 本次导入机器人:', i

# 清除机器人
def clearUserByRobot():
    print '\033[0;30;44m','清除机器人','\033[0m'

    robots = list(mongodb.db('robot').robot.find({"userId":{"$ne":None}}))

    count = len(robots)     # 一共有多少个机器人

    i=1
    for robot in robots:
        userId = robot['userId']
        if userId != None:
            # 删用户
            mongodb.db('vision').user.remove({"_id":userId})
            # 清理关注关系
            mongodb.db('vision').user_follow.remove({"userId":userId})
            mongodb.db('vision').user_follow.remove({"follow":userId})
            mongodb.db('vision').portal_user.remove({"userId":userId})
            mongodb.db('vision').geo_favorite.remove({"follow":userId})
            mongodb.db('vision').video.remove({"userId":userId})
            print str(i) + '/' + str(count), '\t','ID:',userId,'\t', 'fullName:',robot['fullName']
            # 将用户ID回写到机器人表
            mongodb.db('robot').robot.update_one({"_id":ObjectId(robot["_id"])}, {"$set":{"userId":None}})
            i=i+1



if __name__ == '__main__':
    type = ''    # 启动参数

    while(type != 'exit'):
        print '\33[33m','robot  <file> <gender>' ,':','\t', '从file导入robot数据', '\033[0m'
        print '\33[33m','avatar <path> <gender>' ,':','\t', '从目录导入头像', '\033[0m'
        print '\33[33m','rtu    <gender>       ' ,':','\t', '从robot导入用户', '\033[0m'
        print '\33[33m','kol    <portalId>     ' ,':','\t', '从robot生成Kol,绑定到portalId企业', '\033[0m'
        print '\33[33m','clear                 ' ,':','\t', '根据robot清理用户', '\033[0m'
        print '\33[33m','exit                  ' ,':','\t', '退出程序', '\033[0m'

        line = raw_input()   # 读用户输入 python3.x 用 input()
        print 'line', line
        args = line.split(' ')

        type = args[0]

        if type == 'exit':
            print '青山不改，绿水长流，古德拜'

        elif type == 'clear':
            # 从用户表里面删除机器人
            clearUserByRobot()

        elif type == 'kol':
            if len(args) < 1:
                print '\033[0;31m参数数量不对\033[0m'

            else:
                portalId = args[1]          # 企业ID ﻿ObjectId("5c89c9caf67fd0829471c7b3")
                robotToKol(portalId)        # 将机器人绑定给超管企业，当KOL


        elif type == 'rtu':
            # 性别
            gender = 1
            if len(args) > 1:
                gender = int(args[1])
            # 从机器人表导入用户
            robotToUser(gender)

        elif type == 'avatar':
            if len(args) < 2:
                print '\033[0;31m参数数量不对\033[0m'

            else:
                path = args[1]              # 地址 '/Users/ycysvler/Pictures/test'
                gender = int(args[2])       # 性别
                initAvatar(path, gender)    # 将目录xxx，图片写入七牛，记录avatar资源表

        elif type == 'robot':
            if len(args) < 2:
                print '\033[0;31m参数数量不对\033[0m'

            else:
                path = args[1]              # 地址 '/Users/ycysvler/Documents/nan.txt'
                gender = int(args[2])       # 性别
                initRobot(path, gender)     # 将文件中机器人数据写入数据库

        else:
            print '\033[0;31m','未知命令类型:[',type,']\033[0m'

        print ' '








