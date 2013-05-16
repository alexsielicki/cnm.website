import sys
import os
import datetime
import httplib2
from collections import namedtuple
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
REDIRECT_URI = os.environ['OAUTH2_REDIRECT_URI']

CLIENT_TABLEID = os.environ['ANALYTICS_TABLEID']
CLIENT_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
#CLIENT_TABLEID = 'ga:4475786'
#CLIENT_TABLEID can be found at
#https://ga-dev-tools.appspot.com/explorer/?csw=1

Entry = namedtuple("Entry", 'hostname, pagePath, pageTitle, pageviews')

DEFAULT_KEY='_whats_hot'

class Work(object):
    QUERY_RANGE_IN_DAYS = 5
    @staticmethod
    def query(authed_http):
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

    @staticmethod
    def _store_cached_results(portal, results, key=DEFAULT_KEY):
        ut = portal.portal_url.getPortalObject()
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

import transaction
import Acquisition
def main():
    # Generate request
    site = app.Plone
    http = httplib2.Http()
    try:
        credentials = getattr(site, '_oauth2creds', None)
        if credentials is not None:
            #http = credentials.authorize(http)
            expiry = credentials.token_expiry - datetime.datetime.now()
            print 'refresh in', expiry - datetime.timedelta(hours=3)
            if expiry < datetime.timedelta(seconds=0):
                #XXX This should raise a error_log/provoke action to re-auth
                raise RuntimeError("token has expired")
            if expiry < datetime.timedelta(minutes=15) :
                http = credentials.refresh(http)
                setattr(site, '_oauth2creds', credentials)
            else:
                http = credentials.authorize(http)
                print 'authed w/ creds remaining', expiry
            results = Work.query(http)
            Work._store_cached_results(site, results)
            print 'performed query & stored'
            transaction.commit() 
    except:
        raise
if __name__=='__main__':
    """run from cmdline"""
    main()
