import tornado.web
import tornado.ioloop
import argh
from zope.configuration.xmlconfig import xmlconfig
import zope.component.event # enable event triggering
from haifu.model import Application
from haifu.event import StartupEvent
from StringIO import StringIO
from zope.event import notify

def hook_zca():
    xmlconfig(StringIO('''
    <configure xmlns="http://namespaces.zope.org/zope">
        <include package="haifu"/>
    </configure>'''))

def start(port=8888):
    hook_zca()
    application = Application()
    event = StartupEvent()
    notify(event)
    print "STARTED!!"
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

@argh.command
def fg():
    start()

def main():
    parser = argh.ArghParser()
    parser.add_commands([fg])
    parser.dispatch()

