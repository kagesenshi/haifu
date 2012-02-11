import zope.component as zca
import grokcore.component as grok
from zope.interface import implements
from haifu.interfaces import IFormatter
from haifu.util import to_dict
import simplejson

def json_encoder(obj):
    iface = getattr(obj, '__schema__', None)
    if iface is None:
        return obj
    return to_dict(obj)

class JSONFormatter(grok.GlobalUtility):
    grok.name('rawjson')
    content_type = 'text/json'
    implements(IFormatter)

    def format(self, value):
        return simplejson.dumps(value, default=json_encoder)

