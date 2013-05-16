import sys
import logging
import datetime
from zope.intid.interfaces import IIntIds
from zope.component import getUtility, getMultiAdapter
from zope.schema.interfaces import IVocabularyFactory
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

log = logging.getLogger('cnm.website')

BN_NEWS = '1'
EM_NEWS = '2'
FE_NEWS = '3'
NORMAL = '4'

class Homepage(object):

    index = ViewPageTemplateFile('homepage.pt')

    def get_news(self, total=10):
        ctool = getToolByName(self.context, 'portal_catalog')
        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        path = portal_state.navigation_root_path()

        news = []
        for ni in ctool(portal_type='News Item',
                        path=path,
                        sort_on='Date',
                        state='published',
                        news_priority=BN_NEWS):
            item = ni.getObject()
            img = None
            try:
                img = item.restrictedTraverse('image_homepage')
            except AttributeError:
                pass #no image/scale

            news.append({'item': item, 'img': img, 'br': True})

        links = getattr(self.context, 'news_links2', None) 
        if not links:
            return news

        ids = getUtility(IIntIds)
        for id in self.context.news_links2[:5]:
            ob = ids.queryObject(id)
            img = None
            try:
                img = ob.restrictedTraverse('image_homepage')
            except AttributeError:
                pass #no image/scale
            if ob is not None:
                news.append({'item': ob, 'img': img, 'br': False})

        return news

    def __call__(self):
        entries = []
        text_removed_entries = []
        request = self.request
        portal = getToolByName(self.context, 'portal_url').getPortalObject()

        self.cnm_profile = getattr(portal, 'cnm_profile', None)
        self.cnm_blocked = getattr(portal, 'cnm_blocked', ())

        _cache = getattr(portal, '_whats_hot', [])
        if _cache: #self.cnm_profile is not None and self.cnm_profile in voc:
            d1 = datetime.date.today()
            d2 = datetime.date(d1.year-1, d1.month, d1.day)

            for entry in _cache: #.entry:
                if entry['path'] in self.cnm_blocked:
                    continue
                entries.append(entry)
            try:
                if 'analytics_filter' in portal.objectIds():
                    cnm_filtered = portal.analytics_filter(entries)
                    if cnm_filtered:
                        entries = [item for item in entries 
                                   if item['path'] not in cnm_filtered]
            except:
                info = sys.exc_info()
                try:
                    self.context.error_log.raising(info)
                except:
                    pass

            for entry in entries:
                entry['title'] = entry['title'].replace(' Central New Mexico Community College', '')
                entry['title'] = entry['title'].replace(u'\u2014', '')
                text_removed_entries.append(entry) 

        self.entries = text_removed_entries
        return self.index()
