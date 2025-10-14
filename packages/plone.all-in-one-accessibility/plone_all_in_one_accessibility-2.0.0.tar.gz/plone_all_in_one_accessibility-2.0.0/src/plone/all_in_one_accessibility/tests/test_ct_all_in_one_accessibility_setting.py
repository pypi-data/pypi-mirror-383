# -*- coding: utf-8 -*-
from plone import api
from plone.all_in_one_accessibility.content.all_in_one_accessibility_setting import (
    IAllInOneAccessibilitySetting,  # NOQA E501
)
from plone.all_in_one_accessibility.testing import (  # noqa
    PLONE_ALL_IN_ONE_ACCESSIBILITY_INTEGRATION_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class AllInOneAccessibilitySettingIntegrationTest(unittest.TestCase):

    layer = PLONE_ALL_IN_ONE_ACCESSIBILITY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_all_in_one_accessibility_setting_schema(self):
        fti = queryUtility(IDexterityFTI, name='All in One Accessibility Setting')
        schema = fti.lookupSchema()
        self.assertEqual(IAllInOneAccessibilitySetting, schema)

    def test_ct_all_in_one_accessibility_setting_fti(self):
        fti = queryUtility(IDexterityFTI, name='All in One Accessibility Setting')
        self.assertTrue(fti)

    def test_ct_all_in_one_accessibility_setting_factory(self):
        fti = queryUtility(IDexterityFTI, name='All in One Accessibility Setting')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IAllInOneAccessibilitySetting.providedBy(obj),
            u'IAllInOneAccessibilitySetting not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_all_in_one_accessibility_setting_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='All in One Accessibility Setting',
            id='all_in_one_accessibility_setting',
        )

        self.assertTrue(
            IAllInOneAccessibilitySetting.providedBy(obj),
            u'IAllInOneAccessibilitySetting not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('all_in_one_accessibility_setting', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('all_in_one_accessibility_setting', parent.objectIds())

    def test_ct_all_in_one_accessibility_setting_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='All in One Accessibility Setting')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
