import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from collective.lesscss.testing import\
    COLLECTIVE_LESSCSS_INTEGRATION_TESTING


class RegistryTestCase(unittest.TestCase):

    layer = COLLECTIVE_LESSCSS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.tool = getattr(self.portal, 'portal_less')
        self.tool.clearResources()
