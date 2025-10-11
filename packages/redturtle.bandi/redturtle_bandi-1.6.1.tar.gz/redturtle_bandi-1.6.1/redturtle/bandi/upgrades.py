# -*- coding: utf-8 -*-
from plone import api
from plone.app.event.base import default_timezone
from redturtle.bandi import logger
from redturtle.bandi.interfaces.settings import IBandoSettings

import pytz


default_profile = "profile-redturtle.bandi:default"


def update_catalog(context):
    context.runImportStepFromProfile(default_profile, "catalog")


def update_registry(context):
    context.runImportStepFromProfile(
        default_profile, "plone.app.registry", run_dependencies=False
    )


def migrate_to_1100(context):
    PROFILE_ID = "profile-redturtle.bandi:to_1100"
    context.runAllImportStepsFromProfile(PROFILE_ID)

    #  update indexes and topics
    context.runImportStepFromProfile(default_profile, "catalog")
    context.runImportStepFromProfile(
        default_profile, "plone.app.registry", run_dependencies=False
    )

    bandi = api.content.find(portal_type="Bando")
    tot_results = len(bandi)
    logger.info("### Fixing {tot} Bandi ###".format(tot=tot_results))
    for counter, brain in enumerate(bandi):
        logger.info(
            "[{counter}/{tot}] - {bando}".format(
                counter=counter + 1, tot=tot_results, bando=brain.getPath()
            )
        )
        bando = brain.getObject()
        bando.reindexObject(
            idxs=[
                "chiusura_procedimento_bando",
                "destinatari_bando",
                "scadenza_bando",
                "tipologia_bando",
            ]
        )

    criteria_mapping = {
        "getTipologia_bando": "tipologia_bando",
        "getChiusura_procedimento_bando": "chiusura_procedimento_bando",
        "getScadenza_bando": "scadenza_bando",
        "getDestinatariBando": "destinatari_bando",
    }
    collections = api.content.find(portal_type="Collection")
    tot_results = len(collections)
    logger.info("### Fixing {tot} Collections ###".format(tot=tot_results))
    for counter, brain in enumerate(collections):
        collection = brain.getObject()
        query = []
        for criteria in getattr(collection, "query", []):
            criteria["i"] = criteria_mapping.get(criteria["i"], criteria["i"])
            query.append(criteria)
        collection.query = query

        # fix sort_on
        sort_on = getattr(collection, "sort_on", "")
        if sort_on in criteria_mapping:
            collection.sort_on = criteria_mapping[sort_on]

        logger.info(
            "[{counter}/{tot}] - {collection}".format(
                counter=counter + 1,
                tot=tot_results,
                collection=brain.getPath(),
            )
        )
    logger.info("Upgrade to 3100 complete")


def migrate_to_1200(context):
    """
    Fix typo in upgrade-step
    """
    PROFILE_ID = "profile-redturtle.bandi:to_1100"
    context.runAllImportStepsFromProfile(PROFILE_ID)


def migrate_to_1300(context):
    """
    Add tzinfo to scadenza_bando
    """
    tz = pytz.timezone(default_timezone())

    bandi = api.content.find(portal_type="Bando")
    tot_results = len(bandi)
    logger.info("### Fixing {tot} Bandi ###".format(tot=tot_results))
    for counter, brain in enumerate(bandi):
        bando = brain.getObject()
        if not getattr(bando, "scadenza_bando", None):
            continue
        try:
            bando.scadenza_bando = pytz.utc.localize(bando.scadenza_bando).astimezone(
                tz
            )
        except ValueError:
            # convert to right timezone
            if bando.scadenza_bando.tzinfo.zone == tz.zone:
                # same tz, skip
                continue
            bando.scadenza_bando = pytz.utc.localize(
                bando.scadenza_bando.replace(tzinfo=None)
            ).astimezone(tz)
        bando.reindexObject(idxs=["scadenza_bando"])

        logger.info(
            "[{counter}/{tot}] - {bando}".format(
                counter=counter + 1, tot=tot_results, bando=brain.getPath()
            )
        )


def migrate_to_2000(context):
    update_catalog(context)
    update_registry(context)

    bandi = api.content.find(portal_type="Bando")
    tot_results = len(bandi)
    logger.info("### Fixing {tot} Bandi ###".format(tot=tot_results))
    for counter, brain in enumerate(bandi):
        logger.info(
            "[{counter}/{tot}] - {bando}".format(
                counter=counter + 1, tot=tot_results, bando=brain.getPath()
            )
        )
        bando = brain.getObject()
        bando.reindexObject(
            idxs=[
                "apertura_bando",
            ]
        )


def migrate_to_2100(context):
    update_catalog(context)

    bandi = api.content.find(portal_type="Bando")
    tot_results = len(bandi)
    logger.info("### Fixing {tot} Bandi ###".format(tot=tot_results))
    for counter, brain in enumerate(bandi):
        logger.info(
            "[{counter}/{tot}] - {bando}".format(
                counter=counter + 1, tot=tot_results, bando=brain.getPath()
            )
        )
        bando = brain.getObject()
        bando.reindexObject()


def migrate_to_2101(context):
    bandi = api.content.find(portal_type="Bando")
    tot_results = len(bandi)
    logger.info("### Fixing {tot} Bandi ###".format(tot=tot_results))
    for counter, brain in enumerate(bandi):
        logger.info(
            "[{counter}/{tot}] - {bando}".format(
                counter=counter + 1, tot=tot_results, bando=brain.getPath()
            )
        )
        bando = brain.getObject()
        bando.reindexObject(idxs=["scadenza_bando"])


def migrate_to_2102(context):
    update_catalog(context)

    bandi = api.content.find(portal_type="Bando")
    tot_results = len(bandi)
    logger.info("### Fixing {tot} Bandi ###".format(tot=tot_results))
    for counter, brain in enumerate(bandi):
        logger.info(
            "[{counter}/{tot}] - {bando}".format(
                counter=counter + 1, tot=tot_results, bando=brain.getPath()
            )
        )
        bando = brain.getObject()
        bando.reindexObject(idxs=["tipologia_bando_label"])


def migrate_to_2200(context):  # noqa: C901
    from Acquisition import aq_base
    from copy import deepcopy
    from plone.dexterity.utils import iterSchemata
    from zope.schema import getFields

    try:
        from collective.volto.blocksfield.field import BlocksField

        HAS_BLOCKS_FIELD = True
    except ImportError:
        HAS_BLOCKS_FIELD = True

    bandi = api.content.find(portal_type="Bando")
    tot_results = len(bandi)
    logger.info("### Fixing {tot} Bandi ###".format(tot=tot_results))

    def get_value(key, value):
        for entry in api.portal.get_registry_record(
            key, interface=IBandoSettings, default=[]
        ):
            id, label = entry.split("|")
            if id == value:
                return label
        return value

    def fix_listing(blocks):
        for block in blocks.values():
            if block.get("@type", "") != "listing":
                continue
            for query in block.get("querystring", {}).get("query", []):
                value = query.get("v", "")
                if not value:
                    continue
                if query["i"] == "destinatari_bando":
                    query["v"] = [
                        get_value(key="default_destinatari", value=v) for v in value
                    ]
                elif query["i"] == "tipologia_bando":
                    query["v"] = [
                        get_value(key="tipologie_bando", value=v) for v in value
                    ]

    for counter, brain in enumerate(bandi):
        logger.info(
            "[{counter}/{tot}] - {bando}".format(
                counter=counter + 1, tot=tot_results, bando=brain.getPath()
            )
        )
        bando = brain.getObject()
        tipologia = getattr(bando, "tipologia_bando", "")
        destinatari = getattr(bando, "destinatari", "")
        if tipologia:
            value = get_value(key="tipologie_bando", value=tipologia)
            setattr(bando, "tipologia_bando", value)
        if destinatari:
            value = [get_value(key="default_destinatari", value=x) for x in destinatari]
            setattr(bando, "destinatari", value)
        bando.reindexObject(idxs=["tipologia_bando", "destinatari_bando"])

    # fix blocks
    # fix blocks in contents
    logger.info("### Fixing blocks ###")
    pc = api.portal.get_tool(name="portal_catalog")
    brains = pc()
    tot = len(brains)
    i = 0
    for brain in brains:
        i += 1
        if i % 1000 == 0:
            logger.info("Progress: {}/{}".format(i, tot))
        item = aq_base(brain.getObject())
        if getattr(item, "blocks", {}):
            blocks = deepcopy(item.blocks)
            if blocks:
                fix_listing(blocks)
                item.blocks = blocks
        if HAS_BLOCKS_FIELD:
            for schema in iterSchemata(item):
                # fix blocks in blocksfields
                for name, field in getFields(schema).items():
                    if not isinstance(field, BlocksField):
                        continue
                    value = deepcopy(field.get(item))
                    if not value:
                        continue
                    blocks = value.get("blocks", {})
                    if blocks:
                        fix_listing(blocks)
                        setattr(item, name, value)

    # cleanup vocabs
    for key in ["tipologie_bando", "default_destinatari"]:
        values = []
        for old_val in api.portal.get_registry_record(
            key, interface=IBandoSettings, default=[]
        ):
            id, label = old_val.split("|")
            values.append(label)

        api.portal.set_registry_record(key, tuple(values), interface=IBandoSettings)


def migrate_to_2300(context):
    PROFILE_ID = "profile-redturtle.bandi:to_2300"
    context.runAllImportStepsFromProfile(PROFILE_ID)
