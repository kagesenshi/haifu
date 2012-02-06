import grokcore.component as grok
from haifu.interfaces import IRegistry

REGISTRY={
    'site.version': 0.1,
    'site.title': 'Haifu Test',
    'site.host': 'haifu.kagesenshi.org',
    'site.contact': 'izhar@inigo-tech.com',
    'site.ssl_enabled': False
}

class Registry(grok.GlobalUtility):
    grok.implements(IRegistry)
    def get(self, key):
        return REGISTRY.get(key, None)

    def set(self, key, value):
        REGISTRY.set(key, value)
