import tornado.web
import tornado.ioloop
import tornado.process
import tornado.netutil
from tornado.httpserver import HTTPServer
import argh
from zope.configuration.xmlconfig import xmlconfig
import zope.component.event # enable event triggering
import grokcore.component as grok
from haifu.model import Application
from haifu.event import StartupEvent, InitializeEvent
from haifu.interfaces import IConfiguration
from StringIO import StringIO
from zope.event import notify
import sys, os
from ConfigParser import ConfigParser
from zope.component import getGlobalSiteManager

def hook_zca():
    xmlconfig(StringIO('''
    <configure xmlns="http://namespaces.zope.org/zope">
        <include package="haifu"/>
    </configure>'''))

def hook_config(cp):
    gsm = getGlobalSiteManager()
    gsm.registerUtility(cp, IConfiguration)

def start(port=8888):
    hook_zca()
    notify(InitializeEvent())
    application = Application()
    notify(StartupEvent())
    print "STARTED!!"
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

@argh.command
def fg():
    start()

def main():
    # extract out -C parameter
    config = '/etc/haifu.cfg'
    argv = []
    skip = False
    for index, item in enumerate(sys.argv):
        if skip == True:
            skip = False
            continue
        if item == '-C':
            config = sys.argv[index+1]
            skip = True
        elif item.startswith('-C'):
            config = item[2:]
        else:
            argv.append(item)

    cp = ConfigParser()
    if not os.path.exists(config):
        print 'Warning: Config Not Found : %s' % path
    else:
        cp.read(config)
    hook_config(cp)
    parser = argh.ArghParser()
    parser.add_commands([fg])
    parser.dispatch(argv[1:])
