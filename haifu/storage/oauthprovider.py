from haifu.services.oauthprovider import (IOAuthRequest, IOAuthService, 
                                    IOAuthStorage, IOAuthConsumer, 
                                    IOAuthToken)
from haifu.interfaces import IRequest
from haifu.storage.db import OAuthConsumer, OAuthToken, OAuthNonce
from haifu.storage.saconfig import named_scoped_session
from oauth import oauth
import urllib
import random, string
import grokcore.component as grok
import zope.component as zca


def random_key(length=12):
    population = string.letters + string.digits
    return ''.join(random.sample(population, 1)[0] for i in range(length))


class SQLAlchemyOAuthStorage(grok.GlobalUtility):
    grok.implements(IOAuthStorage)

    def lookup_consumer(self, key):
        session = named_scoped_session('haifu.storage')
        consumer = session.query(OAuthConsumer).filter(
            OAuthConsumer.consumer_key==key
        ).first()
        return IOAuthConsumer(consumer) if consumer else None

    def lookup_nonce(self, oauth_consumer, oauth_token, nonce):
        session = named_scoped_session('haifu.storage')
        query = session.query(OAuthNonce).filter(
                OAuthNonce.consumer_key==oauth_consumer.key).filter(
                OAuthNonce.nonce_key==nonce)
        if oauth_token:
            query = query.filter(OAuthNonce.token_key==oauth_token.key)
        n = query.first()
        return n.nonce_key if n else None

    def fetch_request_token(self, oauth_consumer, oauth_callback):
        session = named_scoped_session('haifu.storage')
        token = OAuthToken(
            consumer_key=oauth_consumer.key,
            callback=oauth_callback,
            key=random_key(), secret=random_key(),
            token_type='request'
        )
        session.add(token)
        return IOAuthToken(token)

    def fetch_access_token(self, oauth_consumer, oauth_token, oauth_verifier):
        session = named_scoped_session('haifu.storage')
        request_token = session.query(OAuthToken).filter(
                OAuthToken.consumer_key==oauth_consumer.key).filter(
                OAuthToken.key==oauth_token.key).filter(
                OAuthToken.token_type=='request').filter(
                OAuthToken.verifier==oauth_verifier).first()
        if not request_token:
            return None

        token = OAuthToken(
            consumer_key=oauth_consumer.key,
            key=random_key(),
            secret=random_key(),
            user=request_token.user,
            token_type='access'
        )

        session.add(token)

        return IOAuthToken(token)

    def lookup_token(self, token_type, token):
        session = named_scoped_session('haifu.storage')
        token = session.query(OAuthToken).filter(
            OAuthToken.key==token
        ).filter(OAuthToken.token_type==token_type).first()
        return IOAuthToken(token) if token else None

    def authorize_request_token(self, oauth_token, user):
        session = named_scoped_session('haifu.storage')
        token = session.query(OAuthToken).filter(
            OAuthToken.key==oauth_token.key,
            OAuthToken.token_type=='request').first()
        if token:
            token.verifier = random_key()
            token.user = user
        return IOAuthToken(token) if token else None


@grok.adapter(IRequest)
@grok.implementer(IOAuthRequest)
def request_adapter(request):
    return oauth.OAuthRequest.from_request(
        request.method,
        request.url,
        headers=request.headers,
        query_string=request.query_string
    )

@grok.adapter(OAuthConsumer)
@grok.implementer(IOAuthConsumer)
def consumer_adapter(consumer):
    key = consumer.consumer_key.encode('ascii', 'ignore')
    secret = consumer.consumer_secret.encode('ascii', 'ignore')
    return oauth.OAuthConsumer(key, secret)

@grok.adapter(OAuthToken)
@grok.implementer(IOAuthToken)
def token_adapter(token):
    key = token.key.encode('ascii', 'ignore')
    secret = token.key.encode('ascii', 'ignore')
    oauthtoken = oauth.OAuthToken(key, secret)

    if token.user:
        oauthtoken.user = token.user

    if token.verifier:
        oauthtoken.set_verifier(token.verifier.encode('ascii','ignore'))

    if token.callback:
        callback = token.callback.encode('ascii', 'ignore')
        oauthtoken.set_callback(callback)
    return oauthtoken

