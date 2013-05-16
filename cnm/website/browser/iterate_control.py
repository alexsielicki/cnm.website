import zope.component
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from plone.app.iterate import interfaces
from plone.app.iterate.browser import control


class Control(control.Control):

    def is_working_copy(self, ob=None):
        """ """
        if ob is None:
            ob = self.context
        return self.get_original(ob) is not None

    def checkin_allowed(self):
        """ Check if a checkin is allowed. """
        context = aq_inner(self.context)
        user = getSecurityManager().getUser()

        if not interfaces.IIterateAware.providedBy(context):
            return False

        archiver = interfaces.IObjectArchiver(context)
        if not archiver.isVersionable():
            return False

        original = self.get_original(context)
        if original is None:
            return False

        user_roles = set(user.getRolesInContext(context))
        if user_roles.isdisjoint(set(['Manager', 'Reviewer',
                                      'Site Administrator'])):
            return False

        return True

    def checkout_allowed(self):
        """ Check if a checkout is allowed. """
        if not super(Control, self).checkout_allowed():
            return False

        context = aq_inner(self.context)
        user = getSecurityManager().getUser()

        user_roles = set(user.getRolesInContext(context))
        if user_roles.isdisjoint(set(['Manager', 'Reviewer', 'Editor',
                                      'Site Administrator', 'Contributor',
                                      ])):
            return False

        found_container = False
        for name, locator in zope.component.getAdapters(
                (context,), interfaces.IWCContainerLocator):
            if locator.available:
                found_container = True
                break
        if not found_container:
            return False

        return True
