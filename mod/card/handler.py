# -*- coding: utf-8 -*-
#!/usr/bin/env python
# @Date    : 2014-10-26 12:46:36
# @Author  : yml_bright@163.com

from config import *
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from BeautifulSoup import BeautifulSoup
from time import time
import tornado.web
import tornado.gen
import urllib, re
import json, base64
import datetime
import traceback
from ..auth.handler import authApi
from mod.auth.cookie import getCookie

class CARDHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('Herald Web Service')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        timedelta = int(self.get_argument('timedelta', default=0))
        cardnum = self.get_argument('cardnum')
        cardnum_with_delta = cardnum + str(timedelta)
        data = {
            'Login.Token1':cardnum,
            'Login.Token2':self.get_argument('password'),
        }
        retjson = {'code':200, 'content':''}
        try:
            client = AsyncHTTPClient()
            response = getCookie(cardnum, self.get_argument('password'))
            if response['code']==200:
                cookie = response['content']
                request = HTTPRequest(
                    LOGIN_URL,
                    method='GET',
                    headers={'Cookie':cookie},
                    request_timeout=TIME_OUT)
                response = yield tornado.gen.Task(client.fetch, request)
                cookie += ';' + response.headers['Set-Cookie'].split(';')[0]
                request = HTTPRequest(
                    USERID_URL,
                    method='GET',
                    headers={'Cookie':cookie},
                    request_timeout=TIME_OUT)
                response = yield tornado.gen.Task(client.fetch, request)

                soup = BeautifulSoup(response.body)
                td = soup.findAll('td',{"class": "neiwen"})
                userid = td[3].text
                cardState = td[42].text
                cardLetf = td[46].text.encode('utf-8').split('元')[0]
                # do not need to get the detail
                if timedelta == 0:
                    retjson['content'] = {'state':cardState, 'left':cardLetf}
                    ret = json.dumps(retjson, ensure_ascii=False, indent=2)
                    self.write(retjson)
                    self.finish()
                    return
                #get today detail
                elif timedelta == 1:
                    data = {
                        'account':userid,
                        'inputObject':"all",
                    }
                    request = HTTPRequest(
                        TODAYDATA_URL,
                        method='POST',
                        body=urllib.urlencode(data),
                        headers={'Cookie':cookie},
                        request_timeout=TIME_OUT
                    )
                    response = yield tornado.gen.Task(client.fetch, request)
                    soup = BeautifulSoup(response.body)
                    tr = soup.findAll('tr',{"class": re.compile("listbg")})
                    detail=[]
                    for td in tr:
                            td = td.findChildren()
                            tmp = {}
                            tmp['date'] = td[0].text
                            tmp['type'] = td[3].text.encode('ISO-8859-1').decode('gbk')
                            tmp['system'] = td[4].text.encode('ISO-8859-1').decode('gbk')
                            tmp['price'] = td[5].text
                            tmp['left'] = td[6].text
                            detail.append(tmp)
                    retjson['content'] = {'state':cardState,'left':cardLetf,'detial':detail}
                #get other days detail depend on timedelta
                else:
                    request = HTTPRequest(
                        INIT_URL,
                        method='GET',
                        headers={'Cookie':cookie},
                        request_timeout=TIME_OUT)
                    response = yield tornado.gen.Task(client.fetch, request)
                    soup = BeautifulSoup(response.body)
                    __continue = soup.findAll('form',{'id':'accounthisTrjn1'})[0]['action']

                    now = datetime.datetime.now()
                    delta = datetime.timedelta(timedelta)
                    page = 1
                    data = {
                        'account':userid,
                        'inputObject':'all',
                        'inputStartDate':(now - delta).strftime('%Y%m%d'),
                        'inputEndDate':now.strftime('%Y%m%d'),
                        'pageNum':page
                    }
                    request = HTTPRequest(
                        INDEX_URL+__continue,
                        method='POST',
                        headers={'Cookie':cookie},
                        body=urllib.urlencode(data),
                        request_timeout=TIME_OUT)
                    response = yield tornado.gen.Task(client.fetch, request)
                    soup = BeautifulSoup(response.body)
                    __continue = soup.findAll('form',{'id':'accounthisTrjn2'})[0]['action']
                    request = HTTPRequest(
                        INDEX_URL+__continue,
                        method='POST',
                        headers={'Cookie':cookie},
                        body=urllib.urlencode(data),
                        request_timeout=TIME_OUT)
                    response = yield tornado.gen.Task(client.fetch, request)
                    soup = BeautifulSoup(response.body)
                    __continue = 'accounthisTrjn3.action'
                    request = HTTPRequest(
                        INDEX_URL+__continue,
                        method='POST',
                        headers={'Cookie':cookie},
                        body=urllib.urlencode(data),
                        request_timeout=TIME_OUT)
                    response = yield tornado.gen.Task(client.fetch, request)
                    soup = BeautifulSoup(response.body)
                    detial = []
                    count = 0
                    while 1:
                        tr = soup.findAll('tr',{"class": re.compile("listbg")})
                        if not tr:
                            break
                        for td in tr:
                            td = td.findChildren()
                            tmp = {}
                            tmp['date'] = td[0].text
                            tmp['type'] = td[3].text.encode('ISO-8859-1').decode('gbk')
                            tmp['system'] = td[4].text.encode('ISO-8859-1').decode('gbk')
                            tmp['price'] = td[5].text
                            tmp['left'] = td[6].text
                            if(tmp['type']==u'扣款'):
                                tmp['type'] = u'水电扣费'
                            detial.append(tmp)
                        page += 1
                        data['pageNum'] = page
                        request = HTTPRequest(
                            DATA_URL,
                            method='POST',
                            headers={'Cookie':cookie},
                            body=urllib.urlencode(data),
                            request_timeout=TIME_OUT)
                        response = yield tornado.gen.Task(client.fetch, request)
                        soup = BeautifulSoup(response.body)
                    retjson['content'] = {'state':cardState, 'left':cardLetf, 'detial':detial}
            else:
                retjson['code'] = 401
                retjson['content'] = 'wrong card number or password'
        except Exception as e:
            retjson['code'] = 500
            retjson['content'] = str(e)
            print(traceback.print_exc())
        self.write(json.dumps(retjson, ensure_ascii=False, indent=2))
        self.finish()
