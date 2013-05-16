import json
from Products.CMFCore.utils import getToolByName
EM_NEWS = '2'

EM_HTML = '''
<div id="emergency-news">
    <h1>CNM Emergency notification:</h1>
    %(EMERGENCY)s
</div>
'''

class EmergencyMessage(object):

    def message(self):
        """ """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        pprops = getToolByName(self.context, 'portal_properties')
        props = pprops.uwosh_simpleemergency_properties
        setHeader = self.request.response.setHeader
        setHeader('Cache-Control', 'no-cache')
        setHeader('Content-Type', 'application/json')
        data = dict()
        data['message'] = props.getProperty('emergency_message', '')
        data['last_updated'] = props.getProperty('last_updated', '')
        data['show_on_all_pages'] = props.getProperty('show_on_all_pages',
                False)
        data['display_emergency'] = props.getProperty('display_emergency',
                False)
        data['portal_url'] = portal_url = portal.absolute_url()
        dp = portal.getDefaultPage()
        dp = dp and dp or portal.getLayout()
        data['alt_portal_url'] = portal_url.rstrip('/') + '/' + dp

        data['items'] = []
        for emergency in portal.portal_catalog(portal_type='News Item',
                                               state='published',
                                               news_priority=EM_NEWS,
                                               sort_on='Date'):
            url, title, desc = (emergency.getURL(), emergency.Title, 
                                emergency.Description)
            html = ('<li><a href="%(URL)s"><strong>%(TITLE)s</strong>'
                    '<br>Read more... </a></li>') % {'URL':url,'TITLE':title}
            data['items'].append({'url':url,
                                  'title':title,
                                  'description':desc,
                                  'html':html})
        if data['items']:
            message = ' '.join([frag['html'] for frag in data['items']])
            data['message'] = '<ul>%s</ul>' % message
        else:
            if data['display_emergency'] is False:
                data['message'] = ''
        if data['message']:
            data['html'] = EM_HTML % {'EMERGENCY':data['message']}
        return json.dumps(data)

