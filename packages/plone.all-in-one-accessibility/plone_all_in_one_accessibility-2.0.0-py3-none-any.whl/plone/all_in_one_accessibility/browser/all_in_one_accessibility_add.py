from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView

class AllInOneAccessibilityAddForm(DefaultAddForm):
    def update(self):
        # Check if object already exists
        catalog = self.context.portal_catalog
        brains = catalog(portal_type='All in One Accessibility Setting')
        if brains:
            existing_url = brains[0].getURL()
            self.request.response.redirect(existing_url + '/edit')
            return
        super().update()

    def nextURL(self):
        return self.context.absolute_url() + '/edit'


class AllInOneAccessibilityAddView(DefaultAddView):
    form = AllInOneAccessibilityAddForm
