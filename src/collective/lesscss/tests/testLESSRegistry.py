from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from AccessControl import Unauthorized

from zope.interface.verify import verifyObject
from collective.lesscss.interface import ILESSRegistry
from collective.lesscss.tests.base import RegistryTestCase


class TestProductInstalled(RegistryTestCase):

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'collective.lesscss'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')


class TestImplementation(RegistryTestCase):

    def test_interfaces(self):
        tool = getattr(self.portal, 'portal_less')
        self.failUnless(ILESSRegistry.providedBy(tool))
        self.failUnless(verifyObject(ILESSRegistry, tool))


class TestTool(RegistryTestCase):

    def testToolExists(self):
        self.failUnless('portal_less' in self.portal.objectIds())

    def testZMIForm(self):
        tool = getattr(self.portal, 'portal_less')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.failUnless(tool.manage_cssForm())
        self.failUnless(tool.manage_cssComposition())


class testZMIMethods(RegistryTestCase):

    def testAdd(self):
        self.tool = getattr(self.portal, 'portal_less')
        self.tool.clearResources()
        self.tool.manage_addStylesheet(id='joe')
        self.assertEqual(len(self.tool.getResources()), 1)
        self.failUnless(self.tool.getResources())


class TestLESSStylesheetRegistration(RegistryTestCase):

    def testStoringStylesheet(self):
        self.tool.registerStylesheet('foo')
        self.assertEqual(len(self.tool.getResources()), 1)
        self.assertEqual(self.tool.getResources()[0].getId(), 'foo')

    def testDefaultStylesheetAttributes(self):
        self.tool.registerStylesheet('foodefault')
        self.assertEqual(self.tool.getResources()[0].getId(), 'foodefault')
        self.assertEqual(self.tool.getResources()[0].getExpression(), '')
        self.assertEqual(self.tool.getResources()[0].getAuthenticated(), False)
        self.assertEqual(self.tool.getResources()[0].getMedia(), 'screen')
        self.assertEqual(self.tool.getResources()[0].getRel(), 'stylesheet')
        self.assertEqual(self.tool.getResources()[0].getTitle(), None)
        self.assertEqual(self.tool.getResources()[0].getRendering(), 'link')
        self.failUnless(self.tool.getResources()[0].getEnabled())

    def testExternalDefaultStylesheetAttributes(self):
        self.tool.registerStylesheet('http://example.com/foodefault')
        self.assertEqual(self.tool.getResources()[0].getId(), 'http://example.com/foodefault')
        self.failUnless(self.tool.getResources()[0].isExternalResource())
        self.failIf(self.tool.getResources()[0].getCacheable())
        self.assertEqual(self.tool.getResources()[0].getCompression(), 'none')
        self.failIf(self.tool.getResources()[0].getCookable())
        self.failUnless(self.tool.getResources()[0].getEnabled())

    def testStylesheetAttributes(self):
        self.tool.registerStylesheet('foo', expression='python:1', authenticated=False,
                                     media='print', rel='alternate stylesheet',
                                     title='Foo', rendering='inline', enabled=0)
        self.assertEqual(self.tool.getResources()[0].getId(), 'foo')
        self.assertEqual(self.tool.getResources()[0].getExpression(), 'python:1')
        self.assertEqual(self.tool.getResources()[0].getAuthenticated(), False)
        self.assertEqual(self.tool.getResources()[0].getMedia(), 'print')
        self.assertEqual(self.tool.getResources()[0].getRel(), 'alternate stylesheet')
        self.assertEqual(self.tool.getResources()[0].getTitle(), 'Foo')
        self.assertEqual(self.tool.getResources()[0].getRendering(), 'inline')
        self.failIf(self.tool.getResources()[0].getEnabled())

    def testDisallowingDuplicateIds(self):
        self.tool.registerStylesheet('foo')
        self.assertRaises(ValueError, self.tool.registerStylesheet, 'foo')

    def testPloneCustomStaysOnTop(self):
        self.tool.registerStylesheet('foo')
        self.tool.registerStylesheet('ploneCustom.css')
        self.tool.registerStylesheet('bar')
        self.assertEqual(len(self.tool.getResources()), 3)
        self.assertEqual(self.tool.getResourceIds(),
                         ('foo', 'bar', 'ploneCustom.css'))

    def testUnregisterStylesheet(self):
        self.tool.registerStylesheet('foo')
        self.assertEqual(len(self.tool.getResources()), 1)
        self.assertEqual(self.tool.getResources()[0].getId(), 'foo')
        self.tool.unregisterResource('foo')
        self.assertEqual(len(self.tool.getResources()), 0)

    def testStylesheetsDict(self):
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('ham')
        keys = self.tool.getResourcesDict().keys()
        keys.sort()
        res = ['ham', 'spam']
        res.sort()
        self.assertEqual(res, keys)
        self.assertEqual(self.tool.getResourcesDict()['ham'].getId(), 'ham')


class TestStylesheetRenaming(RegistryTestCase):

    def testRenaming(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(self.tool.concatenatedresources[
                         self.tool.cookedresources[0].getId()],
                         ['ham', 'spam', 'eggs'])
        self.tool.renameResource('spam', 'bacon')
        self.assertEqual(self.tool.concatenatedresources[
                         self.tool.cookedresources[0].getId()],
                         ['ham', 'bacon', 'eggs'])

    def testRenamingIdClash(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertRaises(ValueError, self.tool.renameResource, 'spam', 'eggs')

    def testDoubleRenaming(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.tool.renameResource('spam', 'bacon')
        self.assertRaises(ValueError, self.tool.renameResource, 'spam', 'bacon')


class TestToolSecurity(RegistryTestCase):

    def testRegistrationSecurity(self):
        self.assertRaises(Unauthorized, self.tool.restrictedTraverse,
                          'registerStylesheet')
        self.assertRaises(Unauthorized, self.tool.restrictedTraverse,
                          'unregisterResource')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        try:
            self.tool.restrictedTraverse('registerStylesheet')
            self.tool.restrictedTraverse('unregisterResource')
        except Unauthorized:
            self.fail()


class TestStylesheetMoving(RegistryTestCase):

    def testStylesheetMoveDown(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs'))
        self.tool.moveResourceDown('spam')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'eggs', 'spam'))

    def testStylesheetMoveDownAtEnd(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs'))
        self.tool.moveResourceDown('eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs'))

    def testStylesheetMoveUp(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs'))
        self.tool.moveResourceUp('spam')
        self.assertEqual(self.tool.getResourceIds(),
                         ('spam', 'ham', 'eggs'))

    def testStylesheetMoveUpAtStart(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs'))
        self.tool.moveResourceUp('ham')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs'))

    def testStylesheetMoveIllegalId(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs'))
        self.tool.moveResourceUp('foo')

    def testStylesheetMoveToBottom(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs'))
        self.tool.moveResourceToBottom('ham')
        self.assertEqual(self.tool.getResourceIds(),
                         ('spam', 'eggs', 'ham'))

    def testStylesheetMoveToTop(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs'))
        self.tool.moveResourceToTop('eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('eggs', 'ham', 'spam'))

    def testStylesheetMoveBefore(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.tool.registerStylesheet('bacon')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs', 'bacon'))
        self.tool.moveResourceBefore('bacon', 'ham')
        self.assertEqual(self.tool.getResourceIds(),
                         ('bacon', 'ham', 'spam', 'eggs'))
        self.tool.moveResourceBefore('bacon', 'eggs')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'bacon', 'eggs'))

    def testStylesheetMoveAfter(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.tool.registerStylesheet('bacon')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs', 'bacon'))
        self.tool.moveResourceAfter('bacon', 'ham')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'bacon', 'spam', 'eggs'))
        self.tool.moveResourceAfter('bacon', 'spam')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'bacon', 'eggs'))

    def testStylesheetMove(self):
        self.tool.registerStylesheet('ham')
        self.tool.registerStylesheet('spam')
        self.tool.registerStylesheet('eggs')
        self.tool.registerStylesheet('bacon')
        self.assertEqual(self.tool.getResourceIds(),
                         ('ham', 'spam', 'eggs', 'bacon'))
        self.tool.moveResource('ham', 2)
        self.assertEqual(self.tool.getResourceIds(),
                         ('spam', 'eggs', 'ham', 'bacon'))
        self.tool.moveResource('bacon', 0)
        self.assertEqual(self.tool.getResourceIds(),
                         ('bacon', 'spam', 'eggs', 'ham'))
