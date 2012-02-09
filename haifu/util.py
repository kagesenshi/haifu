import zope.component as zca

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
