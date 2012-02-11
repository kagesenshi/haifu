import zope.component as zca
from zope import schema as zschema
from zope.interface import directlyProvides

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

def extract_data(request, single=[], multi=[], schema=None):
    data = {}
    if (single or multi) and schema:
        raise TypeError('schema cant be used together with single/multi')

    if schema:
        for key, field in zschema.getFields(schema).items():
            if isinstance(field, zchema.List):
                data[key] = request.get_array(key, [])
            elif isinstance(field, zchema.Boolean):
                data[key] = bool(request.get(key, False))
            elif isinstance(field, zchema.Int):
                data[key] = int(request.get(key, 0))
            else:
                data[key] = request.get(key, None)
        return data

    for field in single:
        data[field] = request.get(field, None)
    for field in multi:
        data[field] = request.get_array(field, [])
    return data

class Object(object):pass

def extract_data_as_object(request, schema):
    obj = Object()
    data = extract_data(request, schema)
    for key, field in zschema.getFields(schema).items():
        setattr(obj, key, data[key])
    directlyProvides(obj, schema)
    return obj

def to_dict(obj, iface=None):
    result = {}
    if iface is None:
        iface = getattr(obj, '__schema__', None)
    for key, field in zschema.getFields(iface).items():
        value = getattr(obj, key)
        if value is None or value == []:
            continue
        result[key] = value
    return result
