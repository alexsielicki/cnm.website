from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from Products.PortalTransforms.transforms.safe_html import VALID_TAGS
from plone.app.controlpanel.filter import XHTML_TAGS


def setupVarious(context):
    if context.readDataFile('cnm.website.various.txt') is None:
        return

    site = context.getSite()

    logger = context.getLogger('cnm.website')

    site.portal_tinymce.link_using_uids = True
    site.portal_tinymce.toolbar_pasteword = True

    # remove "Transform" action
    Image = site.portal_types['Image']
    for action in Image.listActions():
        if action.id == 'transform':
            action.visible = False
            break

    # remove nasty tags
    transform = site.portal_transforms.safe_html
    tags = dict([(tag, 1) for tag in transform.get_parameter_value('nasty_tags')
            if tag not in ('embed', 'object')])
    valid = transform.get_parameter_value('valid_tags')
    
    for t in ('embed', 'object', 'option', 'param', 'center', 'canvas'):
        valid[t] = 1

    attrs = [a for a in transform.get_parameter_value('stripped_attributes')
             if a not in ('frame', 'styles')]

    kwargs = {'valid_tags_key': valid.keys(),
              'valid_tags_value': [str(s) for s in valid.values()],
              'nasty_tags_key': tags.keys(),
              'nasty_tags_value': [str(s) for s in tags.values()],
              'stripped_attributes': attrs,
              }

    transform.set_parameters(**kwargs)
    transform._p_changed = True
    transform.reload()

    unhideEmergencyViewlet(site)
    addImageScales(site)
    moveCheckoutAction(site)

def moveCheckoutAction(site):
    atool = getToolByName(site, 'portal_actions')
    if 'object' in atool.objectIds():
        cat = atool['object']
        if 'iterate_checkout' in cat.objectIds():
            cat.moveObjectToPosition('iterate_checkout',
                    cat.getObjectPosition('folderContents') + 1)


def unhideEmergencyViewlet(site):
    viewlet = "uwosh.simpleemergency"
    manager = "plone.portaltop"

    storage = getUtility(IViewletSettingsStorage)
    skinname = site.getCurrentSkinName()
    hidden = storage.getHidden(manager, skinname)
    if viewlet in hidden:
        hidden = tuple(x for x in hidden if x != viewlet)
        storage.setHidden(manager, skinname, hidden)

def addImageScales(site):
    pp = getToolByName(site, 'portal_properties')
    if 'imaging_properties' in pp.objectIds():
        ip = pp.imaging_properties
        allowed_sizes = list(ip.getProperty('allowed_sizes', []))
        add = True
        for size in allowed_sizes:
            scale, dems = size.strip().split()
            if scale == 'homepage':
                add = False
        if add:
            allowed_sizes.append('homepage 200:140')
            ip.allowed_sizes = tuple(allowed_sizes)

