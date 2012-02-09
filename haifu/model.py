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


class BaseHandler(RequestHandler):

    def prepare(self):
        notify(RequestStartingEvent(self))
        self._current_user = None

    def finish(self, *args, **kwargs):
        notify(RequestFinishingEvent(self))
        self._current_user = None
        return super(BaseHandler, self).finish(*args, **kwargs)

    def get_current_user(self):
        return self._current_user


class HandlerRegistry(object):

    def __init__(self):
        self.registry = {}

    def append(self, pattern, cls, attr):
        if pattern in self.registry:
            handler = self.registry[pattern]
            self._hook_method_handler(handler, cls, attr)
        else:
            handler = type('Handler', (BaseHandler,), {})
            self._hook_method_handler(handler, cls, attr)
            self.registry[pattern] = handler

    def _hook_method_handler(self, handler, cls, attr):
        func = getattr(cls, attr)
        method = getattr(func, '__haifu_method__', 'get')
        def wrapper(self, *args, **kwargs):
            service = cls(self)
            return getattr(service, attr)(*args, **kwargs)
        setattr(handler, method, 
            formattransformer(
                httpexceptionhandler(
                    error_handler(
                        wrapper
                    )
                )
            )
        )

    def items(self):
        return self.registry.items()

class Service(grok.GlobalUtility):
    implements(IService)
    grok.direct()
    grok.baseclass()

    def __init__(self, handler):
        self.handler = handler
        self.request = handler.request

    @classmethod
    def __handlers__(cls):
        handlers = HandlerRegistry()
        for attr in dir(cls):
            if attr.startswith('_'):
                # dont include internal/private stuff
                continue

            func = getattr(cls, attr)

            if not getattr(func, 'func_name', False):
                # not a function, skip~~
                continue

            prefix = func.func_name

            if prefix == 'index':
                # index is the default page
                prefix = r''
            else:
                prefix = r'/' + prefix

            # always hook the function
            handlers.append(prefix + r'/?', cls, attr)

            #if theres arguments, include em
            
            argcount = getattr(
                func, '__haifu_argcount__',
                len(inspect.getargs(func.func_code).args) - 1
            )
            if argcount > 0:
                handlers.append(
                    prefix + r'/(.*?)' * argcount + r'/?',
                    cls, attr
                )
        return handlers.items()
