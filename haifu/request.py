from tornado.web import RequestHandler
from haifu.interfaces import IRequest
import grokcore.component as grok
import urlparse

class Request(grok.Adapter):
    grok.implements(IRequest)
    grok.context(RequestHandler)

    def __init__(self, context):
        self.context = context

    @property
    def method(self):
        return self.context.request.method

    @property
    def headers(self):
        return self.context.request.headers

    @property
    def url(self):
        return self.context.request.full_url()

    @property
    def path(self):
        return self.context.request.uri

    def get(self, key, default=None):
        return self.context.get_argument(key, default)

    def get_array(self, key, default=None):
        return self.context.get_arguments(key, default)

    @property
    def query_string(self):
        return self.context.request.query

    @property
    def body(self):
        return self.context.request.body

    def get_url(self, path):
        r = urlparse.ParseResult(self.context.request.protocol,
                            self.context.request.host,
                            path,'','','')
        return urlparse.urlunparse(r)
