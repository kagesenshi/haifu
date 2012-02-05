from tornado.web import Application as BaseApplication
from tornado.web import RequestHandler, addslash
from zope.component import getUtilitiesFor, getUtility
from haifu.interfaces import IService, IFormatter
from zope.interface import implements
import grokcore.component as grok
import inspect
import simplejson
import traceback
from haifu.basicauth import require_basic_auth
from haifu.exc import HTTPException
from haifu.decorator import (error_handler, formattransformer,
                                httpexceptionhandler)

class Application(BaseApplication):

    def __init__(self):
        handlers = []
        for name, util in getUtilitiesFor(IService):
            for pattern, handler in util.__handlers__():
                handlers.append((r'/' + name + pattern, handler))
        super(Application, self).__init__(handlers)

def handler_factory(func):
    method = getattr(func, '__haifu_method__', 'get')

    class Handler(RequestHandler):
        pass

    setattr(Handler, method, 
        formattransformer(
            httpexceptionhandler(
                error_handler(
                    func.im_func
                )
            )
        )
    )
    return Handler

class Service(grok.GlobalUtility):
    implements(IService)
    grok.direct()
    grok.baseclass()

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

            if func.func_name == 'index':
                # index is the default page
                handlers.append((r'/?', handler_factory(func)))
                continue

            # always hook the function
            handlers.append(
                (r'/' + attr + r'/?', handler_factory(func)),
            )

            #if theres arguments, include em
            argcount = len(inspect.getargs(func.func_code).args) - 1
            if argcount > 0:
                handlers.append(
                    (r'/' + attr + r'/(.*)' * argcount + r'/?',
                    handler_factory(func))
                )
        return handlers
