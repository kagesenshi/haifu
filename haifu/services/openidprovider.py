from haifu.interfaces import IService, IRequest
from haifu.model import Service
from haifu.api import require_auth, method, node_name
import grokcore.component as grok
import zope.component as zca
from zope.interface import classProvides, Interface
from openid.server.server import Server
from haifu.util import extract_data
import urlparse

class IOpenIDStorage(Interface):
    pass

class IOpenIDAssociation(Interface):
    pass

def create_openid_service(request):
    storage = zca.getUtility(IOpenIDStorage)
    return Server(storage, request.get_url('/openid/endpoint'))

class OpenIDProvider(Service):
    classProvides(IService)
    grok.name('openid')

    def index(self):
        self.handler.set_header('Content-Type', 'Application/xrds+xml')
        return '''<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS xmlns:xrds="xri://$xrds" xmlns="xri://$xrd*($v*2.0)">
  <XRD>
  <Service priority="0">
  <Type>http://specs.openid.net/auth/2.0/server</Type>
  <Type>http://openid.net/srv/ax/1.0</Type>
  <URI>%s</URI>
  </Service>
  </XRD>
</xrds:XRDS>
        ''' % (self.request.get_url('/openid/endpoint'))

    @node_name('id')
    def identity(self, user):
        self.handler.set_header('Content-Type', 'Application/xrds+xml')
        return '''<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS xmlns:xrds="xri://$xrds" xmlns="xri://$xrd*($v*2.0)">
  <XRD>
  <Service priority="0">
  <Type>http://specs.openid.net/auth/2.0/signon</Type>
  <Type>http://openid.net/srv/ax/1.0</Type>
  <URI>%s</URI>
  </Service>
  </XRD>
</xrds:XRDS>
        ''' % (self.request.get_url('/openid/endpoint'))

        return self.endpoint()

    def endpoint(self):
        server = create_openid_service(self.request)
        data = dict(urlparse.parse_qsl(self.request.query_string or
                                        self.request.body))
        openid_request = server.decodeRequest(data)
        if openid_request.mode in ['checkid_immediate', 'checkid_setup']:
            if openid_request.immediate:
                openid_response = openid_request.answer(False)
            else:
                openid_response = openid_request.answer(True,
                        identity=self.request.get_url('/openid/id/izhar'))
        else:
            openid_response = server.handleRequest(openid_request)

        vals = {
            'email': 'izhar@inigo-tech.com',
            'firstname': 'izhar',
            'lastname': 'firdaus',
            'language':'en_US',
            'username':'izhar',
            'fullname': 'izhar firdaus'
        }

        ns = {
        'email': 'http://axschema.org/contact/email',
        'firstname': 'http://axschema.org/namePerson/first',
        'fullname': 'http://axschema.org/namePerson',
        'language': 'http://axschema.org/pref/language',
        'lastname': 'http://axschema.org/namePerson/last',
        'username': 'http://axschema.org/namePerson/friendly',
        }
        axns = 'http://openid.net/srv/ax/1.0'
        for k,v in ns.items():
            openid_response.fields.setArg(axns, 'type.%s' % k, v)
            openid_response.fields.setArg(axns, 'value.%s' % k, vals[k])

        response = server.encodeResponse(openid_response)
        self.handler.set_status(response.code)
        for key, value in response.headers.items():
            self.handler.set_header(key, value)

        return response.body

    @method('post')
    @node_name('endpoint')
    def endpoint_post(self):
        return self.endpoint()

