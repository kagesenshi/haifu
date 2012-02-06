import grokcore.component as grok
import zope.component as zca
from haifu.interfaces import IRegistry, IConfiguration

REGISTRY={
    'site.version': 0.1,
    'site.title': 'Haifu Test',
    'site.host': 'haifu.kagesenshi.org',
    'site.contact': 'izhar@inigo-tech.com',
    'site.ssl_enabled': False
}

class Registry(grok.GlobalUtility):
    grok.implements(IRegistry)
    def get(self, key, type=None):
        config = zca.getUtility(IConfiguration)
        if not config.has_option('registry', key):
            return None

        if type == 'boolean':
            return config.getboolean('registry', key)
        elif type == 'float':
            return config.getfloat('registry', key)
        elif type == 'int':
            return config.getint('registry', key)

        return config.get('registry', key)

    def set(self, key, value):
        # doesnt apply here
        raise NotImplementedError
