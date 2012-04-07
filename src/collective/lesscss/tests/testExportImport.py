from collective.lesscss.tests.base import RegistryTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class TestExportImport(RegistryTestCase):

    def test_removing(self):
        # Test that you can tell the resource registries to remove a
        # resource (a javascript here) using xml.
        tool = self.portal.portal_setup
        profile_id = 'profile-collective.lesscss.tests:test'
        # The next line used to throw an UnboundLocalError:
        try:
            result = tool.runImportStepFromProfile(profile_id, 'lessregistry')
        except UnboundLocalError, e:
            self.fail("UnboundLocalError thrown: %s" % e)
        self.failUnless("resourceregistry: LESS Stylesheet registry imported." in \
                   result['messages']['lessregistry'],
               "LESS registry should have been imported")
        # We depend on some other steps:
        self.assertEqual(result['steps'],
                         [u'toolset', u'componentregistry', 'lessregistry'])

    def test_snapshot(self):
        # GenericSetup snapshot should work
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        tool = self.portal.portal_setup
        snapshot_id = tool._mangleTimestampName('test')
        tool.createSnapshot(snapshot_id)
