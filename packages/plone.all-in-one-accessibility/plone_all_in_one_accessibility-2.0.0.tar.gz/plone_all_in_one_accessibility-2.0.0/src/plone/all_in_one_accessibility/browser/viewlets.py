from zope.interface import Interface
from zope.viewlet.manager import ViewletManager
from plone.app.layout.viewlets.common import ViewletBase


class AccessibilityCSSViewlet(ViewletBase):
    def render(self):
        return """
<link rel="stylesheet" href="++plone++plone.all_in_one_accessibility/custom.css" />
<script src="++plone++plone.all_in_one_accessibility/custom.js"></script>
"""

