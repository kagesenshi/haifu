
class HTTPException(Exception):
    headers = []
    pass

class Unauthorized(HTTPException):
    code = 401
    message = 'Unauthorized'
    headers = [('WWW-Authenticate', 'Basic realm=Restricted')]

class Forbidden(HTTPException):
    code = 403
    message = 'Forbidden'

class InternalError(HTTPException):
    code = 501
    message = ''
