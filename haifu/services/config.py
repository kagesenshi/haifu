from haifu.api import Service, method, require_auth
from haifu.interfaces import IService, IRegistry
from haifu.model import Result, Config
import grokcore.component as grok
import zope.component as zca
from zope.interface import classProvides

class ConfigService(Service):
    grok.name('v1/config')
    classProvides(IService)

    def index(self):
        registry = zca.getUtility(IRegistry)
        data = [
            Config(
                version=registry.get('site.version', 'float'),
                website=registry.get('site.title'),
                host=registry.get('site.host'),
                contact=registry.get('site.contact'),
                ssl=registry.get('site.ssl_enabled', 'boolean'),
            )
        ]
        result = Result()
        result.data = data

        return result
