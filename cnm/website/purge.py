
from cnm.website.content.homepage import IHomepage
from plone.app.caching import purge
from z3c.caching.interfaces import IPurgePaths
from z3c.caching.purge import Purge
from zope.component import adapts
from zope.component.hooks import getSite
from zope.event import notify
from zope.interface import implements


class HomepagePurgePaths(purge.ContentPurgePaths):
    implements(IPurgePaths)
    adapts(IHomepage)

    def getRelativePaths(self):
        for path in super(HomepagePurgePaths, self).getRelativePaths():
            yield path

        portal = getSite()
        prefix = portal.absolute_url_path()
        yield prefix + '/emergency_message.json'

def purgeOnEmergencyConfigChange(event):
    portal = getSite()
    homepage = portal['homepage.html']
    notify(Purge(homepage))
