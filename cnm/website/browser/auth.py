import sys
import os
import datetime
import httplib2
import logging

from collections import namedtuple
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from cmdauth import Work

logger = logging.getLogger(__name__)

try:
    CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
    CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
    REDIRECT_URI = os.environ['OAUTH2_REDIRECT_URI']
    CLIENT_TABLEID = os.environ['ANALYTICS_TABLEID']
except KeyError:
    CLIENT_ID = REDIRECT_URI = CLIENT_SECRET = CLIENT_TABLEID = 'NOT SETUP'
    logger.info("OAUTH environment not found; no OAUTH features will work")

CLIENT_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
#https://ga-dev-tools.appspot.com/explorer/?csw=1

DEFAULT_KEY='_whats_hot'

Entry = namedtuple("Entry", 'hostname, pagePath, pageTitle, pageviews')

class OAuth2(object):
    index = ViewPageTemplateFile('auth.pt')
    flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                           client_secret=CLIENT_SECRET,
                           scope=CLIENT_SCOPE)

    def _store_cached_results(self, results, key=DEFAULT_KEY):
        ut = self.context.portal_url.getPortalObject()
        cache = []
        for entry in results:
            if isinstance(entry.pageTitle, str):
                title = unicode(entry.pageTitle, 'utf-8')
            else:
                title = entry.pageTitle

            cache.append(
                {'href': 'http://%s%s'%(entry.hostname,entry.pagePath),
                 'views': entry.pageviews,
                 'path': '%s'%entry.pagePath,
                 'title': title})
        setattr(ut, key, cache)
        return cache

    def _get_cached_results(self, key=DEFAULT_KEY):
        ut = self.context.portal_url.getPortalObject()
        return getattr(ut, key, None)

    def _store_creds(self, credentials):
        ut = self.context.portal_url.getPortalObject()
        ut._oauth2creds = credentials

    def _get_creds(self):
        ut = self.context.portal_url.getPortalObject()
        http = httplib2.Http()
        credentials = getattr(ut, '_oauth2creds', None)
        return credentials

    def _query_analytics(self, authed_http):
        service = build('analytics', 'v3', http=authed_http)
        interval = datetime.timedelta(days=Work.QUERY_RANGE_IN_DAYS)
        end = datetime.datetime.now()
        start = end - interval
        end = end.date()
        start = start.date()
        q = {'metrics': 'ga:pageviews',
                 'sort': '-ga:pageviews',
                 'max_results': 50,
                 'dimensions': 'ga:hostname,ga:pagePath,ga:pageTitle',
                 'start_date': str(start),
                 'end_date': str(end),
                 'ids' : CLIENT_TABLEID}
        query = service.data().ga().get(**q)
        _results = query.execute()
        results = map(Entry._make, _results['rows'])
        return results

    def _refresh_if_needed(self, credentials):
        """ refresh when 10 minutes remaining """
        expiry = credentials.token_expiry - datetime.datetime.now()
        http = None

        print 'refresh in', expiry - datetime.timedelta(hours=3)

        if expiry < datetime.timedelta(seconds=0):
            raise RuntimeError("token has expired")
        if expiry < datetime.timedelta(minutes=15) :
            http = httplib2.Http()
            http = credentials.refresh(http)
            self._store_creds(credentials)
            print 'refreshed creds & store', expiry
        return http 

    def __call__(self):
        context = self.context
        request = self.request
        if request.get('reset', None):
            setattr(context.portal_url.getPortalObject(), '_oauth2creds', None)
        self.credentials = credentials = False
        self.results = results = []
        self.auth_uri = auth_uri = ''
        self.stored_credentials = stored_credentials = self._get_creds()

        oauth2code = request.get('code', None)

        if oauth2code is None and stored_credentials is None:
            self.auth_uri = auth_uri = OAuth2.flow.step1_get_authorize_url(redirect_uri=REDIRECT_URI)
            return self.index()

        if oauth2code is not None:
            credentials = OAuth2.flow.step2_exchange(oauth2code)
            http = httplib2.Http()
            http = credentials.authorize(http)
            analytics_results = self._query_analytics(http)
            self._store_creds(credentials)
            print 'oauth2call hit with "code" in request'
        else:
            print 'oauth2call hit without "code" in request'
            http = self._refresh_if_needed(stored_credentials)
            analytics_results = self._query_analytics(http)
            self._store_cached_results(analytics_results)

        self.auth_uri = auth_uri
        self.stored_credentials = stored_credentials
        self.results = analytics_results
        self.credentials = credentials

        return self.index()

import transaction
import Acquisition
def main():
    # Generate request
    site = app.Plone
    http = httplib2.Http()
    try:
        credentials = getattr(site, '_oauth2creds', None)
        if credentials is not None:
            http = credentials.authorize(http)
            expiry = credentials.token_expiry - datetime.datetime.now()
            print 'refresh in', expiry - datetime.timedelta(hours=3)
            if expiry < datetime.timedelta(seconds=0):
                raise RuntimeError(message="token has expired")
            if expiry < datetime.timedelta(hours=3) :
                http = credentials.refresh(http)
                setattr(site, '_oauth2creds', credentials)
            else:
                http = credentials.authorize(http)
                print 'authed w/ creds remaining', expiry
        transaction.commit() 
    except:
        raise
if __name__=='__main__':
    """run from cmdline"""
    main()
