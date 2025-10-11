from collective.tiles.collection.interfaces import ICollectiveTilesCollectionLayer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IRedturtleBandiLayer(IDefaultBrowserLayer, ICollectiveTilesCollectionLayer):
    """Marker interface that defines a browser layer."""
