# -*- coding: utf-8 -*-

from collective.documentgenerator import _
from collective.documentgenerator.content.pod_template import IConfigurablePODTemplate
from collective.documentgenerator.content.pod_template import ConfigurablePODTemplate

from plone.autoform import directives as form

from z3c.form.browser.select import SelectWidget

from zope import schema
from zope.interface import implements

import logging

logger = logging.getLogger("Products.urban: UrbanTemplate")


class IUrbanTemplate(IConfigurablePODTemplate):
    """
    UrbanTemplate dexterity schema.
    """

    form.widget("pod_portal_types", SelectWidget, multiple="multiple", size=15)
    pod_portal_types = schema.List(
        title=_(u"Allowed portal types"),
        description=_(
            u"Select for which content types the template will be available."
        ),
        value_type=schema.Choice(source="collective.documentgenerator.PortalTypes"),
        required=False,
        default=[
            "UrbanEvent",
            "UrbanEventInquiry",
            "UrbanEventOpinionRequest",
            "UrbanEventAnnouncement",
        ],
    )


class UrbanTemplate(ConfigurablePODTemplate):
    """
    UrbanTemplate dexterity class.
    """

    implements(IUrbanTemplate)
