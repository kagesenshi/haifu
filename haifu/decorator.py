from haifu.exc import HTTPException, Unauthorized
from zope.component import getUtility, getUtilitiesFor
from haifu.interfaces import IService, IFormatter, IAuthService
from haifu import formathelper
import traceback
import base64

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
            message = formathelper.meta(False, 999, str(e))
            traceback.print_exc()
            return {'ocs': message}
    wrapper.func_name = func.func_name
    return wrapper


def formattransformer(func):
    def wrapper(self, *args, **kwargs):
        format_ = self.get_argument('format', 'xml')
        value = func(self, *args, **kwargs)
        formatter = getUtility(IFormatter, name=format_)
        self.set_header('Content-Type', formatter.content_type)
        self.write(formatter.format(value))
    wrapper.func_name = func.func_name
    return wrapper

def httpexceptionhandler(func):
    # based on
    # http://kelleyk.com/post/7362319243/easy-basic-http-authentication-with-tornado
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except HTTPException, e:
            self.set_status(e.code)
            for k, v in e.headers:
                self.set_header(k, v)
            message = '%s: %s' % (e.code, e.message)
            result = formathelper.meta(False, 999, message)
            self._transforms = []
            return result
        return result
    wrapper.func_name = func.func_name
    return wrapper

def require_auth(func):
    def wrapper(self, *args, **kwargs):
        auth_header = self.request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Basic '):
            raise Unauthorized
        auth_decoded = base64.decodestring(auth_header[6:])
        cred = auth_decoded.split(':', 2)
        username = cred[0]
        password = None
        if len(cred) == 2:
            password = cred[1]

        valid = False
        for name, util in getUtilitiesFor(IAuthService):
            if util.authenticate(username, password):
                valid = True
                break
        if not valid:
            raise Unauthorized
        return func(self, *args, **kwargs)

    wrapper.func_name = func.func_name
    return wrapper
