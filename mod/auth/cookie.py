# -*- coding: utf-8 -*-
# @Date    : 2016-03-24 16 16:34:57
# @Author  : jerry.liangj@qq.com

import time,json
import urllib
from tornado.httpclient import HTTPRequest, HTTPClient,HTTPError
from sqlalchemy.orm.exc import NoResultFound
from config import *
from newHandler import newAuthApi
from handler import authApi
from mod.models.cache import cache


def getCookie(cardnum, card_pwd):
    state = 1
    ret = {'code':200,'content':''}
    try:
        result = cache[cardnum]
        ret['content'] = result
    except KeyError:
        _result = authApi(cardnum, card_pwd)
        if _result['code']==200:
            cookie = _result['content']
            ret['content'] = cookie
            cache[cardnum] = cookie
        else:
            ret['code'] = 500
            ret['content'] = 'error'
    return ret
