# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.browserlayer import utils
from redturtle.bandi.interfaces.browserlayer import IRedturtleBandiLayer
from redturtle.bandi.testing import INTEGRATION_TESTING

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:  # pragma: no cover
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that redturtle.bandi is properly installed."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if redturtle.bandi is installed."""
        if hasattr(self.installer, "is_product_installed"):
            self.assertFalse(self.installer.is_product_installed("redturtle.volto"))
        else:
            self.assertFalse(self.installer.isProductInstalled("redturtle.volto"))

    def test_browserlayer(self):
        """Test that IRedturtleBandiLayer is registered."""
        self.assertIn(IRedturtleBandiLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        if hasattr(self.installer, "uninstall_product"):
            self.installer.uninstall_product("redturtle.volto")
        else:
            self.installer.uninstallProducts(["redturtle.volto"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if redturtle.bandi is cleanly uninstalled."""
        if hasattr(self.installer, "is_product_installed"):
            self.assertFalse(self.installer.is_product_installed("redturtle.volto"))
        else:
            self.assertFalse(self.installer.isProductInstalled("redturtle.volto"))

    # TODO
    # def test_browserlayer_removed(self):
    #     """Test that IRedturtleBandiLayer is removed."""
    #     self.assertNotIn(IRedturtleBandiLayer, utils.registered_layers())
