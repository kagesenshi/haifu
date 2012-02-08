from sqlalchemy import (Table, Column, Integer, MetaData, String, 
                        create_engine, UnicodeText, DateTime)
from sqlalchemy.orm import mapper
from haifu.interfaces import IStartupEvent, IConfiguration
from haifu.storage.saconfig import named_scoped_session
import grokcore.component as grok
import zope.component as zca

metadata = MetaData()

@grok.subscribe(IStartupEvent)
def handler(event):
    session = named_scoped_session('haifu.storage')
    metadata.create_all(session.bind)

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


verification_entry = Table('verification_entry', metadata,
    Column('id', Integer, primary_key=True),
    Column('action_id', String(255)),
    Column('data', UnicodeText),
    Column('unique_key', String(255)),
    Column('key', String(255)),
    Column('timestamp', DateTime)
)

class VerificationEntry(Model):
    pass

mapper(VerificationEntry, verification_entry)
