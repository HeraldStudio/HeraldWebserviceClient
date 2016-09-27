# -*- coding: utf-8 -*-
# @Date    : 2014-06-25 15:43:36
# @Author  : xindervella@gamil.com yml_bright@163.com
from sqlalchemy.orm import scoped_session, sessionmaker
from mod.models.db import engine
from mod.gpa.gpa_handler import GPAHandler
from mod.pe.pedetailHandler import pedetailHandler
from mod.srtp.srtp_handler import SRTPHandler
from mod.card.handler import CARDHandler
from mod.nic.handler import NICHandler
from mod.lecture.handler import LectureHandler
from mod.library.listhandler import LibListHandler
from mod.phylab.handler import PhylabHandler
from mod.bedRoom.handler import RoomHandler
from mod.exam.handler import ExamHandler
import tornado.web
import tornado.ioloop
import tornado.options

from tornado.options import define, options
define('port', default=7000, help='run on the given port', type=int)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'/crawler/srtp', SRTPHandler),
            (r'/crawler/gpa', GPAHandler),
            (r'/crawler/pedetail', pedetailHandler),
            (r'/crawler/nic', NICHandler),
            (r'/crawler/card', CARDHandler),
            (r'/crawler/lecture', LectureHandler),
            (r'/crawler/library', LibListHandler),
            (r'/crawler/phylab',PhylabHandler),
            (r'/crawler/room',RoomHandler),
            (r'/crawler/exam',ExamHandler),
        ]
        settings = dict(
            cookie_secret="7CA71A57B571B5AEAC5E64C6042415DE",
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = scoped_session(sessionmaker(bind=engine,
                                              autocommit=False, autoflush=True,
                                              expire_on_commit=False))

if __name__ == '__main__':
    tornado.options.parse_command_line()
    Application().listen(options.port, address='127.0.0.1')
    tornado.ioloop.IOLoop.instance().start()
