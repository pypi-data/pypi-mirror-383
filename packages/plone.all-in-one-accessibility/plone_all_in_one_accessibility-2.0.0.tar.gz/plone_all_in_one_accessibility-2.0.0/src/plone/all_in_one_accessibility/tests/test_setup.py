# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.all_in_one_accessibility.testing import (  # noqa: E501
    PLONE_ALL_IN_ONE_ACCESSIBILITY_INTEGRATION_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that plone.all_in_one_accessibility is properly installed."""

    layer = PLONE_ALL_IN_ONE_ACCESSIBILITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if plone.all_in_one_accessibility is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'plone.all_in_one_accessibility'))

    def test_browserlayer(self):
        """Test that IPloneAllInOneAccessibilityLayer is registered."""
        from plone.all_in_one_accessibility.interfaces import (
            IPloneAllInOneAccessibilityLayer,
        )
        from plone.browserlayer import utils
        self.assertIn(
            IPloneAllInOneAccessibilityLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = PLONE_ALL_IN_ONE_ACCESSIBILITY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstall_product('plone.all_in_one_accessibility')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if plone.all_in_one_accessibility is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'plone.all_in_one_accessibility'))

    def test_browserlayer_removed(self):
        """Test that IPloneAllInOneAccessibilityLayer is removed."""
        from plone.all_in_one_accessibility.interfaces import (
            IPloneAllInOneAccessibilityLayer,
        )
        from plone.browserlayer import utils
        self.assertNotIn(IPloneAllInOneAccessibilityLayer, utils.registered_layers())
