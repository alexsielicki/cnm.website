from zope import schema
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from plone.directives import form, dexterity
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Products.CMFCore.utils import getToolByName


class IHomepage(form.Schema):

    title = schema.TextLine(
        title=u'Title', required=True)

    description = schema.Text(
        title=u'Description', required=False)

    news_links2 = schema.List(
        title=u'Featured News', required=False,
        description=(u'Left column is the last 30 days of published news. ' 
                    'The right column contains the currently selected ' 
                    'homepage news. Breaking news takes priority.'), 
        value_type=schema.Choice(vocabulary='cnm-newsItems2'))


def newsVoc(context, tag):
    ids = getUtility(IIntIds)
    catalog = getToolByName(context, 'portal_catalog')

    news = []
    for ni in catalog(portal_type='News Item',
                      sort_on='Date',
                      news_priority=tag,
                      review_state = 'published',
                      sort_order='reverse'):
        obj = ni.getObject()
        id = ids.queryId(obj)
        if id is None:
            ids.register(obj)
            id = ids.getId(obj)
        news.append(SimpleTerm(id, str(id), ni.Title))

    return SimpleVocabulary(news)


def newsVoc1(context):
    return newsVoc(context, '2')

def newsVoc2(context):
    """ cnm-newsItems2 """
    return newsVoc(context, ('3','4'))

def newsVoc3(context):
    return newsVoc(context, '1')
