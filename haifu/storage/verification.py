from haifu.interfaces import IVerificationStorage, IVerificationEntry
from haifu.storage.saconfig import named_scoped_session
from haifu.storage.db import VerificationEntry
from sqlalchemy import and_
import grokcore.component as grok
import simplejson
from datetime import datetime, timedelta

class SQLAlchemyVerificationStorage(grok.GlobalUtility):
    grok.implements(IVerificationStorage)

    def add_entry(self, key, action_id, data, unique_key, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow()
        session = named_scoped_session('haifu.storage')
        # delete old entries with the same unique key
        entries = session.query(VerificationEntry).filter(
            and_(VerificationEntry.action_id==action_id,
            VerificationEntry.unique_key==unique_key))
        for entry in entries:
            session.delete(entry)

        # add new entry
        jsondata = simplejson.dumps(data)
        entry = VerificationEntry(
            key=key, action_id=action_id, data=jsondata,
            unique_key=unique_key,
            timestamp=timestamp
        )

        session.add(entry)

    def has_entry(self, action_id, unique_key):
        session = named_scoped_session('haifu.storage')
        if session.query(VerificationEntry).filter(
                and_(VerificationEntry.action_id==action_id,
                VerificationEntry.unique_key==unique_key)
            ).first():
            return True
        return False

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

    def expire_entries(self, age=24):
        delta = datetime.timedelta(0,age*60*60)
        youngest = datetime.utcnow() - delta
        entries = session.query(VerificationEntry).filter(
            VerificationEntry.timestamp<=youngest
        )
        for entry in entries:
            session.delete(entry)

    def get_key_for(self, unique_key):
        session = named_scoped_session('haifu.storage')
        entry = session.query(VerificationEntry).filter(
            VerificationEntry.unique_key==unique_key
        ).first()
        if entry:
            return entry.key
        return None

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
