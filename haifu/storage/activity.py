from haifu.interfaces import IActivityStorage, IActivity
from haifu.storage.db import Activity
from haifu.storage.saconfig import named_scoped_session
import grokcore.component as grok
from datetime import datetime
import simplejson

HARD_LIMIT=100

class SQLAlchemyActivityStorage(grok.GlobalUtility):
    grok.implements(IActivityStorage)

    def add_activity(self, person_id, data, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow()

        session = named_scoped_session('haifu.storage')

        jsondata = simplejson.dumps(data)
        activity = Activity(
            person_id = person_id,
            data = jsondata,
            timestamp = timestamp
        )

        session.add(activity)

    def get_activities(self, person_id, limit=None, offset=None):

        session = named_scoped_session('haifu.storage')
        query = session.query(Activity).filter(
                    Activity.person_id==person_id
                ).order_by(Activity.timestamp.desc())
        
        if limit is None or limit==0 or limit > HARD_LIMIT:
            limit = HARD_LIMIT
        query.limit(limit)
        if offset is not None or offset != 0:
            query.offset(offset)

        return [IActivity(i) for i in query]


class ActivityAdapter(grok.Adapter):
    grok.context(Activity)
    grok.implements(IActivity)

    def __init__(self, context):
        self.context = context

    def data(self):
        data = simplejson.loads(self.context.data)
        data['id'] = self.context.id
        return data
