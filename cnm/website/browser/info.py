
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import RequestReview
from Products.CMFCore.permissions import ReviewPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.iterate.browser.info import BaselineInfoViewlet \
        as BaseBaselineInfoViewlet
from plone.app.iterate.browser.info import CheckoutInfoViewlet \
        as BaseCheckoutInfoViewlet


class BaselineInfoViewlet(BaseBaselineInfoViewlet):

    index = ViewPageTemplateFile('info_baseline.pt')

    def render(self):
        sm = getSecurityManager()
        context = self.context
        working_copy = self.working_copy()
        if working_copy is not None and (
                sm.checkPermission(RequestReview, context) or
                sm.checkPermission(RequestReview, working_copy) or
                sm.checkPermission(ReviewPortalContent, context) or
                sm.checkPermission(ReviewPortalContent, working_copy) or
                sm.checkPermission(ModifyPortalContent, context) or
                sm.checkPermission(ModifyPortalContent, working_copy)):
            return self.index()
        else:
            return ""

class CheckoutInfoViewlet(BaseCheckoutInfoViewlet):

    index = ViewPageTemplateFile('info_checkout.pt')

    def render(self):
        sm = getSecurityManager()
        context = self.context
        if self.baseline() is not None and (
            sm.checkPermission(RequestReview, context) or
            sm.checkPermission(ReviewPortalContent, context) or
            sm.checkPermission(ModifyPortalContent, context)):
            return self.index()
        else:
            return ""

