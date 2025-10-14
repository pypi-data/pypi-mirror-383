from Products.Five.browser import BrowserView

class RedirectToSettingEditView(BrowserView):
    def __call__(self):
        # URL of your unique setting object edit page
        setting_edit_url = self.context.absolute_url() + '/all-in-one-accessibility-setting/edit'
        self.request.response.redirect(setting_edit_url)
        return ''
