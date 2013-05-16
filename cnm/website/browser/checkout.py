
from zope.component import getMultiAdapter, getAdapters

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError

from Products.statusmessages.interfaces import IStatusMessage

from plone.app.iterate import PloneMessageFactory as _
from plone.app.iterate.browser.checkout import Checkout as CheckoutBase
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import CheckoutException
from plone.app.iterate.interfaces import IWCContainerLocator
from plone.app.iterate.interfaces import IObjectArchiver

class Checkout(CheckoutBase):

    index = ViewPageTemplateFile('checkout.pt')

    def __call__(self):
        context = aq_inner(self.context)

        containers = list(self.containers())
        if len(containers) == 1:
            # Special case for when there's only when folder to select
            self.request.form['form.button.Checkout'] = 1
            self.request.form['checkout_location'] = containers[0]['name']

        # We want to redirect to a specific template, else we might
        # end up downloading a file
        if self.request.form.has_key('form.button.Checkout'):
            control = getMultiAdapter((context, self.request), name=u"iterate_control")
            if not control.checkout_allowed():
                raise CheckoutException(u"Not allowed")

            location = self.request.form.get('checkout_location', None)
            locator = None
            try:
                locator = [c['locator'] for c in self.containers() if c['name'] == location][0]
            except IndexError:
                IStatusMessage(self.request).addStatusMessage(_("Cannot find checkout location"), type='stop')
                view_url = context.restrictedTraverse("@@plone_context_state").view_url()
                self.request.response.redirect(view_url)
                return

            policy = ICheckinCheckoutPolicy(context)
            wc = policy.checkout(locator())

            # we do this for metadata update side affects which will update lock info
            context.reindexObject('review_state')

            IStatusMessage(self.request).addStatusMessage(_("Draft copy created"), type='info')
            edit_url = wc.restrictedTraverse("@@plone_context_state").object_url() + '/edit'
            self.request.response.redirect(edit_url)
        elif self.request.form.has_key('form.button.Cancel'):
            view_url = context.restrictedTraverse("@@plone_context_state").view_url()
            self.request.response.redirect(view_url)
        else:
            return self.index()
