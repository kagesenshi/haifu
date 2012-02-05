import zope.component as zca
from haifu.interfaces import ISAEngine
from sqlalchemy.orm import scoped_session, sessionmaker

_named_scoped_session = {}

def named_scoped_session(name=''):
    if _named_scoped_session.get(name, None):
        return _named_scoped_session[name]

    engine = zca.getUtility(ISAEngine, name)()
    session = scoped_session(sessionmaker(bind=engine))
    _named_scoped_session[name] = session
    return session
