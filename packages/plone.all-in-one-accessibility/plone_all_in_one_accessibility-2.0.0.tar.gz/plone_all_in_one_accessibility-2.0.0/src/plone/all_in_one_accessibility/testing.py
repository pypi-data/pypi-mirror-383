# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import plone.all_in_one_accessibility


class PloneAllInOneAccessibilityLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=plone.all_in_one_accessibility)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.all_in_one_accessibility:default')


PLONE_ALL_IN_ONE_ACCESSIBILITY_FIXTURE = PloneAllInOneAccessibilityLayer()


PLONE_ALL_IN_ONE_ACCESSIBILITY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_ALL_IN_ONE_ACCESSIBILITY_FIXTURE,),
    name='PloneAllInOneAccessibilityLayer:IntegrationTesting',
)


PLONE_ALL_IN_ONE_ACCESSIBILITY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_ALL_IN_ONE_ACCESSIBILITY_FIXTURE,),
    name='PloneAllInOneAccessibilityLayer:FunctionalTesting',
)


PLONE_ALL_IN_ONE_ACCESSIBILITY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLONE_ALL_IN_ONE_ACCESSIBILITY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='PloneAllInOneAccessibilityLayer:AcceptanceTesting',
)
