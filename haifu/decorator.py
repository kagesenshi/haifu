from haifu.exc import HTTPException, Unauthorized, InternalError
from zope.component import getUtility, getUtilitiesFor
from haifu.interfaces import (IService, IFormatter, IAuthService,
                              IFormatTransformable)
from haifu import util
import traceback
import base64
from tornado.escape import xhtml_escape
import inspect

def _preserve_argcount(decorator, func):
    argcount = getattr(func, '__haifu_argcount__', 
        len(inspect.getargs(func.func_code).args) - 1)
    decorator.__haifu_argcount__ = argcount


def method(method='get'):
    """ decorator to set the method of the function """
    def wrapper(func):
        func.__haifu_method__ = method
        return func
    return wrapper


def error_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception, e:
            if isinstance(e, HTTPException):
                raise e
            error = InternalError()
            error.message = xhtml_escape('%s : %s' % (
                e.__class__.__name__,
                str(e)
            ))
            traceback.print_exc()
            raise error
    _preserve_argcount(wrapper, func)
    wrapper.func_name = func.func_name
    return wrapper


def formattransformer(func):
    def wrapper(self, *args, **kwargs):
        value = func(self, *args, **kwargs)
        if not IFormatTransformable.providedBy(value):
            return self.write(unicode(value))
        format_ = self.get_argument('format', 'xml')
        formatter = getUtility(IFormatter, name=format_)
        self.set_header('Content-Type', formatter.content_type)
        self.write(formatter.format(value))

    _preserve_argcount(wrapper, func)
    wrapper.func_name = func.func_name
    return wrapper

def require_auth(func):
    def wrapper(self, *args, **kwargs):
        auth = getUtility(IAuthService)
        credentials = auth.extract_credentials(self.request)            
        if not auth.authenticate(credentials):
            raise Unauthorized
        self.handler._current_user = auth.principal(credentials)
        return func(self, *args, **kwargs)
    _preserve_argcount(wrapper, func)
    wrapper.func_name = func.func_name
    return wrapper

def node_name(name):
    def wrapper(func):
        func.func_name = name
        return func
    return wrapper

