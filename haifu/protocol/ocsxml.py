from haifu.schema import (IPerson, IResult, IConfig, IData,
                         IActivity, IAttribute)
from haifu.interfaces import IFormatter
import grokcore.component as grok
import zope.component as zca
from zope.interface import implements, Interface
from zope import schema
import xmldict
from haifu.util import to_dict

class IOpenCollaborationServiceXML(Interface):
    pass

class XMLFormatter(grok.GlobalUtility):
    grok.name('xml')
    content_type = 'text/xml'
    grok.implements(IFormatter)

    def format(self, value):
        obj = IOpenCollaborationServiceXML(value)()
        return '<?xml version="1.0"?>' + xmldict.dict_to_xml(obj)


class BaseAdapter(grok.Adapter):
    implements(IOpenCollaborationServiceXML)
    grok.context(IData)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return to_dict(self.context)

    def insert(self, container):
        container.update(self.__call__())

class ResultAdapter(BaseAdapter):
    grok.context(IResult)

    def __call__(self):
        obj = self.context
        result = {
           'meta': {
               'status': obj.status,
               'statuscode': obj.statuscode,
           },
        }

        if obj.message:
            result['meta']['message'] = obj.message

        for item in obj.data:
            result.setdefault('data', {})
            adapter = IOpenCollaborationServiceXML(item)
            adapter.insert(result['data'])

        return {'ocs': result}

class PersonAdapter(BaseAdapter):
    grok.context(IPerson)

    def insert(self, container):
        data = {
            '@details':'full'
        }
        container.setdefault('person', [])
        data.update(self.__call__())
        container['person'].append(data)

class AttributeAdapter(BaseAdapter):
    grok.context(IAttribute)

    def insert(self, container):
        data = self.context.data
        if data:
            container['attribute'] = data

class ActivityAdapter(BaseAdapter):
    grok.context(IActivity)

    def insert(self, container):
        data = self.__call__()
        data['id'] = data['activityid']
        del data['activityid']
        container.setdefault('activity', [])
        container['activity'].append(data)
