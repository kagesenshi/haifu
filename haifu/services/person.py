from haifu.interfaces import IService, IAuthService, IPersonStorage
from zope.interface import classProvides
import grokcore.component as grok
import zope.component as zca
from haifu.api import Service, method
from haifu import ocshelper
import base64
import re

class PersonService(Service):
    grok.name('v1/person')
    classProvides(IService)

    @method('post')
    def check(self):
        login = self.get_argument('login', None)
        password = self.get_argument('password', None)

        if login is None:
            return {'ocs': ocshelper.meta(False, 101, 
                'please specify all mandatory fields ')
            }

        auth = zca.getUtility(IAuthService)
        credentials = {
            'login': login,
            'password': password
        }

        if not auth.authenticate(credentials):
            return {'ocs': ocshelper.meta(False, 102, 
                'login not valid')}

        result = ocshelper.meta()
        principal = auth.principal(credentials)
        result.update({'data': { 'person': {'personid': principal}}})
        return {'ocs': result}


    @method('post')
    def add(self):
        login = self.get_argument('login', None)
        password = self.get_argument('password', None)
        firstname = self.get_argument('firstname', None)
        lastname = self.get_argument('lastname', None)
        email = self.get_argument('email', None)

        if not (login and password and firstname and lastname and email):
            return {'ocs': ocshelper.meta(False, 101, 
                        'please specify all mandatory fields')}

        if len(password) < 8:
            return {'ocs': ocshelper.meta(False, 102, 
                        'please specify a password longer than 8 characters')}

        if not re.match(r'^[A-Z0-9]{0,9999}$', login):
            return {'ocs': ocshelper.meta(False, 102, 
                        'login can only consist of alphanumeric characters')}

        if '@' not in email:
            # not sure whats the best email validator parser around
            return {'ocs': ocshelper.meta(False, 106,
                'invalid email')}

        storage = zca.getUtility(IPersonStorage)
        if storage.get_person(login):
            return {'ocs': ocshelper.meta(False, 104, 
                '%s already exist, please choose a different login' % login)}

        if storage.get_person_by_email(email):
            return {'ocs': ocshelper.meta(False, 105,
                '%s already have an account associated' % login)}

        storage.add_person(
            login=login,
            password=password,
            firstname=firstname,
            lastname=lastname,
            email=email
        )

        return {'ocs': ocshelper.meta()}
            


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
