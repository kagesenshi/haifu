from haifu.interfaces import (IStartupEvent, IInitializeEvent,
                              IRequestFinishingEvent, IRequestStartingEvent)
import grokcore.component as grok

class StartupEvent(object):
    grok.implements(IStartupEvent)

class InitializeEvent(object):
    grok.implements(IInitializeEvent)

class RequestFinishingEvent(object):
    grok.implements(IRequestFinishingEvent)

    def __init__(self, handler):
        self.handler = handler

class RequestStartingEvent(object):
    grok.implements(IRequestStartingEvent)

    def __init__(self, handler):
        self.handler = handler
