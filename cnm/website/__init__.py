
from zope.i18nmessageid import MessageFactory

CNMMessageFactory = MessageFactory('cnm')

def initialize(context):
    import permissions
    import patches

def bpython_init(self, *args):
    """ custom entry-point for bin/instance to use bpython """
    import os
    bembed = "import bpython; bpython.embed(locals_=locals())"
    cmdline = self.get_startup_cmd(self.options.python, bembed,
                                       pyflags = '-i', )
    print ('Starting debugger (the name "app" is bound to the top-level '
           'Zope object)')
    os.system(cmdline)
