from haifu.interfaces import IPersonStorage, IPerson
import grokcore.component as grok
from haifu.storage.saconfig import named_scoped_session
from haifu.storage.db import Person
import hashlib

class SQLAlchemyPersonStorage(grok.GlobalUtility):
    grok.implements(IPersonStorage)

    def add_person(self, login, password, firstname, lastname, email):
        session = named_scoped_session('haifu.storage')
        
        hashed_pw = hashlib.sha1(password).hexdigest()
        
        p = Person(
            login=login,
            password=hashed_pw,
            firstname=firstname,
            lastname=lastname,
            email=email
        )

        session.add(p)
        session.flush()
        return IPerson(p)

    def get_person(self, login):
        session = named_scoped_session('haifu.storage')
        p = session.query(Person).filter(Person.login==login).first()
        return IPerson(p) if p else None

    def get_person_by_email(self, email):
        session = named_scoped_session('haifu.storage')
        p = session.query(Person).filter(Person.email==email).first()
        return IPerson(p) if p else None

    def get_person_by_apikey(self, apikey):
        raise NotImplementedError


class SQLPersonAdapter(grok.Adapter):
    grok.context(Person)
    grok.implements(IPerson)

    def __init__(self, context):
        self.context = context

    @property
    def principal(self):
        return self.context.login

    def validate_password(self, password):
        hashed_pw = hashlib.sha1(password).hexdigest()
        if self.context.password == hashed_pw:
            return True
        return False
