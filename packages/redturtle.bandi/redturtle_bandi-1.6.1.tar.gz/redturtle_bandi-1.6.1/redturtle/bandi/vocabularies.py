# -*- coding: utf-8 -*-
from plone import api
from redturtle.bandi.interfaces.settings import IBandoSettings
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class TipologiaBandoVocabulary(object):
    def __call__(self, context):
        values = api.portal.get_registry_record(
            "tipologie_bando", interface=IBandoSettings, default=[]
        )
        terms = [SimpleTerm(value=x, token=x, title=x) for x in values if x]
        return SimpleVocabulary(terms)


TipologiaBandoVocabularyFactory = TipologiaBandoVocabulary()


@implementer(IVocabularyFactory)
class DestinatariVocabularyFactory(object):
    def __call__(self, context):
        values = api.portal.get_registry_record(
            "default_destinatari", interface=IBandoSettings, default=[]
        )
        terms = [SimpleTerm(value=x, token=x, title=x) for x in values if x]
        return SimpleVocabulary(terms)


DestinatariVocabulary = DestinatariVocabularyFactory()


@implementer(IVocabularyFactory)
class EnteVocabularyFactory(object):
    def __call__(self, context):
        catalog = api.portal.get_tool("portal_catalog")
        enti = list(catalog._catalog.uniqueValuesFor("ente_bando"))
        terms = [SimpleTerm(value=ente, token=ente, title=ente) for ente in enti]

        return SimpleVocabulary(terms)


EnteVocabulary = EnteVocabularyFactory()


@implementer(IVocabularyFactory)
class BandiStatesVcabulary(object):
    def __call__(self, context):
        terms = [
            SimpleTerm(
                value=i,
                token=i,
                title=api.portal.translate(msgid=i, domain="redturtle.bandi"),
            )
            for i in ["open", "in-progress", "closed", "scheduled"]
        ]

        return SimpleVocabulary(terms)


BandiStatesVcabularyFactory = BandiStatesVcabulary()
