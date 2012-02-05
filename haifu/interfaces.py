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
