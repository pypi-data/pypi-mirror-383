# -*- coding: utf-8 -*-

from collections import OrderedDict

from Products.urban.interfaces import IEnvironmentBase
from Products.urban.workflows.adapter import LocalRoleAdapter

from plone import api


class StateRolesMapping(LocalRoleAdapter):
    """ """

    def __init__(self, context):
        self.context = context
        self.licence = self.context.aq_parent

    def get_opinion_group(self, groupe_type="editors"):
        opinion_request = self.context
        opinion_config = opinion_request.getUrbaneventtypes()

        if opinion_config.getIs_internal_service():
            registry = api.portal.get_tool("portal_registry")
            registry_field = registry[
                "Products.urban.interfaces.IInternalOpinionServices.services"
            ]

            record = registry_field.get(opinion_config.getInternal_service(), None)
            if record:
                if groupe_type is "editors":
                    return (record["editor_group_id"],)
                elif groupe_type is "validators":
                    return (record["validator_group_id"],)

        return ("urban_editors", "environment_editors")

    def get_editors(self):
        if IEnvironmentBase.providedBy(self.licence):
            return ("environment_editors",)
        return ("urban_editors",)

    def get_editors_roles(self):
        if "urban_editors" in self.get_opinion_editor():
            return (
                "Reader",
                "Contributor",
            )
        return ("Reader",)

    def get_opinion_editor(self):
        return self.get_opinion_group("editors")

    def get_opinion_validator(self):
        return self.get_opinion_group("validators")

    def get_opinion_editor_role(self):
        groups = self.get_opinion_editor()
        if "urban_editors" in groups:
            return (
                "Reader",
                "Contributor",
            )
        return (
            "Reader",
            "Editor",
        )

    mapping = {
        "creation": OrderedDict(
            [
                (get_editors, ("Editor",)),
                ("opinions_editors", ("Reader",)),
                (LocalRoleAdapter.get_readers, ("Reader",)),
            ]
        ),
        "waiting_opinion": OrderedDict(
            [
                (get_editors, (get_editors_roles,)),
                (get_opinion_editor, (get_opinion_editor_role,)),
                (get_opinion_validator, (get_opinion_editor_role,)),
                (LocalRoleAdapter.get_readers, ("Reader",)),
            ]
        ),
        "opinion_validation": OrderedDict(
            [
                (get_opinion_editor, ("Reader",)),
                (
                    get_opinion_validator,
                    (
                        "Reader",
                        "Contributor",
                    ),
                ),
                (LocalRoleAdapter.get_readers, ("Reader",)),
            ]
        ),
        "opinion_given": OrderedDict(
            [
                (get_editors, (get_editors_roles,)),
                (get_opinion_editor, ("Reader",)),
                (get_opinion_validator, ("Reader",)),
                (LocalRoleAdapter.get_readers, ("Reader",)),
            ]
        ),
    }
