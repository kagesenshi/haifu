from haifu.schema import IPerson, IResult, IConfig, IData
from haifu.interfaces import IFormatter
from haifu.util import to_dict
import grokcore.component as grok
import zope.component as zca
from zope.interface import implements, Interface
import simplejson
from zope import schema

class IOpenCollaborationServicesJSON(Interface):
    pass

def json_encoder(obj):
    iface = getattr(obj, '__schema__', None)
    if iface is None:
        return obj
    return IOpenCollaborationServicesJSON(obj)()

class BaseAdapter(grok.Adapter):
    grok.implements(IOpenCollaborationServicesJSON)
    grok.context(IData)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        result = to_dict(self.context)
        return result


class ResultAdapter(BaseAdapter):
    grok.context(IResult)

    def __call__(self):
        obj = self.context
        result = {
            'status': obj.status,
            'statuscode': obj.statuscode,
            'message': obj.message,
            'data': obj.data
        }
        return result

class PersonAdapter(BaseAdapter):
    grok.context(IPerson)

    def __call__(self):
        result = to_dict(self.context)
        for listing in result.get('listings', []):
            result[listing.type_] = listing.items
        return result


class JSONFormatter(grok.GlobalUtility):
    grok.name('json')
    content_type = 'text/json'
    implements(IFormatter)

    def format(self, value):
        return simplejson.dumps(value, default=json_encoder)

