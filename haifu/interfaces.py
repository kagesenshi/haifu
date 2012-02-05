from zope.interface import Interface

class IService(Interface):
    """ marker interface for a service """

class IRegistry(Interface):
    """ Registry utility """

    def get(key): pass
    def set(key, value): pass

class IFormatter(Interface):

    def format(value): pass


class IAuthService(Interface):
    pass
