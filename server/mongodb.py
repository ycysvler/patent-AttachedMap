#!/usr/bin/python
# -*- coding: UTF-8 -*-
from pymongo import MongoClient
import config

# "mongodb://root:root@127.0.0.1:27017/"
client = MongoClient(config.mongodb['host'], config.mongodb['port'])
#database = client['admin']
#database.authenticate(config.mongodb['user'],config.mongodb['passwd'])

def db(name='patentdb'):
	return client[name]