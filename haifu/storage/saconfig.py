import zope.component as zca
import grokcore.component as grok
from haifu.interfaces import (IInitializeEvent, IConfiguration,
                                IRequestFinishingEvent)
from zope.interface import Interface
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

_named_scoped_session = {}

class IEngineFactory(Interface):
    """ global utility which create an engine """
    def __call__():
        """ returns engine from sqlalchemy create_engine """

def named_scoped_session(name=''):
    if _named_scoped_session.get(name, None):
        return _named_scoped_session[name]

    engine = zca.getUtility(IEngineFactory, name)()
    session = scoped_session(sessionmaker(bind=engine))
    _named_scoped_session[name] = session
    return session

@grok.subscribe(IInitializeEvent)
def handler(event):
    config = zca.getUtility(IConfiguration)
    gsm = zca.getGlobalSiteManager()
    for name, dburi in config.items('saconfig'):
        engine = create_engine(dburi)
        gsm.registerUtility(lambda: engine, IEngineFactory, name=name)

@grok.subscribe(IRequestFinishingEvent)
def request_finish(event):
    config = zca.getUtility(IConfiguration)
    for name, dburi in config.items('saconfig'):
        session = named_scoped_session(name)
        session.commit()
