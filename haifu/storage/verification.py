from haifu.interfaces import IVerificationStorage, IVerificationEntry
from haifu.storage.saconfig import named_scoped_session
from haifu.storage.db import VerificationEntry
import grokcore.component as grok
import simplejson

class SQLAlchemyVerificationStorage(grok.GlobalUtility):
    grok.implements(IVerificationStorage)

    def add_entry(self, key, action_id, data, unique_key):
        session = named_scoped_session('haifu.storage')
        # delete old entries with the same unique key
        entries = session.query(VerificationEntry).filter(
            VerificationEntry.unique_key==unique_key)
        for entry in entries:
            session.delete(entry)

        # add new entry
        jsondata = simplejson.dumps(data)
        entry = VerificationEntry(
            key=key, action_id=action_id, data=jsondata,
            unique_key=unique_key
        )

        session.add(entry)

    def get_entry(self, key):
        session = named_scoped_session('haifu.storage')
        entry = session.query(VerificationEntry).filter(
                VerificationEntry.key==key).first()
        return IVerificationEntry(entry) if entry else None

    def delete_entry(self, key):
        session = named_scoped_session('haifu.storage')
        entries = session.query(VerificationEntry).filter(
                VerificationEntry.key==key)
        for entry in entries:
            session.delete(entry)


class VerificationEntryAdapter(grok.Adapter):
    grok.context(VerificationEntry)
    grok.implements(IVerificationEntry)

    def __init__(self, context):
        self.context = context

    @property
    def action_id(self):
        return self.context.action_id

    @property
    def data(self):
        return simplejson.loads(self.context.data)
