from collective.lesscss.interface import ILESSRegistry

from Products.ResourceRegistries.exportimport.resourceregistry import ResourceRegistryNodeAdapter, \
     importResRegistry, exportResRegistry

_FILENAME = 'lessregistry.xml'
_REG_ID = 'portal_less'
_REG_TITLE = 'LESS Stylesheet registry'


def importLESSRegistry(context):
    """
    Import CSS registry.
    """
    return importResRegistry(context, _REG_ID, _REG_TITLE, _FILENAME)


def exportLESSRegistry(context):
    """
    Export CSS registry.
    """
    return exportResRegistry(context, _REG_ID, _REG_TITLE, _FILENAME)


class LESSRegistryNodeAdapter(ResourceRegistryNodeAdapter):
    """
    Node im- and exporter for CSSRegistry.
    """

    __used_for__ = ILESSRegistry
    registry_id = _REG_ID
    resource_type = 'stylesheet'
    register_method = 'registerStylesheet'
    update_method = 'updateStylesheet'
