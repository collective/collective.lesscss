from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Products.ResourceRegistries.tools.CSSRegistry import CSSRegistryTool
from Products.ResourceRegistries.tools.CSSRegistry import Stylesheet
from collective.lesscss.interface import ILESSRegistry
from Products.ResourceRegistries import permissions


class LESSStyleSheet(Stylesheet):
    pass


class LESSRegistryTool(CSSRegistryTool):
    """A Plone registry for managing the linking to css files."""
    security = ClassSecurityInfo()

    id = 'portal_less'
    meta_type = 'LESS Stylesheets Registry'
    title = 'LESS Registry'

    implements(ILESSRegistry)

    #
    # ZMI stuff
    #

    manage_cssForm = PageTemplateFile('www/lessconfig', globals())

    filename_base = 'ploneLESSStyles'
    filename_appendix = '.less'
    merged_output_prefix = u''
    cache_duration = 7
    resource_class = LESSStyleSheet

    security.declareProtected(permissions.ManagePortal, 'getRenderingOptions')
    def getRenderingOptions(self):
        """Rendering methods for use in ZMI forms."""
        return ('link', )
