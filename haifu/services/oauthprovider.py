from haifu.interfaces import IService, IRequest
from haifu.model import Service
from haifu.api import require_auth
import grokcore.component as grok
import zope.component as zca
from zope.interface import classProvides, Interface
from oauth import oauth
import urllib
import random, string

class IOAuthRequest(Interface): 
    pass

class IOAuthService(Interface):
    pass

class IOAuthStorage(Interface):
    pass

class IOAuthConsumer(Interface):
    pass

class IOAuthToken(Interface):
    pass

def create_oauth_service():
    storage = zca.getUtility(IOAuthStorage)
    server = oauth.OAuthServer(storage)
    server.add_signature_method(oauth.OAuthSignatureMethod_PLAINTEXT())
    server.add_signature_method(oauth.OAuthSignatureMethod_HMAC_SHA1())
    return server

class OAuthService(Service):
    grok.name('oauth')
    classProvides(IService)

    def request_token(self):
        request = IOAuthRequest(self.request)
        service = create_oauth_service()
        token = service.fetch_request_token(request)
        return token.to_string()

    @require_auth
    def authorize(self):
        request = IOAuthRequest(self.request)
        service = create_oauth_service()
        token = service.fetch_request_token(request)
        token = service.authorize_token(token, self.handler.get_current_user())

        result = {
            'oauth_token': token.key,
            'oauth_verifier': token.verifier
        }

        cb = token.get_callback_url() or self.request.get(
                'oauth_callback', None)

        if cb:
            self.handler.redirect('%s?%s' % (cb, urllib.urlencode(result)))
            return

        return token.verifier

    def access_token(self):
        request = IOAuthRequest(self.request)
        service = create_oauth_service()
        token = service.fetch_access_token(request)
        return '%s&%s' % (token.to_string(), urllib.urlencode({'username':
            token.user}))
