
from Products.CMFCore.utils import getToolByName
from .setuphandlers import moveCheckoutAction

def upgrade_default_from_1_to_2(portal_setup):
    portal = getToolByName(portal_setup, 'portal_url').getPortalObject()
    portal_setup.runImportStepFromProfile('profile-cnm.website:default',
            'actions')
    moveCheckoutAction(portal)
    portal_setup.runImportStepFromProfile('profile-cnm.website:default',
            'workflow')

def upgrade_default_from_2_to_3(portal_setup):
    portal_setup.runImportStepFromProfile('profile-cnm.website:default',
            'workflow')

