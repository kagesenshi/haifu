from haifu.services.openidprovider import IOpenIDStorage, IOpenIDAssociation
from haifu.storage.db import OpenIDAssociation
from haifu.storage.saconfig import named_scoped_session
import grokcore.component as grok
import base64
from openid.association import Association

class SQLALchemyOpenIDStorage(grok.GlobalUtility):
    grok.implements(IOpenIDStorage)

    def storeAssociation(self, server_url, association):
        session = named_scoped_session('haifu.storage')
        assoc = OpenIDAssociation(server_url=server_url,
                                 handle=association.handle,
                                 secret=base64.b64encode(association.secret),
                                 issued=association.issued,
                                 lifetime=association.lifetime,
                                 assoc_type=association.assoc_type)
        session.add(assoc)

    def getAssociation(self, server_url, handle=None):
        session = named_scoped_session('haifu.storage')
        query = session.query(OpenIDAssociation).filter(
                OpenIDAssociation.server_url==server_url)
        if handle:
            query = query.filter(OpenIDAssociation.handle==handle)
        query = query.order_by(OpenIDAssociation.issued.desc())
        assoc = query.first()
        return IOpenIDAssociation(assoc) if assoc else None

    def removeAssociation(self, server_url, handle):
        session = named_scoped_session('haifu.storage')
        query = session.query(OpenIDAssociation).filter(
                OpenIDAssociation.server_url==server_url).filter(
                OpenIDAssociation.handle==handle)

        for i in query:
            session.delete(i)

    def useNonce(self, server_url, timestamp, salt):
        return False

@grok.adapter(OpenIDAssociation)
@grok.implementer(IOpenIDAssociation)
def association_adapter(obj):
    return Association(
        handle=obj.handle,
        secret=base64.b64decode(obj.secret),
        issued=obj.issued,
        lifetime=obj.lifetime,
        assoc_type=obj.assoc_type
    )
