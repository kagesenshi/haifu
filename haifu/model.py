from tornado.web import Application as BaseApplication
from tornado.web import RequestHandler, addslash
from zope.component import getUtilitiesFor, getUtility
from haifu.interfaces import (IService, IFormatter, IJson, IRequest,
                              IFormatTransformable)
from zope.interface import implements, directlyProvides, alsoProvides
from zope import schema
import grokcore.component as grok
import inspect
import simplejson
import traceback
from haifu.exc import HTTPException
from haifu.decorator import (error_handler, formattransformer,
                            _preserve_argcount)
from haifu import schema as haifuschema
from haifu.event import RequestFinishingEvent, RequestStartingEvent
from zope.event import notify
import zope.component as zca

def httpexceptionhandler(func):
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except HTTPException, e:
            self.set_status(e.code)
            for k, v in e.headers:
                self.set_header(k, v)
            message = '%s: %s' % (e.code, e.message)
            result = Result(False, 999, message)
            self._transforms = []
            return result
        return result
    _preserve_argcount(wrapper, func)
    wrapper.func_name = func.func_name
    return wrapper

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
        self.request = IRequest(handler)

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


class Object(object):

    def __repr__(self):
        return 'Object of %s' % self.__schema__

def make_object(iface, data=None, baseclass=Object):
    data = data or {}
    defaults = {}

    for key, value in schema.getFields(iface).items():
        if isinstance(value, schema.List):
            defaults.setdefault(key, [])
        else:
            defaults.setdefault(key, value.default)

    defaults.update(data)

    obj = baseclass()

    directlyProvides(obj, iface)

    obj.__schema__ = iface
    for key, value in defaults.items():
        setattr(obj, key, value)

    return obj


def json_encoder(obj):
    iface = getattr(obj, '__schema__', None)
    if iface is None:
        return obj

    data = {}
    for key, field in schema.getFields(iface).items():
        value = getattr(obj, key)
        data[key] = value
    return data

def Result(success=True, statuscode=100, message=''):
    if success:
        status = 'ok'
    else:
        status = 'failed'
    obj = make_object(haifuschema.IResult, {
        'status': status,
        'statuscode': statuscode,
        'message': message
    })
    alsoProvides(obj, IFormatTransformable)
    return obj

def Config(**data):
    return make_object(haifuschema.IConfig, data)

def Person(**data):
    return make_object(haifuschema.IPerson, data)

def Attribute(data):
    return make_object(haifuschema.IAttribute, {'data': data})

def Activity(**data):
    return make_object(haifuschema.IActivity, data)
