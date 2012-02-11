from zope.interface import implements, Interface, Attribute
from zope import schema

class IData(Interface):
    __schema__ = Attribute('Schema')

class IResult(Interface):
    status = schema.TextLine(title=u'Status')
    statuscode = schema.Int(title=u'Status Code')
    message = schema.TextLine(title=u'Message')
    data = schema.List(title=u'Data', 
        value_type=schema.Object(schema=IData)
    )


class IConfig(IData):
    version = schema.Float(title=u'Version')
    website = schema.TextLine(title=u'Website')
    host = schema.TextLine(title=u'Host')
    contact = schema.TextLine(title=u'Contact')
    ssl = schema.TextLine(title=u'SSL Enabled')


class IWebsite(IData):
    link = schema.URI(title=u'Website URL')
    # whats the available homepagetypes?
    type_ = schema.TextLine(title=u'Website Type')


class IIRCChannel(IData):
    channel = schema.TextLine(title=u'Channel name')
    link = schema.URI(title=u'IRC Link')

class IListing(IData):
    type_ = schema.TextLine(title=u'Type')
    items = schema.List(title=u'Items')

class IPerson(IData):
    personid = schema.TextLine(title=u'Person ID')
    description = schema.TextLine(title=u'Description')
    profilepage = schema.URI(title=u'Profile page url')
    firstname = schema.TextLine(title=u'First Name')
    lastname = schema.TextLine(title=u'Last Name')
    gender = schema.Choice(title=u'Gender',
                            values=['male','female','other'])
    communityrole = schema.TextLine(title=u'Community Role')


    privacy = schema.Int(title=u'Privacy')
    privacytext = schema.TextLine(title=u'Privacy Text')

    company = schema.TextLine(title=u'Company')

    # why not having avatar similar like how icon is specified in <icon>?.
    # instead of avatar and bigavatar, use 
    # <avatar width="x" height="y>URI</avatar>

    avatarpic = schema.URI(title=u'Avatar picture URL')
    avatarpicfound = schema.Int(title=u'Has avatar flag') # bool?
    bigavatarpic = schema.URI(title=u'Larger avatar picture')
    bigavatarpicfound = schema.Int(title=u'Has big avatar flag') # bool?

    #

    birthday = schema.Date(title=u'Birthday date') # strftime('%F')
    jobstatus = schema.TextLine(title=u'Job status')

    # location information
    city = schema.TextLine(title=u'City')
    latitude = schema.Float(title=u'Latitude')
    longitude = schema.Float(title=u'Longitude')

    listings = schema.List(title=u'Favourites',
        value_type=schema.Object(schema=IListing)
    )


class IActivity(IData):
    activityid = schema.Int(title=u'ID')
    person = schema.Object(title=u'Person',
        schema=IPerson
    )
    timestamp = schema.Datetime(title=u'Timestamp')
    type_ = schema.Int(title=u'Activity type')
    message = schema.TextLine(title=u'Message')
    link = schema.URI(title=u'Link')

class IAttribute(IData):
    data = schema.Object(schema=Interface)
