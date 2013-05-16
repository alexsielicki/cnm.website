
import urlparse
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from cnm.website.newsitem import BREAKING, EMERGENCY, NORMAL

class BaseNewsItemsRSS(object):

    title = u'News RSS'
    description = u'News RSS'

    index = ViewPageTemplateFile('rss.pt')

    @property
    def url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return portal_url.rstrip('/') + '/news'

    @property
    def items(self):
        brains = self.doSearch()
        items = list()
        for brain in brains:
            items.append(dict(title=brain.Title, description=brain.Description,
                    url=brain.getURL(), pubdate=brain.effective.rfc822()))
        return items

    def __call__(self):
        setHeader = self.request.response.setHeader
        setHeader('Content-Type', 'text/xml; charset=UTF-8')
        setHeader('Cache-Control', 's-max-age=300')
        return self.index()


class OfficialNewsItemsRSS(BaseNewsItemsRSS):

    title = u'Official News RSS'
    description = u'Official News RSS'

    def doSearch(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(Type='News Item',
                         review_state='published',
                         historical_news_priority=(BREAKING,EMERGENCY,NORMAL),
                         sort_on="Date",
                         #sort_on="effective",
                         sort_order='descending')


class AllNewsItemsRSS(BaseNewsItemsRSS):

    def doSearch(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(Type='News Item',
                         review_state='published',
                         sort_on="Date",
                         #sort_on="effective",
                         sort_order='descending')


