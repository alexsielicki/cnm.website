import sys
import datetime
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from AccessControl.SecurityManagement import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.PythonScript import PythonScript

PS_ID = 'analytics_filter'


class ControlPanelForm(object):

    index = ViewPageTemplateFile('controlpanel.pt')

    label = u"CNM Analytics"

    def get_profiles(self):
        return []
        voc = getUtility(
            IVocabularyFactory, 
            'collective.googleanalytics.Profiles')(self.context)
        return voc

    def get_filter_script(self):
        if PS_ID not in self.context.objectIds():
            self.context._setObject(PS_ID, PythonScript(PS_ID))
            self.context[PS_ID].ZPythonScript_edit('entries', '')
            self.context[PS_ID].ZPythonScript_setTitle(
                'Return a list of relative paths to filter')

        return self.context[PS_ID]

    def canModifyScript(self):
        return getSecurityManager().checkPermission(
            'Manage portal', self.context)

    def __call__(self):
        script = self.get_filter_script()
        #analytics = getToolByName(self.context, 'portal_analytics')
        portal = self.context

        request = self.request

        if 'save.profile' in request.form:
            profile = request.form['profile']
            if profile == '--empty--':
                portal.cnm_profile = None
            else:
                portal.cnm_profile = profile

            request.response.redirect('@@cnmanalytics-controlpanel')
            return

        if 'save.blocked' in request.form:
            pages = request.form.get('page-path',())
            block = request.form.get('page', '')
            if block:
                if isinstance(pages, basestring):
                    pages = (pages,)
                if isinstance(block, basestring):
                    block = (block,)

                blocked = getattr(portal, 'cnm_blocked', [])

                for page in pages:
                    if page in block:
                        blocked.append(page)
                    elif page in blocked:
                        blocked.remove(page)

                portal.cnm_blocked = blocked
                request.response.redirect('@@cnmanalytics-controlpanel')
                return

        if 'save.unblocked' in request.form:
            unblock = request.form.get('path', '')
            if unblock:
                if isinstance(unblock, basestring):
                    unblock = (unblock,)

                blocked = getattr(portal, 'cnm_blocked', [])
                for page in unblock:
                    if page in blocked:
                        blocked.remove(page)
    
                portal.cnm_blocked = blocked
                request.response.redirect('@@cnmanalytics-controlpanel')
                return

        self.cnm_filtered = []
        self.cnm_profile = getattr(portal, 'cnm_profile', None)
        self.cnm_blocked = getattr(portal, 'cnm_blocked', ())
        self.cnm_blocked = set(self.cnm_blocked)
        #self.profiles = self.get_profiles()

        _results = getattr(self.context, '_whats_hot', [])

        if _results:
        #if self.cnm_profile is not None and self.cnm_profile in self.profiles:
            d1 = datetime.date.today()
            d2 = datetime.date(d1.year-1, d1.month, d1.day)
            """
            q = {'metrics': 'ga:pageviews', 'sort': '-ga:pageviews',
                 'max_results': 40, 
                 'dimensions': 'ga:hostname,ga:pagePath,ga:pageTitle',
                 'start_date': d2,
                 'end_date': d1,
                 
                 'ids': self.cnm_profile,
                 }
             
            entries = []
            for entry in analytics.makeClientRequest(
                'data', 'GetData', **q).entry:

                if isinstance(entry.pageTitle.value, str):
                    title = unicode(entry.pageTitle.value, 'utf-8')
                else:
                    title = entry.pageTitle.value

                entries.append(
                    {'href': 'http://%s%s'%(entry.hostname,entry.pagePath),
                     'views': entry.pageviews,
                     'path': '%s'%entry.pagePath,
                     'title': title})
            """
            entries=_results
            try:
                self.cnm_filtered = script(entries)
                if not self.cnm_filtered:
                    self.cnm_filtered = ()
            except:
                info = sys.exc_info()
                try:
                    self.context.error_log.raising(info)
                except:
                    pass

            self.entries = entries
        else:
            self.entries = []

        return self.index()
