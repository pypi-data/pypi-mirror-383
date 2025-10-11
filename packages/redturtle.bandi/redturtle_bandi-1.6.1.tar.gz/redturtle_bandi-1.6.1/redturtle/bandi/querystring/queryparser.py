from collections import namedtuple
from plone.app.querystring.queryparser import _largerThan
from plone.app.querystring.queryparser import _lessThan

import DateTime


Row = namedtuple("Row", ["index", "operator", "values"])


def _afterDateTime(context, row):  # noqa
    try:
        value = DateTime.DateTime(row.values)
    except DateTime.interfaces.SyntaxError:
        value = DateTime.DateTime()

    row = Row(index=row.index, operator=row.operator, values=value)

    return _largerThan(context, row)


def _beforeDateTime(context, row):  # noqa
    try:
        value = DateTime.DateTime(row.values)
    except DateTime.interfaces.SyntaxError:
        value = DateTime.DateTime()

    row = Row(index=row.index, operator=row.operator, values=value)

    return _lessThan(context, row)
