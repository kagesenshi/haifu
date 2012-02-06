from zope.interface import Interface, Attribute

class IConfiguration(Interface):
    """ marker interface for a global 
        configparser object storing system config """

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

class IVerificationService(Interface):
    """ Service for email verification of actions """
    def send_verification(action_id, data, unique_key=None):
        """ return a verification ID 

            unique_key parameter is used for determining unique of 
            the entry. if duplicate is found, the old verification id 
            is deleted, and a new one is generated.
        """

    def approve_verification(verification_id):
        """ check the verification id, and trigger the associated action. 
            return True for valid id, return False for unknown id """

class IVerificationAction(Interface):
    """ marker interface for verification actions. """

class IVerificationStorage(Interface):
    """ global utility which stores verification entries """

    def add_entry(key, action_id, data, unique_key):
        """ add an entry. delete old entry if unique_key matches """

    def get_entry(key):
        """ returns IVerificationEntry object from the entry key """

    def delete_entry(key):
        """ delete entry which matches the key """

class IVerificationEntry(Interface):
    action_id = Attribute('Action ID')
    data = Attribute('Action Data')

class IEvent(Interface):
    pass

class IStartupEvent(IEvent):
    pass

class IInitializeEvent(IEvent):
    pass

class IRequestFinishingEvent(IEvent):
    pass

class IVerificationEvent(IEvent):
    data = Attribute('Event data')

class IPersonVerificationEvent(IVerificationEvent):
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


