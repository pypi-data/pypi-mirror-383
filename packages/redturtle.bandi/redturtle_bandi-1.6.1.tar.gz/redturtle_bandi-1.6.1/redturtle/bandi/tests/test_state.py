# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from redturtle.bandi.testing import INTEGRATION_TESTING

import unittest


class BandoStateTest(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_bando_initial_state(self):
        self.bando = api.content.create(
            container=self.portal, type="Bando", title="Bando foo"
        )
        view = api.content.get_view(
            name="bando_view", context=self.bando, request=self.request
        )
        self.assertEqual(view.getBandoState(), ("open", "Open"))

    def test_bando_scheduled_state(self):
        self.bando = api.content.create(
            container=self.portal, type="Bando", title="Bando foo"
        )
        self.bando.apertura_bando = datetime.now() + timedelta(days=1)
        view = api.content.get_view(
            name="bando_view", context=self.bando, request=self.request
        )
        self.assertEqual(view.getBandoState(), ("scheduled", "Scheduled"))

    def test_bando_in_progress_state(self):
        """
        apertura > scadenza > (today) > chiusura_procedimento  ==> inprogress
        """
        self.bando = api.content.create(
            container=self.portal, type="Bando", title="Bando foo"
        )
        self.bando.apertura_bando = datetime.now() - timedelta(days=2)
        self.bando.scadenza_bando = datetime.now() - timedelta(days=1)
        self.bando.chiusura_procedimento_bando = (
            datetime.now() + timedelta(days=1)
        ).date()
        view = api.content.get_view(
            name="bando_view", context=self.bando, request=self.request
        )
        self.assertEqual(view.getBandoState(), ("inProgress", "In progress"))

    def test_bando_closed_state(self):
        """
        apertura > chiusura_procedimento > (today)  ==> closed
        """
        self.bando = api.content.create(
            container=self.portal, type="Bando", title="Bando foo"
        )
        self.bando.apertura_bando = datetime.now() - timedelta(days=2)
        self.bando.chiusura_procedimento_bando = (
            datetime.now() - timedelta(days=1)
        ).date()
        view = api.content.get_view(
            name="bando_view", context=self.bando, request=self.request
        )
        self.assertEqual(view.getBandoState(), ("closed", "Closed"))

    def test_bando_closed_state_2(self):
        """
        apertura > scadenza > chiusura_procedimento > (today) ==> closed
        """
        self.bando = api.content.create(
            container=self.portal, type="Bando", title="Bando foo"
        )
        self.bando.apertura_bando = datetime.now() - timedelta(days=3)
        self.bando.scadenza_bando = datetime.now() - timedelta(days=2)
        self.bando.chiusura_procedimento_bando = (
            datetime.now() - timedelta(days=1)
        ).date()
        view = api.content.get_view(
            name="bando_view", context=self.bando, request=self.request
        )
        self.assertEqual(view.getBandoState(), ("closed", "Closed"))
