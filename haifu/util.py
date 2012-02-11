import zope.component as zca
from zope import schema

def meta(success=True, statuscode=100, message=''):
    if success:
        status = 'ok'
    else:
        status = 'failed'

    return {
        'meta': {
            'status': status,
            'statuscode': statuscode,
            'message': message
        }
    }

def extract_data(handler, single=[], multi=[]):
    data = {}
    for field in single:
        data[field] = handler.get_argument(field, None)
    for field in multi:
        data[field] = handler.get_arguments(field, [])
    return data

def to_dict(obj, iface=None):
    result = {}
    if iface is None:
        iface = getattr(obj, '__schema__', None)
    for key, field in schema.getFields(iface).items():
        value = getattr(obj, key)
        if value is None or value == []:
            continue
        result[key] = value
    return result
