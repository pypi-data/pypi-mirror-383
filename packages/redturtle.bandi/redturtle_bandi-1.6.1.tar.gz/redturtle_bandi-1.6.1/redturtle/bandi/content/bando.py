# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from redturtle.bandi.interfaces.bando import IBando
from zope.interface import implementer


@implementer(IBando)
class Bando(Container):
    """ """
