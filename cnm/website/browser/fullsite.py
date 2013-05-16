from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class FullSite(object):
	def __call__(self):
		self.request.response.setCookie("no-mobile-please", "true")
		self.request.response.redirect("/")
