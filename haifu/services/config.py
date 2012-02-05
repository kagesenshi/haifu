from haifu.api import Service, method, require_auth
from haifu.interfaces import IService, IRegistry
import grokcore.component as grok
import zope.component as zca
from zope.interface import classProvides

class ConfigService(Service):
    grok.name('v1/config')
    classProvides(IService)

    @require_auth
    def index(self):
        registry = zca.getUtility(IRegistry)
        return {
            'ocs': {
                'meta': {
                    'status': 'ok',
                    'statuscode': 100,
                    'message': ''
                },
                'data': {
                    'version': registry.get('site.version'),
                    'website': registry.get('site.title'),
                    'host': registry.get('site.host'),
                    'contact': registry.get('site.contact'),
                    'ssl': registry.get('site.ssl_enabled')
                }
            }
        }
