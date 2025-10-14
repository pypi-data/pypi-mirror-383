# encoding: utf-8

from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFPlone import PloneMessageFactory as _

from Products.urban.interfaces import IGenericLicence

from plone import api


class ParcelRecordsView(BrowserView):
    """
    This manage the view of the popup showing the licences related to some parcels
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.parcel_id = self.request.get("id", None)
        self.capakeys = []
        if not self.parcel_id:
            plone_utils = api.portal.get_tool("plone_utils")
            plone_utils.addPortalMessage(_("Nothing to show !!!"), type="error")

    def get_related_licences_displays(self):
        """
        Returns the licences related to a parcel
        """
        licence_brains, self.capakeys, historic = self.search_licences()
        display = self.get_display(licence_brains)
        historic_display = self.get_historic_display(historic, licence_brains)
        return display, historic_display

    def get_display(self, licence_brains, short=False):
        context = aq_inner(self.context)
        related_items = []
        for brain in licence_brains:
            if brain.id != context.id:
                title = (short and brain.getReference) or (
                    len(brain.Title) < 40
                    and brain.Title
                    or "{}...".format(brain.Title[:40])
                )
                item_infos = {
                    "title": title,
                    "url": brain.getURL(),
                    "class": "state-{} contenttype-{}".format(
                        brain.review_state, brain.portal_type.lower()
                    ),
                }
                related_items.append(item_infos)
        return related_items

    def search_licences(self):
        """
        Do the search and return licence brains
        """
        context = aq_inner(self.context)
        catalog = api.portal.get_tool("portal_catalog")
        parcel = getattr(context, self.parcel_id)
        capakeys = [parcel.get_capakey()]
        historic = parcel.get_historic()
        capakeys.extend(historic.get_all_capakeys())

        related_brains = catalog(
            object_provides=IGenericLicence.__identifier__,
            parcelInfosIndex=capakeys,
            sort_on="sortable_title",
        )

        return related_brains, capakeys, historic

    def get_historic_display(self, parcels_historic, related_brains):
        table = parcels_historic.table_display()

        for line in table:
            for element in line:
                if not element.display():  # ignore blanks
                    continue
                parcel = element
                licence_brains = []
                for brain in related_brains:
                    if parcel.capakey in brain.parcelInfosIndex:
                        licence_brains.append(brain)
                licences = self.get_display(licence_brains, short=True)
                setattr(parcel, "licences", licences)
        return table

    def get_missing_capakey(self):
        interface = "Products.urban.interfaces.IMissingCapakey"
        registry = api.portal.get_registry_record(interface)
        if len(registry) == 0:
            return []
        missing_capakey = [capakey for capakey in self.capakeys if capakey in registry]
        return missing_capakey
