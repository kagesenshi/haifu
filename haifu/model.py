from tornado.web import Application as BaseApplication
from tornado.web import RequestHandler, addslash
from zope.component import getUtilitiesFor, getUtility
from haifu.interfaces import IService, IFormatter
from zope.interface import implements
import grokcore.component as grok
import inspect
import simplejson
import traceback
from haifu.exc import HTTPException
from haifu.decorator import (error_handler, formattransformer,
                                httpexceptionhandler)
from haifu.event import RequestFinishingEvent, RequestStartingEvent
from zope.event import notify
import zope.component as zca

class Application(BaseApplication):

    def __init__(self):
        handlers = []
        for name, util in getUtilitiesFor(IService):
            for pattern, handler in util.__handlers__():
                handlers.append((r'/' + name + pattern, handler))
        super(Application, self).__init__(handlers)

def handler_factory(cls, attr):
    func = getattr(cls, attr)
    method = getattr(func, '__haifu_method__', 'get')

    class Handler(RequestHandler):

        def prepare(self):
            notify(RequestStartingEvent(self))
            self._current_user = None

        def finish(self, *args, **kwargs):
            notify(RequestFinishingEvent(self))
            self._current_user = None
            return super(Handler, self).finish(*args, **kwargs)

        def get_current_user(self):
            return self._current_user

    def wrapper(self, *args, **kwargs):
        service = cls(self)
        return getattr(service, attr)(*args, **kwargs)

    setattr(Handler, method, 
        formattransformer(
            httpexceptionhandler(
                error_handler(
                    wrapper
                )
            )
        )
    )
    return Handler

class Service(grok.GlobalUtility):
    implements(IService)
    grok.direct()
    grok.baseclass()

    def __init__(self, handler):
        self.handler = handler
        self.request = handler.request

    @classmethod
    def __handlers__(cls):
        handlers = []
        for attr in dir(cls):
            if attr.startswith('_'):
                # dont include internal/private stuff
                continue

            func = getattr(cls, attr)

            if not getattr(func, 'func_name', False):
                # not a function, skip~~
                continue

            if attr == 'index':
                # index is the default page
                handlers.append((r'/?', handler_factory(cls, attr)))
                continue

            # always hook the function
            handlers.append(
                (r'/' + attr + r'/?', handler_factory(cls, attr)),
            )

            #if theres arguments, include em
            
            argcount = getattr(
                func, '__haifu_argcount__',
                len(inspect.getargs(func.func_code).args) - 1
            )
            if argcount > 0:
                handlers.append(
                    (r'/' + attr + r'/(.*)' * argcount + r'/?',
                    handler_factory(cls, attr))
                )
        return handlers
