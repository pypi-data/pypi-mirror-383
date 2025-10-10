# encoding: utf-8

from borg.localrole.interfaces import ILocalRoleProvider

from imio.schedule.config import DONE
from imio.schedule.config import STARTED
from imio.schedule.config import status_by_state
from imio.schedule.content.task import IAutomatedTask

from plone import api
from plone.memoize.request import cache

from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName

from Products.urban.content.licence.RoadDecree import RoadDecree
from Products.urban.interfaces import ICODT_IntegratedLicence
from Products.urban.interfaces import ICODT_UniqueLicence
from Products.urban.interfaces import IEnvironmentBase
from Products.urban.interfaces import IIntegratedLicence
from Products.urban.interfaces import IUniqueLicence

from zope.component import getAdapters
from zope.interface import implements


class GroupNotFoundError(Exception):
    """ """


class RoleNotFoundError(Exception):
    """ """


def _get_rolemap_caching_key(method, localrole_adapter, state):
    return (str(localrole_adapter.__class__), localrole_adapter.context.UID(), state)


class LocalRoleAdapter(object):
    """
    borg.localrole adapter to set localrole following type and state configuration.
    """

    implements(ILocalRoleProvider)

    mapping = {}

    def __init__(self, context):
        self.context = context
        self.licence = self.context

    def get_allowed_groups(self, licence):
        if (
            IUniqueLicence.providedBy(licence)
            or ICODT_UniqueLicence.providedBy(licence)
            or IIntegratedLicence.providedBy(licence)
            or ICODT_IntegratedLicence.providedBy(licence)
        ):
            return "urban_and_environment"
        elif IEnvironmentBase.providedBy(licence):
            return "environment_only"
        else:
            return "urban_only"

    def get_linked_opinion_editors(self):
        linked_opinion_editors = []
        if self.context.portal_type in RoadDecree.schema['bound_licence'].allowed_types:
            reference_catalog = getToolByName(self.context, REFERENCE_CATALOG)
            back_refs = reference_catalog.getBackReferences(self.context, 'bound_licence')
            if back_refs:
                back_obj = [ref.getSourceObject() for ref in back_refs][0]
                back_obj_local_role_adapters = [
                    adapter for name, adapter in getAdapters((back_obj,), ILocalRoleProvider)
                    if hasattr(adapter, 'get_opinion_editors')
                ]
                for back_obj_local_role_adapter in back_obj_local_role_adapters:
                    f = back_obj_local_role_adapter.get_opinion_editors()
                    linked_opinion_editors.extend(f)
        return linked_opinion_editors

    def get_opinion_editors(self):
        """
        Return groups who have external opinion to give on the licence.
        Thes groups should be to able to partially read the licence (
        'ExternalReader' role)
        """
        portal_urban = api.portal.get_tool("portal_urban")
        schedule_config = portal_urban.opinions_schedule

        exceptions = ["Voirie_editors", "Voirie_Validators"]
        opinion_editors = []
        all_opinion_request = self.context.getOpinionRequests()

        for opinion_request in all_opinion_request:
            task = None
            for task_config in schedule_config.get_all_task_configs():
                for obj in opinion_request.objectValues():
                    if (
                        IAutomatedTask.providedBy(obj)
                        and obj.task_config_UID == task_config.UID()
                    ):
                        task = obj
                        if task and status_by_state[api.content.get_state(task)] in [
                            STARTED,
                            DONE,
                        ]:
                            group = task.assigned_group
                            if group not in exceptions:
                                opinion_editors.append(group)

        back_ref_opinion_editors = self.get_linked_opinion_editors()
        opinion_editors.extend(back_ref_opinion_editors)

        return list(set(opinion_editors))

    def get_editors(self):
        """ """
        licence = self.licence
        mapping = {
            "urban_only": [
                "urban_editors",
            ],
            "environment_only": [
                "environment_editors",
            ],
            "urban_and_environment": [
                "urban_editors",
                "environment_editors",
            ],
        }
        allowed_group = self.get_allowed_groups(licence)
        if allowed_group in mapping:
            return mapping.get(allowed_group)

    def get_readers(self):
        """ """
        licence = self.licence
        mapping = {
            "urban_only": [
                "urban_readers",
            ],
            "environment_only": [
                "environment_readers",
            ],
            "urban_and_environment": [
                "urban_readers",
                "environment_readers",
            ],
        }
        allowed_group = self.get_allowed_groups(licence)
        if allowed_group in mapping:
            return mapping.get(allowed_group)

    def getRoles(self, principal):
        """
        Grant permission for principal.
        """
        current_state = self.get_state()
        state_config = self.get_roles_mapping_for_state(current_state)
        if not state_config:
            return []
        if not state_config.get(principal, []):
            return ()
        return tuple(state_config.get(principal))

    def getAllRoles(self):
        """
        Grant permissions.
        """
        current_state = self.get_state()
        state_config = self.get_roles_mapping_for_state(current_state)
        if not state_config:
            yield ("", ("",))
            raise StopIteration
        for principal, roles in state_config.items():
            yield (principal, tuple(roles))

    @cache(get_key=_get_rolemap_caching_key, get_request="self.context.REQUEST")
    def get_roles_mapping_for_state(self, state):
        """
        Return the group/roles mapping of a given state.
        """
        group_roles_mapping = self.mapping.get(state, {})
        generated_mapping = {}

        for group_name, role_names in group_roles_mapping.iteritems():
            groups = self.compute_group_value(group_name)

            roles = []
            for role in role_names:
                roles.extend(self.compute_role_value(role))
            roles = list(set(roles))

            for group in groups:
                generated_mapping[group] = roles

        return generated_mapping

    def compute_value(self, value):
        """
        Values in the mapping can be either the value to return or a method to
        call to dynamically compute the value.
        """
        if callable(value):
            computed_value = value(self)
        else:
            computed_value = [value]
        return computed_value

    def compute_group_value(self, group_name):
        group_values = self.compute_value(group_name) or []
        for group_value in group_values:
            if not api.group.get(group_value):
                if callable(group_name):
                    msg = "Group '{}' computed by '{}' method does not exist.".format(
                        group_value, group_name.__name__
                    )
                else:
                    msg = "'{}' is neither an existing group nor a method on mapping object {}.".format(
                        group_name,
                        self,
                    )
                raise GroupNotFoundError(msg)
        return group_values

    def compute_role_value(self, role_name):
        role_values = self.compute_value(role_name) or []

        portal = api.portal.getSite()
        portal_roles = portal.acl_users.portal_role_manager
        registered_roles = portal_roles.listRoleIds()
        for role_value in role_values:
            if role_value not in registered_roles:
                if callable(role_name):
                    msg = "Role '{}' computed by '{}' method does not exist.".format(
                        role_value, role_name.__func__.__name__
                    )
                else:
                    msg = "'{}' is neither an existing role nor a method on mapping object {}.".format(
                        role_name,
                        self,
                    )
                raise RoleNotFoundError(msg)
        return role_values

    def get_state(self):
        """Return the state of the current object"""
        try:
            return api.content.get_state(obj=self.context)
        except (WorkflowException, api.portal.CannotGetPortalError):
            return None
