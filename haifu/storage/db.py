from sqlalchemy import Table, Column, Integer, MetaData, String, create_engine
from sqlalchemy.orm import mapper
from haifu.interfaces import IStartupEvent, IConfiguration
from haifu.storage.saconfig import named_scoped_session, IEngineFactory
import grokcore.component as grok
import zope.component as zca

metadata = MetaData()

@grok.subscribe(IStartupEvent)
def handler(event):
    config = zca.getUtility(IConfiguration)
    gsm = zca.getGlobalSiteManager()
    dburi = config.get('saconfig', 'haifu.storage')
    engine = create_engine(dburi)
    gsm.registerUtility(lambda: engine, IEngineFactory, name='haifu.storage')
    metadata.create_all(engine)

class Model(object):
    def __init__(self, **kw):
        for key, value in kw.items():
            setattr(self, key, value)

person = Table('person', metadata,
    Column('id', Integer, primary_key=True),
    Column('login', String(255)),
    Column('password', String(255)),
    Column('firstname', String(255)),
    Column('lastname', String(255)),
    Column('email', String(255))
)

class Person(Model):
    pass

mapper(Person, person)
