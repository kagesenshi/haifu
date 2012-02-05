import tornado.web
import tornado.ioloop
import argh
from zope.configuration.xmlconfig import xmlconfig
from haifu.model import Application
from StringIO import StringIO

def hook_zca():
    xmlconfig(StringIO('''
    <configure xmlns="http://namespaces.zope.org/zope">
        <include package="haifu"/>
    </configure>'''))

def start(port=8888):
    hook_zca()
    application = Application()
#    application = tornado.web.Application([])
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

