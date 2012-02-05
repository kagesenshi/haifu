

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
