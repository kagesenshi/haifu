from haifu.interfaces import (IService, IAuthService, IPersonStorage,
                              IVerificationService, IVerificationAction,
                              IVerificationEvent, IVerificationStorage)
from zope.interface import classProvides
import grokcore.component as grok
import zope.component as zca
from haifu.api import Service, method, require_auth, node_name
from haifu.model import Result, Person, Attribute
from haifu import util
import base64
import re

class PersonService(Service):
    grok.name('v1/person')
    classProvides(IService)

    @method('post')
    def check(self):
        login = self.request.get('login', None)
        password = self.request.get('password', None)

        if login is None:
            return Result(False, 101, 
                'please specify all mandatory fields ')

        auth = zca.getUtility(IAuthService)
        credentials = {
            'login': login,
            'password': password
        }

        if not auth.authenticate(credentials):
            return Result(False, 102, 'login not valid')

        principal = auth.principal(credentials)

        result = Result()
        result.data = [Person(personid=principal)]
        return result


    @method('post')
    def add(self):
        login = self.request.get('login', None)
        password = self.request.get('password', None)
        firstname = self.request.get('firstname', None)
        lastname = self.request.get('lastname', None)
        email = self.request.get('email', None)

        if not (login and password and firstname and lastname and email):
            return Result(False, 101, 'please specify all mandatory fields')

        if len(password) < 8:
            return Result(False, 102, 
                        'please specify a password longer than 8 characters')

        if not re.match(r'^[A-Za-z0-9]{0,9999}$', login):
            return Result(False, 102, 
                        'login can only consist of alphanumeric characters')

        if '@' not in email:
            # not sure whats the best email validator parser around
            return Result(False, 106, 'invalid email')

        storage = zca.getUtility(IPersonStorage)
        vstorage = zca.getUtility(IVerificationStorage)
        if (storage.get_person(login) or 
            vstorage.has_entry('haifu.verify.person', login)):
            return Result(False, 104, 
                '%s already taken, please choose a different login' % login)

        if storage.get_person_by_email(email):
            return Result(False, 105,
                '%s already have an account associated' % email)

        vs = zca.getUtility(IVerificationService)
        vs.send_verification('haifu.verify.person', {
            'login': login,
            'password': password,
            'firstname': firstname,
            'lastname': lastname,
            'email': email }, 
            unique_key=login
        )

        return Result()

    @require_auth
    def data(self, person_id):
        storage = zca.getUtility(IPersonStorage)
        person = storage.get_person(person_id)
        if not person:
            return Result(False, 101, 'unknown user id')

        if not person.viewable_by(self.handler.get_current_user()):
            return Result(False, 102, 'user is private')

        result = Result()
        result.data = [
            Person(**person.get_properties())
        ]

        return result

    @require_auth
    def self(self):
        principal = self.handler.get_current_user()
        storage = zca.getUtility(IPersonStorage)
        person = storage.get_person(principal)
        result = Result()
        result.data = [
            Person(**person.get_properties())
        ]
        return result

    @node_name('self')
    @method('post')
    @require_auth
    def set_self(self):
        data = util.extract_data(self.handler, ['latitude', 'longitude', 'city',
                                                'country'])
        has_param = False
        for key, value in data.items():
            if value != None:
                has_param = True
                break

        if not has_param:
            return Result(False, 101, 'No parameter to update found')

        principal = self.handler.get_current_user()
        storage = zca.getUtility(IPersonStorage)
        person = storage.get_person(principal)

        person.set_properties(data)

        return result

    @require_auth
    def balance(self):
        principal = self.handler.get_current_user()
        storage = zca.getUtility(IPersonStorage)
        person = storage.get_person(principal)

        result = Result()
        result.data = [
            Person(**person.get_balance())
        ]

        return result

    @require_auth
    def attributes(self, person_id, app=None, key=None):
        storage = zca.getUtility(IPersonStorage)
        person = storage.get_person(person_id)

        result = Result()

        data = person.get_xattr(app, key)
        if data:
            result.data = [
                Attribute(person.get_xattr(app, key))
            ]

        return result


    @require_auth
    @method('post')
    def setattribute(self, app, key):
        data = util.extract_data(self.handler, ['value'])

        principal = self.handler.get_current_user()
        storage = zca.getUtility(IPersonStorage)
        person = storage.get_person(principal)

        person.set_xattr(app, key, value)

        return Result()

    @require_auth
    @method('post')
    def deleteattribute(self, app, key):
        principal = self.handler.get_current_user()
        storage = zca.getUtility(IPersonStorage)
        person = storage.get_person(principal)

        person.delete_xattr(app, key, value)

        return Result()



class IPersonVerificationEvent(IVerificationEvent):
    pass

@grok.subscribe(IPersonVerificationEvent)
def handler(event):
    storage = zca.getUtility(IPersonStorage)
    storage.add_person(**event.data)

class SimpleBasicAuthService(grok.GlobalUtility):
    grok.implements(IAuthService)
    # based on
    # http://kelleyk.com/post/7362319243/easy-basic-http-authentication-with-tornado

    def extract_credentials(self, request):

        auth_header = request.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Basic '):
            return {'login': None, 'password': None}

        auth_decoded = base64.decodestring(auth_header[6:])
        cred = auth_decoded.split(':', 2)
        login = cred[0]
        password = None
        if len(cred) == 2:
            password = cred[1]

        return {
            'login': login,
            'password': password
        }

    def authenticate(self, credentials):
        login = credentials.get('login', None)
        password = credentials.get('password', None)

        storage = zca.getUtility(IPersonStorage)

        if login is None:
            return False

        if password is not None:
            person = storage.get_person(login)
        else:
            person = storage.get_person_by_apikey(login)

        if not person:
            return False

        if not person.validate_password(password):
            return False

        return True

    def principal(self, credentials):
        login = credentials.get('login', None)
        password = credentials.get('password', None)

        storage = zca.getUtility(IPersonStorage)

        if password is not None:
            person = storage.get_person(login)
        else:
            person = storage.get_person_by_apikey(login)

        return person.principal


class PersonVerificationEvent(grok.GlobalUtility):
    grok.implements(IPersonVerificationEvent)
    grok.name('haifu.verify.person')
    grok.direct()
    classProvides(IVerificationAction)

    def __init__(self, data):
        self.data = data
