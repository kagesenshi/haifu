from haifu.exc import HTTPException, Unauthorized
from zope.component import getUtility, getUtilitiesFor
from haifu.interfaces import IService, IFormatter, IAuthService
from haifu import ocshelper
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
            message = ocshelper.meta(False, 999, str(e))
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
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except HTTPException, e:
            self.set_status(e.code)
            for k, v in e.headers:
                self.set_header(k, v)
            message = '%s: %s' % (e.code, e.message)
            result = ocshelper.meta(False, 999, message)
            self._transforms = []
            return {'ocs': result}
        return result
    wrapper.func_name = func.func_name
    return wrapper

def require_auth(func):
    def wrapper(self, *args, **kwargs):
        # inspired from Plone's Pluggable Auth Service
        valid = False
        for name, util in getUtilitiesFor(IAuthService):
            credentials = util.extract_credentials(self.request)            
            if util.authenticate(**credentials):
                valid = True
                break
        if not valid:
            raise Unauthorized
        return func(self, *args, **kwargs)

    wrapper.func_name = func.func_name
    return wrapper
