# -*- coding: utf-8 -*-
from collective.tiles.collection.interfaces import ICollectionTileRenderer
from Products.Five.browser import BrowserView
from redturtle.bandi import bandiMessageFactory as _
from zope.interface import implementer


@implementer(ICollectionTileRenderer)
class View(BrowserView):

    display_name = _("bandi_layout", default="Layout Bandi")
