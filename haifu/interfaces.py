from zope.interface import Interface, Attribute

class IConfiguration(Interface):
    """ marker interface for a global 
        configparser object storing system config """

class IService(Interface):
    """ marker interface for a service """

class IRegistry(Interface):
    """ Registry utility for site configurations"""

    def get(key, type=None): pass
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

    def add_entry(key, action_id, data, unique_key, timestamp=None):
        """ 
            add an entry. delete old entry if unique_key matches.

            store timestamp as current UTC time if not specified, 
            if specified, use the specified time, converted to UTC
            if possible.
        
        """

    def get_entry(key):
        """ returns IVerificationEntry object from the entry key """

    def has_entry(action_id, unique_key):
        """ 
            return boolean whether theres matching entry of action_id and 
            unique_key
        """

    def delete_entry(key):
        """ delete entry which matches the key """

    def expire_entries(age=24):
        """ 
            expire old entries. delete entries older than 
            the specified age, in hour 
        """

class IVerificationEntry(Interface):
    action_id = Attribute('Action ID')
    data = Attribute('Action Data')

class IEvent(Interface):
    pass

class IStartupEvent(IEvent):
    pass

class IInitializeEvent(IEvent):
    pass

class IRequestStartingEvent(IEvent):
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


    def get_properties():
        """ return a dictionary of person properties 
            
            refer:
            http://freedesktop.org/wiki/Specifications/open-collaboration-services#get
        """

    def set_properties(data):
        """
            accepts a dictionary, set the person main properties
        """

    def get_balance():
        """
            return account balance. 
            format: 
            
            {
                'currency': 'USD',
                'balance': 1.49
            }
        """
