from haifu.interfaces import IService, IAuthService
from zope.interface import classProvides
import grokcore.component as grok
import zope.component as zca
from haifu.api import Service, method
from haifu import formathelper
import base64

class PersonService(Service):
    grok.name('v1/person')
    classProvides(IService)

    @method('post')
    def check(self):
        login = self.get_argument('login', None)
        password = self.get_argument('password', None)

        if login is None:
            return {'ocs': formathelper.meta(False, 102, 'Missing login')}

        auth = zca.getUtility(IAuthService)


class SimpleBasicAuthService(grok.GlobalUtility):
    grok.implements(IAuthService)
    # based on
    # http://kelleyk.com/post/7362319243/easy-basic-http-authentication-with-tornado

    def extract_credentials(self, request):

        auth_header = request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Basic '):
            return {'login': None, 'password': None}

        auth_decoded = base64.decodestring(auth_header[6:])
        cred = auth_decoded.split(':', 2)
        login = cred[0]
        password = None
        if len(cred) == 2:
            password = cred[1]

        return {
            'login': login,
            'password': password
        }

    def authenticate(self, credentials):
        login = credentials.get('login', None)
        password = credentials.get('password', None)
        if login == 'izhar' and password=='password':
            return True
        return False

    def principal(self, credentials):
        return credentials.get('login', None)
