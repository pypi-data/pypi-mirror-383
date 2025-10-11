from DateTime import DateTime
from plone.app.querystring.interfaces import IQueryModifier
from plone.restapi.serializer.converters import json_compatible
from zope.interface import provider


@provider(IQueryModifier)
def modify_bandi_state_query(query):
    """
    Substitute bando_state in query with a combination of other indexes
    """
    now = json_compatible(DateTime())

    state_operators = {
        "open": (
            {
                "o": "plone.app.querystring.operation.date.beforeDateTime",
                "v": now,
                "i": "apertura_bando",
            },
            {
                "o": "plone.app.querystring.operation.date.afterDateTime",
                "v": now,
                "i": "scadenza_bando",
            },
            {
                "o": "plone.app.querystring.operation.date.afterDateTime",
                "v": now,
                "i": "chiusura_procedimento_bando",
            },
        ),
        "in-progress": (
            {
                "o": "plone.app.querystring.operation.date.beforeDateTime",
                "v": now,
                "i": "scadenza_bando",
            },
            {
                "o": "plone.app.querystring.operation.date.afterDateTime",
                "v": now,
                "i": "chiusura_procedimento_bando",
            },
        ),
        "closed": (
            {
                "o": "plone.app.querystring.operation.date.beforeDateTime",
                "v": now,
                "i": "chiusura_procedimento_bando",
            },
        ),
        "scheduled": (
            {
                "o": "plone.app.querystring.operation.date.afterDateTime",
                "v": now,
                "i": "apertura_bando",
            },
        ),
    }

    new_query = []
    for criteria in query:
        if criteria.get("i", "") != "bando_state":
            new_query.append(criteria)
            continue

        value = criteria.get("v", "")
        if isinstance(value, list):
            # get only first
            value = value and value[0] or ""

        operator = state_operators.get(value, None)
        if operator:
            new_query.extend(operator)
    return new_query
