from haifu.interfaces import IStartupEvent, IInitializeEvent
import grokcore.component as grok

class StartupEvent(object):
    grok.implements(IStartupEvent)

class InitializeEvent(object):
    grok.implements(IInitializeEvent)
