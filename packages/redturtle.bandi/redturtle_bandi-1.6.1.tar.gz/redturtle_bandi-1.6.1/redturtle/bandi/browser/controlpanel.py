# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from redturtle.bandi import bandiMessageFactory as _
from redturtle.bandi.interfaces.settings import IBandoSettings


class BandiSettingsForm(controlpanel.RegistryEditForm):
    schema = IBandoSettings
    id = "BandiSettingsForm"
    label = _("bandi_settings_label", default="Impostazioni per i bandi")


class BandiControlPanel(controlpanel.ControlPanelFormWrapper):

    form = BandiSettingsForm
