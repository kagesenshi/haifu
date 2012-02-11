from haifu.api import Service, require_auth, node_name, method
from haifu.model import Activity, Result
from haifu import util
from haifu.interfaces import IService, IActivityStorage, IPersonStorage
from zope.interface import classProvides
import grokcore.component as grok
import zope.component as zca

class ActivityService(Service):
    grok.name('v1/activity')
    classProvides(IService)

    @require_auth
    def index(self, person_id):
        storage = zca.getUtility(IActivityStorage)

        data = util.extract_data(self.handler, ['page', 'pagesize'])

        limit = int(data['pagesize'] or 0)
        offset = int(limit * (data['page'] or 0))
        activities = [
            a.data() for a in storage.get_activities(
                            person_id, limit, offset)
        ]

        result = Result()

        data = []
        for activity in activities:
            data.append(Activity(**activity))

        if data:
            result.data = data
        return result


    @node_name('index')
    @method('post')
    def post_message(self, person_id):
        data = util.extract_data(self.handler, ['message'])

        if data['message'] is None:
            return Result(False, 101, 'empty message')

        pstorage = zca.getUtility(IPersonStorage)
        person = pstorage.get_person(person_id)

        if person is None:
            return Result(False, 102, 'user not found')

        storage = zca.getUtility(IActivityStorage)
        storage.add_activity(person_id, data)
        return Result()
