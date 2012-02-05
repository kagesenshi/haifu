from haifu.interfaces import IStartupEvent
import grokcore.component as grok

class StartupEvent(object):
    grok.implements(IStartupEvent)
