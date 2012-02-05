from haifu.interfaces import IFormatter
import grokcore.component as grok
import simplejson
import xmldict

class JSONFormatter(grok.GlobalUtility):
    grok.name('json')
    content_type = 'text/json'
    grok.implements(IFormatter)

    def format(self, value):
        return simplejson.dumps(value)

class XMLFormatter(grok.GlobalUtility):
    grok.name('xml')
    content_type = 'text/xml'
    grok.implements(IFormatter)

    def format(self, value):
        return '<?xml version="1.0"?>' + xmldict.dict_to_xml(value)
