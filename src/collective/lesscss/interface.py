from zope.interface import Interface
from Products.ResourceRegistries.interfaces.registries import ICSSRegistry


class ILESSRegistry(ICSSRegistry):
    pass


class ICollectiveLESSCSSLayer(Interface):
    """Request marker installed via browserlayer.xml.
    """
