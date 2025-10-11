# -*- coding: utf-8 -*-
from plone.restapi.controlpanels import RegistryConfigletPanel
from redturtle.bandi.interfaces.settings import IBandoSettings
from zope.component import adapter
from zope.interface import Interface


@adapter(Interface, Interface)
class BandiControlpanel(RegistryConfigletPanel):
    schema = IBandoSettings
    configlet_id = "redturtle_bandi"
    configlet_category_id = "Products"
    schema_prefix = None
