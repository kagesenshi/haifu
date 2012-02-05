from haifu.interfaces import IFormatter
import grokcore.component as grok
import simplejson

class JSONFormatter(grok.GlobalUtility):
    grok.name('json')
    content_type = 'text/json'
    grok.implements(IFormatter)

    def format(self, value):
        return simplejson.dumps(value)
