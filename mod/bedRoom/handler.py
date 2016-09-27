#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-08-24 12:46:36
# @Author  : LiangJ

from config import *
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
import tornado.web
import tornado.gen
import json, base64
from BeautifulSoup import BeautifulSoup
import urllib
from time import time, localtime, strftime
import datetime
from ..auth.handler import authApi
from mod.auth.cookie import getCookie

class RoomHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    def get(self):
        self.write('Herald Web Service')

    def on_finish(self):
        self.db.close()
    
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        number = self.get_argument('cardnum',default=None)
        retjson = {'code':200, 'content':''}

        try:
            client = AsyncHTTPClient()
            response = getCookie(self.db, number,self.get_argument("password"))
            
            if response['code'] == 200:
                cookie = response['content']
                request = HTTPRequest(
                    URL,
                    method='GET',
                    headers={'Cookie': cookie},
                    request_timeout=TIME_OUT)
                response = yield tornado.gen.Task(client.fetch, request)
                soup = BeautifulSoup(response.body)
                table2 = soup.findAll('td')
                room = table2[9].text
                bed = table2[10].text
                retjson['code'] = 200
                retjson['content'] = {
                    'bed': bed,
                    'room': room
                }
            else:
                retjson['code'] = 401
        except Exception,e:
            retjson['code'] = 200
            retjson['content'] = {'bed': "",'room': ""}
        ret = json.dumps(retjson, ensure_ascii=False, indent=2)
        self.write(ret)
        self.finish()

        