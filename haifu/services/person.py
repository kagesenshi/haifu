from haifu.interfaces import IService
from zope.interface import classProvides
import grokcore.component as grok
import zope.component as zca
from haifu.api import Service, method
from haifu import formathelper

class PersonService(Service):
    grok.name('v1/person')
    classProvides(IService)

    @method('post')
    def check(self):
        login = self.get_argument('login', None)
        password = self.get_argument('password', None)

        if login is None:
            return {'ocs': formathelper.meta(False, 102, 'Missing login')}
