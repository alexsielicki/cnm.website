import logging

from zope import component, interface
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.component.hooks import getSite
from zope.lifecycleevent import IObjectAddedEvent
from zope.lifecycleevent import IObjectModifiedEvent

from z3c.caching.purge import Purge

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender

from Products.Archetypes import atapi
from Products.ATContentTypes.interfaces import IATNewsItem
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.interfaces import IAfterTransitionEvent

from cnm.website.content.homepage import IHomepage

logger = logging.getLogger(__name__)

BREAKING = '1'
EMERGENCY = '2'
FEATURED = '3'
NORMAL = '4'

PRIORITIES = atapi.DisplayList(
    (('4', 'Normal'),
     #('3', 'Featured News'),
     ('1', 'Breaking News'),
     ('2', 'Emergency News'),))

class ExtStringField(ExtensionField, atapi.StringField):
    pass

class NewsItemExtender(object):
    component.adapts(IATNewsItem)
    interface.implements(IOrderableSchemaExtender)

    fields = (
        ExtStringField(
            "news_priority",
            description='this is test',
            vocabulary=PRIORITIES,
            write_permission = 'CNM: News Priority',
            widget = atapi.SelectionWidget(
                format = 'radio',
                label="Select News Priority")),
        )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, original):
        default = original['default']
        if 'news_priority' in default:
            default.remove('news_priority')
            default.insert(2, 'news_priority')
        return original


@component.adapter(IATNewsItem, IObjectAddedEvent)
def onCreate(ob, ev):
    """ On save.
        If ob is new & we have emergency/breaking; set and perform action.
        if ob has previous value & going from emergency/breaking to normal
        save historical_news_priorty.
    """
    if 'portal_factory' in ob.absolute_url():
        return

    if getattr(ob, '_v_onsave', None) is not None:
        return

    # calculate newspriority & mark historical
    form_np = ob.REQUEST.get('news_priority', '')
    obj_np = getattr(ob, 'news_priority', '')

    if form_np:
        ob.historical_news_priority = (form_np,)
    else:
        ob.historical_news_priority = (NORMAL,)
        ob.news_priority = NORMAL

    if form_np in (EMERGENCY, BREAKING) and obj_np in ('', NORMAL):
        ob.portal_workflow.doActionFor(ob, 'publish')

        portal = getSite()
        homepage = portal['homepage.html']
        notify(Purge(homepage))

    ob._v_onsave = 1

@component.adapter(IATNewsItem, IObjectModifiedEvent)
def onModify(ob, ev):
    portal = getSite()
    if ob.news_priority in (EMERGENCY, BREAKING):
        wftool = getToolByName(portal, 'portal_workflow')
        state = wftool.getInfoFor(ob, 'review_state')
        if state in ('draft', 'pending'):
            try:
                wftool.doActionFor(ob, 'publish')
            except WorkflowException:
                # working copies don't have a publish transition
                fmt = 'Could not publish %s. Possible working copy?'
                logger.info(fmt % '/'.join(ob.getPhysicalPath()))
    # Always purge homepage because we may have removed emergency or
    # breaking priority
    homepage = portal['homepage.html']
    notify(Purge(homepage))

    hist_np = getattr(ob, 'historical_news_priority', None)
    if hist_np is None:
        hist_np = ob.historical_news_priority = ()
    if ob.news_priority not in hist_np:
        ob.historical_news_priority += (ob.news_priority,)
        ob.reindexObject(idxs=['historical_news_priority'])

@component.adapter(IATNewsItem, IAfterTransitionEvent)
def afterTransitionHandler(ob, ev):
    logger.info("bypassing transition")
    return

    portal = getSite()
    id = component.getUtility(IIntIds).queryId(ob)
    if id is None:
        return

    state = ev.new_state.id
    news_priority = getattr(ob, 'news_priority', '')
    if state == 'published':
        historical = getattr(ob, 'historical_news_priority', ())
        if historical and not isinstance(historical, tuple):
            ob.historical_news_priority = historical = (historical,)
        if news_priority and news_priority not in historical:
            ob.historical_news_priority = historical + (news_priority,)
            ob.reindexObject(idxs=['historical_news_priority'])

    for hp in portal.contentValues():
        if IHomepage.providedBy(hp):
            links = hp.news_links2 #XXX Hardcoded must fix
            if links is None:
                links = []

            if state == 'published':
                if id not in links and news_priority == '3':
                    links.append(id)
                    hp.news_links2 = links
            else:
                if id in hp.news_links2:
                    links.remove(id)
                    hp.news_links2 = links
