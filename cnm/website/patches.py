import logging
from AccessControl import Unauthorized
from Products.CMFDefault.utils import IllegalHTML
from Products.PortalTransforms.transforms.safe_html import StrippingParser
from Products.PortalTransforms.transforms.safe_html import hasScript
from Products.PortalTransforms.utils import safeToInt
from Products.Archetypes import Field
from cgi import escape
from cnm.website import CNMMessageFactory as _

logger = logging.getLogger('cnm.website.patches')


def _pfg_make_file(self, id, title='', file='', instance=None):
    """File content factory. Awful practice passing in a builtin, file in signature"""
    if (not isinstance(file, str)
        and not (hasattr(file, '__class__') and file.__class__ is Pdata)
        and getattr(file, 'seek', None) is None):
        logger.info("Invalid file value, using empty string as value.")
        file = ''
    return self.content_class(id, title, file)

#Field.FileField._make_file = _pfg_make_file

#logger.warn('Patching Produts.Archetypes.Field.FileField._make_file.'
            #'cnm.website.patches._pfg_make_file')


def unknown_starttag(self, tag, attrs):
    """ Delete all tags except for legal ones.
    """
    if self.suppress:
        return

    if tag in self.valid:
        self.result.append('<' + tag)

        remove_script = getattr(self, 'remove_javascript', True)

        for k, v in attrs:
            if remove_script and k.strip().lower().startswith('on'):
                if not self.raise_error:
                    continue
                else:
                    raise IllegalHTML('Script event "%s" not allowed.' % k)
            elif remove_script and hasScript(v):
                if not self.raise_error:
                    continue
                else:
                    raise IllegalHTML('Script URI "%s" not allowed.' % v)
            else:
                # escape attribute values to compensate for a change in
                # SGMLParser on python 2.6 - josh
                self.result.append(' %s="%s"' % (k, escape(v)))

        #UNUSED endTag = '</%s>' % tag
        if safeToInt(self.valid.get(tag)):
            self.result.append('>')
        else:
            self.result.append(' />')
    elif tag in self.nasty:
        self.suppress = True
        if self.raise_error:
            raise IllegalHTML('Dynamic tag "%s" not allowed.' % tag)
    else:
        # omit tag
        pass

#StrippingParser.unknown_starttag = unknown_starttag
#logger.warn('Patched Products.PortalTransforms.transforms.safe_html.Stripping'
#            'Parser.unknown_starttag')

from uwosh.simpleemergency.browser import controlpanel as se_controlpanel


def get_display_emergency(self):
    return self.props.getProperty('display_emergency', False)


def set_display_emergency(self, value):
    self.props.display_emergency = value

se_adapter = se_controlpanel.SimpleEmergencyControlPanelAdapter
se_adapter.get_display_emergency = get_display_emergency
se_adapter.set_display_emergency = set_display_emergency
se_adapter.display_emergency = property(se_adapter.get_display_emergency,
                                        se_adapter.set_display_emergency)

se_controlpanel.EmergencyNotificationConfigurationForm.form_name = _(
    u'CNM Emergency Notification')

from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFCore.utils import _checkPermission
from cnm.website.permissions import DeleteThisObject


def manage_delObjects(self, ids=[], REQUEST=None):
    """ Additional security check. """
    if isinstance(ids, basestring):
        ids = [ids]
    msg = 'You do not have the permissions necessary to delete %s.'
    for id in ids:
        item = self._getOb(id)
        if not _checkPermission(DeleteThisObject, item):
            raise Unauthorized(message=msg % id,
                               needed={'permission': DeleteThisObject})
    return self.__cnm_original_manage_delObjects(ids=ids, REQUEST=REQUEST)

if not hasattr(PortalFolderBase, '__cnm_patched_manage_delObjects__'):
    PortalFolderBase.__cnm_patched_manage_delObjects__ = True
    PortalFolderBase.__cnm_original_manage_delObjects = \
        PortalFolderBase.manage_delObjects
    PortalFolderBase.manage_delObjects = manage_delObjects
    logger.warn('Patched PortalFolderBase.manage_delObjects.')

#For expiry date
from time import gmtime, strftime


def _mp_call__(self):
    resp = self.request.response
    imagedata = self.imageeditor.get_current_image_data()
    resp.setHeader('Content-Type', 'image/jpeg')
    resp.setHeader('Content-Length', len(imagedata))
    resp.setHeader('Last-Modified',
                   strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime()))

    # Ensure IE does not cache
    resp.setHeader('Pragma', 'no-cache')
    resp.setHeader('Cache-Control', 'no-cache')
    resp.setHeader('Expires', 'Tue, 06 Aug 2002 22:18:44 GMT')

    resp.write(imagedata)
from Products.ImageEditor.browser import imageeditor
imageeditor.ShowCurrentEdit.__call__ = _mp_call__

logger.warn('Patching Products.ImageEditor.browser.imageeditor.'
            'ShowCurrentEdit.__call__ with response headers')
