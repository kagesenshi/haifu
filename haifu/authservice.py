import grokcore.component as grok
from haifu.interfaces import IAuthService
import base64

class SimpleBasicAuthService(grok.GlobalUtility):
    grok.implements(IAuthService)
    # based on
    # http://kelleyk.com/post/7362319243/easy-basic-http-authentication-with-tornado

    def extract_credentials(self, request):

        auth_header = request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Basic '):
            return {'username': None, 'password': None}
        
        auth_decoded = base64.decodestring(auth_header[6:])
        cred = auth_decoded.split(':', 2)
        username = cred[0]
        password = None
        if len(cred) == 2:
            password = cred[1]

        return {
            'username': username,
            'password': password
        }

    def authenticate(self, username, password, **creds):
        if username == 'izhar' and password=='password':
            return True
        return False

    def principal(self, username, **creds):
        return username
