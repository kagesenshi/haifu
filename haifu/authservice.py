import grokcore.component as grok
from haifu.interfaces import IAuthService

class SimpleAuthService(grok.GlobalUtility):
    grok.implements(IAuthService)

    def authenticate(self, username, password):
        if username == 'izhar' and password=='password':
            return True
        return False

    def principal(self, username):
        return username
