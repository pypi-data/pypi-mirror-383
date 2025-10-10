# -*- coding: utf-8 -*-

from Products.urban.testing import URBAN_TESTS_CONFIG_FUNCTIONAL
from datetime import datetime
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

import unittest


class TestAmendedPlansStartDate(unittest.TestCase):

    layer = URBAN_TESTS_CONFIG_FUNCTIONAL

    def _get_due_date(self, task):
        """"Return the due date for a given task"""
        container = task.get_container()
        config = task.get_task_config()
        return config.compute_due_date(container, task)

    def _create_recepisse_plans_modificatifs(self, licence, event_date):
        event_config = self.portal_urban.codt_buildlicence.urbaneventtypes["recepisse-de-plans-modificatifs"]
        event = licence.createUrbanEvent(event_config)
        event.setEventDate(event_date)
        notify(ObjectModifiedEvent(licence))

    def setUp(self):
        portal = self.layer["portal"]
        self.portal = portal
        api.user.grant_roles(username="urbanmanager", roles=["Member", "Manager"])
        api.group.add_user(username="urbanmanager", groupname="urban_editors")
        login(self.portal, "urbanmanager")
        self.portal_urban = portal.portal_urban
        event_config_deposit = self.portal_urban.codt_buildlicence.urbaneventtypes["depot-de-la-demande"]
        event_config_intention = self.portal_urban.codt_buildlicence.urbaneventtypes["intention-de-depot-de-plans-modifies"]

        # receipt date + ultimatum date
        self.licence_1 = api.content.create(
            type="CODT_BuildLicence",
            container=self.portal.urban.codt_buildlicences,
            title="Licence 1",
        )
        self.licence_1.setProcedureChoice("simple")

        event = self.licence_1.createUrbanEvent(event_config_deposit)
        event.setEventDate(datetime(2024, 4, 10))

        event_config_intention = self.portal_urban.codt_buildlicence.urbaneventtypes["intention-de-depot-de-plans-modifies"]
        event = self.licence_1.createUrbanEvent(event_config_intention)
        event.setReceiptDate(datetime(2024, 4, 20))
        event.setUltimeDate(datetime(2024, 6, 23))

        self.licence_1.setHasModifiedBlueprints(True)

        api.content.transition(self.licence_1, transition="ask_address_validation")
        api.content.transition(self.licence_1, transition="validate_address")
        api.content.transition(self.licence_1, transition="propose_complete")

        api.content.transition(self.licence_1, transition="suspend")
        notify(ObjectModifiedEvent(self.licence_1))

        # receipt date only
        self.licence_2 = api.content.create(
            type="CODT_BuildLicence",
            container=self.portal.urban.codt_buildlicences,
            title="Licence 2",
        )
        self.licence_2.setProcedureChoice("simple")

        event = self.licence_2.createUrbanEvent(event_config_deposit)
        event.setEventDate(datetime(2024, 4, 10))
        api.content.transition(event, to_state="closed")
        event = self.licence_2.createUrbanEvent(event_config_intention)
        event.setReceiptDate(datetime(2024, 4, 20))

        self.licence_2.setHasModifiedBlueprints(True)

        api.content.transition(self.licence_2, transition="ask_address_validation")
        api.content.transition(self.licence_2, transition="validate_address")
        api.content.transition(self.licence_2, transition="propose_complete")
        api.content.transition(self.licence_2, transition="suspend")
        notify(ObjectModifiedEvent(self.licence_2))

        # no date
        self.licence_3 = api.content.create(
            type="CODT_BuildLicence",
            container=self.portal.urban.codt_buildlicences,
            title="Licence 3",
        )
        self.licence_3.setProcedureChoice("simple")
        event = self.licence_3.createUrbanEvent(event_config_deposit)
        event.setEventDate(datetime(2024, 4, 10))
        event_config_intention = self.portal_urban.codt_buildlicence.urbaneventtypes["intention-de-depot-de-plans-modifies"]
        event = self.licence_3.createUrbanEvent(event_config_intention)

        self.licence_3.setHasModifiedBlueprints(True)

        api.content.transition(self.licence_3, transition="ask_address_validation")
        api.content.transition(self.licence_3, transition="validate_address")
        api.content.transition(self.licence_3, transition="propose_complete")
        api.content.transition(self.licence_3, transition="suspend")
        notify(ObjectModifiedEvent(self.licence_3))


        logout()
        login(portal, "urbaneditor")

    def tearDown(self):
        login(self.portal, "urbanmanager")
        api.content.delete(self.licence_1)
        api.content.delete(self.licence_2)
        api.content.delete(self.licence_3)

    def test_start_date(self):
        # receipt date + ultimatum date
        self.assertTrue("TASK_attente_plans_modifies" in self.licence_1)
        task = self.licence_1.TASK_attente_plans_modifies
        self.assertEqual(datetime(2024, 6, 23).date(), self._get_due_date(task))

        # receipt date only
        self.assertTrue("TASK_attente_plans_modifies" in self.licence_2)
        task = self.licence_2.TASK_attente_plans_modifies
        self.assertEqual(datetime(2024, 10, 17).date(), self._get_due_date(task))

        # no date
        self.assertTrue("TASK_attente_plans_modifies" in self.licence_3)
        task = self.licence_3.TASK_attente_plans_modifies
        self.assertEqual(datetime(9999, 1, 1).date(), self._get_due_date(task))

    def test_delay_amend_then_resume(self):
        login(self.portal, "urbanmanager")

        self._create_recepisse_plans_modificatifs(self.licence_1, datetime(2024, 5, 10))
        api.content.transition(self.licence_1, transition="resume")
        notify(ObjectModifiedEvent(self.licence_1))
        self.assertTrue("TASK_verif_complet-1" in self.licence_1)
        task = self.licence_1["TASK_verif_complet-1"]
        self.assertEqual(api.content.get_state(task), "to_do")
        self.assertEqual(datetime(2024, 6, 3).date(), self._get_due_date(task))

        self._create_recepisse_plans_modificatifs(self.licence_2, datetime(2024, 5, 10))
        api.content.transition(self.licence_2, transition="resume")
        notify(ObjectModifiedEvent(self.licence_2))
        self.assertTrue("TASK_verif_complet-1" in self.licence_2)
        task = self.licence_2["TASK_verif_complet-1"]
        self.assertEqual(api.content.get_state(task), "to_do")
        self.assertEqual(datetime(2024, 6, 3).date(), self._get_due_date(task))

        self._create_recepisse_plans_modificatifs(self.licence_3, datetime(2024, 5, 10))
        api.content.transition(self.licence_3, transition="resume")
        notify(ObjectModifiedEvent(self.licence_3))
        self.assertTrue("TASK_verif_complet-1" in self.licence_3)
        task = self.licence_3["TASK_verif_complet-1"]
        self.assertEqual(api.content.get_state(task), "to_do")
        self.assertEqual(datetime(2024, 6, 3).date(), self._get_due_date(task))

    def test_delay_resume_only(self):
        login(self.portal, "urbanmanager")

        api.content.transition(self.licence_1, transition="resume")
        notify(ObjectModifiedEvent(self.licence_1))
        self.assertTrue("TASK_verif_complet-1" in self.licence_1)
        task = self.licence_1["TASK_verif_complet-1"]
        self.assertEqual(api.content.get_state(task), "to_do")
        self.assertEqual(datetime(2024, 7, 17).date(), self._get_due_date(task))

        api.content.transition(self.licence_2, transition="resume")
        notify(ObjectModifiedEvent(self.licence_2))
        self.assertTrue("TASK_verif_complet-1" in self.licence_2)
        task = self.licence_2["TASK_verif_complet-1"]
        self.assertEqual(api.content.get_state(task), "to_do")
        self.assertEqual(datetime(2024, 11, 10).date(), self._get_due_date(task))

        api.content.transition(self.licence_3, transition="resume")
        notify(ObjectModifiedEvent(self.licence_3))
        self.assertTrue("TASK_verif_complet-1" in self.licence_3)
        task = self.licence_3["TASK_verif_complet-1"]
        self.assertEqual(api.content.get_state(task), "to_do")
        self.assertEqual(datetime(2024, 5, 4).date(), self._get_due_date(task))

    def test_delay_resume_then_amend(self):
        login(self.portal, "urbanmanager")
        
        api.content.transition(self.licence_1, transition="resume")
        notify(ObjectModifiedEvent(self.licence_1))
        self._create_recepisse_plans_modificatifs(self.licence_1, datetime(2024, 5, 10))
        self.assertTrue("TASK_verif_complet-1" in self.licence_1)
        task = self.licence_1["TASK_verif_complet-1"]
        self.assertEqual(api.content.get_state(task), "to_do")
        self.assertEqual(datetime(2024, 6, 3).date(), self._get_due_date(task))

        api.content.transition(self.licence_2, transition="resume")
        notify(ObjectModifiedEvent(self.licence_2))
        self._create_recepisse_plans_modificatifs(self.licence_2, datetime(2024, 5, 10))
        self.assertTrue("TASK_verif_complet-1" in self.licence_2)
        task = self.licence_2["TASK_verif_complet-1"]
        self.assertEqual(api.content.get_state(task), "to_do")
        self.assertEqual(datetime(2024, 6, 3).date(), self._get_due_date(task))

        api.content.transition(self.licence_3, transition="resume")
        notify(ObjectModifiedEvent(self.licence_3))
        self._create_recepisse_plans_modificatifs(self.licence_3, datetime(2024, 5, 10))
        self.assertTrue("TASK_verif_complet-1" in self.licence_3)
        task = self.licence_3["TASK_verif_complet-1"]
        self.assertEqual(api.content.get_state(task), "to_do")
        self.assertEqual(datetime(2024, 6, 3).date(), self._get_due_date(task))
