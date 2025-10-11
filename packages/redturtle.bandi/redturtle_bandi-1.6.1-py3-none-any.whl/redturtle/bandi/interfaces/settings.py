# -*- coding: utf-8 -*-
from redturtle.bandi import bandiMessageFactory as _
from zope import schema
from zope.interface import Interface


class IBandoSettings(Interface):
    """
    Settings used for announcements default value
    """

    default_ente = schema.Tuple(
        title=_("default_ente_label", default="Default Ente"),
        description=_(
            "default_ente_help",
            default="Insert a list of default Enti that will be automatically selected when adding a new Bando.",
        ),
        required=False,
        value_type=schema.TextLine(),
        missing_value=None,
        default=("Regione Emilia-Romagna",),
    )

    default_destinatari = schema.Tuple(
        title=_("default_destinatari_label", default="Destinatari types"),
        description=_(
            "default_destinatari_help",
            default="Insert a list of available destinatari that can be selected when adding a new Bando.",
        ),
        required=False,
        value_type=schema.TextLine(),
        missing_value=None,
        default=(
            "Cittadini",
            "Imprese",
            "Enti locali",
            "Associazioni",
            "Altro",
        ),
    )

    tipologie_bando = schema.Tuple(
        title=_("tipologie_bando_label", default="Announcement types"),
        description=_(
            "tipologie_help",
            "These values will extend bandi.xml vocabulary on filesystem",
        ),
        required=False,
        value_type=schema.TextLine(),
        missing_value=None,
        default=(
            "Acquisizione beni e servizi",
            "Agevolazioni, finanziamenti, contributi",
            "Altro",
        ),
    )
