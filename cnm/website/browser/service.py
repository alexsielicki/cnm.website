CLIENT_ID='17533032080-9u3gvr2gf6t2dnjs8uoih5pvrki9n21m.apps.googleusercontent.com'
EMAIL_ADDR='17533032080-9u3gvr2gf6t2dnjs8uoih5pvrki9n21m@developer.gserviceaccount.com'
PUB_KEYPRINT = '9aa2b0570864561bb9cb837eae881f2d5e2078da'
ANALYTICS_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
import datetime
import httplib2
import pprint
import sys

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials

def main():
    """ ids is internal id for API. as a user who has analytics access
        and has enabled it in console. you can get your id in the explorer
        https://ga-dev-tools.appspot.com/explorer/?csw=1
    """
    p = app.Plone
    key_file = p['9aa2b0570864561bb9cb837eae881f2d5e2078da-privatekey.p12'] 
    key = key_file.data

    credentials = SignedJwtAssertionCredentials(EMAIL_ADDR, key, ANALYTICS_SCOPE)
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('analytics', 'v3', http=http)
    q = {'metrics': 'ga:pageviews', 
         'sort': '-ga:pageviews',
         'max_results': 20,
         'dimensions': 'ga:hostname,ga:pagePath,ga:pageTitle',
         'start_date': '2011-08-02', #datetime.date(2011, 8, 2),
         'end_date': '2012-08-02', #datetime.date(2012, 8, 2),
         'ids' : 'ga:209197'}

    query = service.data().ga().get(**q)
    results = query.execute()
main()
