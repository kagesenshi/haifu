from haifu.api import Service
from haifu.interfaces import (IService, IVerificationService,
                                IVerificationAction,
                                IVerificationStorage)
from haifu import util
import grokcore.component as grok
import zope.component as zca
from zope.interface import classProvides
import uuid
from zope.event import notify

class Verification(Service):
    grok.name('verify')
    classProvides(IService)

    def index(self):
        key = self.handler.get_argument('key', None)
        if key:
            vs = zca.getUtility(IVerificationService)
            if vs.approve_verification(key):
                return {'ocs': util.meta(message='verification successful')}
        return {'ocs': util.meta(False, 101, 'unknown key')}


class EmailVerificationService(grok.GlobalUtility):
    grok.implements(IVerificationService)

    def send_verification(self, action_id, data, unique_key=None):
        if unique_key is None:
            unique_key = id(data)
        storage = zca.getUtility(IVerificationStorage)
        key = str(uuid.uuid4())
        storage.add_entry(key, action_id, data, unique_key)
        # XXX send email here
        print key
        return key

    def approve_verification(self, verification_id):
        storage = zca.getUtility(IVerificationStorage)
        entry = storage.get_entry(verification_id)
        if not entry:
            return False
        action = zca.getUtility(
            IVerificationAction, 
            name=entry.action_id
        )(entry.data)

        notify(action)
        storage.delete_entry(verification_id)
        return True
