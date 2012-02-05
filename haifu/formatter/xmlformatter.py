from haifu.interfaces import IFormatter
import grokcore.component as grok
import xmldict

class XMLFormatter(grok.GlobalUtility):
    grok.name('xml')
    content_type = 'text/xml'
    grok.implements(IFormatter)

    def format(self, value):
        return '<?xml version="1.0"?>' + xmldict.dict_to_xml(value)
