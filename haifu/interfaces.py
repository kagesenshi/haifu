from zope.interface import Interface, Attribute

class IService(Interface):
    """ marker interface for a service """

class IRegistry(Interface):
    """ Registry utility for site configurations"""

    def get(key): pass
    def set(key, value): pass

class IFormatter(Interface):
    """ Output formatter, convert dicts to xml/json """

    content_type = Attribute('Content Type')

    def format(value): 
        """ accepts a dict, and write the formatted value """


class IAuthService(Interface):
    """ Authentication plugin, inspired from Plone PAS """

    def extract_credentials(request):
        """ Extract credentials from request, return a dict """

    def authenticate(credentials):
        """ Authenticate the given credentials """

    def principal(**credentials):
        """ Return the principal id (user id) from the credentials """


class IEvent(Interface):
    pass

class IStartupEvent(IEvent):
    pass


class IStorage(Interface):
    pass

class IPersonStorage(IStorage):
    def add_person(login, password, firstname, lastname, email):
        """ return object which implements IPerson """

    def get_person(login):
        """ return object which implements IPerson """

    def get_person_by_email(email):
        """ return object which implements IPerson """

    def get_person_by_apikey(apikey):
        """ return object which implements IPerson """


class IPerson(Interface):

    principal = Attribute('Principal ID')

    def validate_password(password):
        """ returns bool """
