import zope.component as zca
from zope.interface import Interface
from sqlalchemy.orm import scoped_session, sessionmaker

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
